from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import httpx
import json
import os
import gzip
import zlib
import re
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

def get_course_ids(book_name: str) -> dict:
    """
    Get the correct author_id and collection_id for known courses
    
    Args:
        book_name: The book/course name
        
    Returns:
        Dict with author_id and collection_id
    """
    # Course mapping - add new courses here as needed
    course_mapping = {
        # System Design Interview course (working)
        "grokking_the_system_design_interview": {
            "author_id": "10370001",
            "collection_id": "4941429335392256"
        },
        "grokking-the-system-design-interview": {
            "author_id": "10370001", 
            "collection_id": "4941429335392256"
        },
        
        # Low Level Design Interview course - these are the correct IDs
        "grokking_the_low_level_design_interview_using_ood_principles": {
            "author_id": "10370001",  # Try same author first
            "collection_id": "6303669653422080"  # Different collection ID for low-level design
        },
        "grokking-the-low-level-design-interview": {
            "author_id": "10370001",
            "collection_id": "6303669653422080"
        },
        
        # Add more courses as needed
        "grokking_the_coding_interview": {
            "author_id": "10370001",
            "collection_id": "5761421253959680"
        }
    }
    
    # Get course IDs or use default fallback
    return course_mapping.get(book_name, {
        "author_id": "10370001",  # Default fallback
        "collection_id": "4941429335392256"  # Default fallback
    })

# Initialize FastAPI app
app = FastAPI(
    title="Educative Content Processor",
    description="A FastAPI application for converting Educative courses to LaTeX books with automatic image processing",
    version="2.0.0"
)

# Mount static files directory
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models for request/response
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    is_active: bool = True

class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    is_active: bool

# New models for book content generation
class GenerateBookContentRequest(BaseModel):
    educative_course_name: str
    token: Optional[str] = None
    cookie: Optional[str] = None
    use_env_credentials: bool = True  # Use environment variables by default
    content_type: str = "course"  # "course" or "interview-prep"

class GenerateBookContentResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error_message: Optional[str] = None
    source: Optional[str] = None  # To indicate whether env or provided credentials were used

# New models for LaTeX book generation
class GenerateLatexBookRequest(BaseModel):
    educative_course_name: str
    content_type: str = "course"  # "course" or "interview-prep"
    book_name: Optional[str] = None  # Custom name for the generated book
    token: Optional[str] = None
    cookie: Optional[str] = None
    use_env_credentials: bool = True

class LaTeXGenerationResponse(BaseModel):
    success: bool
    book_path: Optional[str] = None
    generated_files: Optional[List[str]] = None
    book_data: Optional[dict] = None  # Include the sanitized book data
    error_message: Optional[str] = None
    source: Optional[str] = None

# New models for Phase 3 - Section content generation
class GenerateSectionContentRequest(BaseModel):
    book_name: str  # Name of the generated book
    chapter_number: int  # Chapter number (1-based)
    educative_course_name: str  # Course name for content fetching
    content_type: str = "course"  # "course" or "interview-prep"
    token: Optional[str] = None
    cookie: Optional[str] = None
    use_env_credentials: bool = True

class SectionContentResponse(BaseModel):
    success: bool
    generated_sections: Optional[List[dict]] = None  # List of generated section details
    total_sections_generated: Optional[int] = None
    failed_sections: Optional[List[dict]] = None  # List of failed sections with errors
    chapter_info: Optional[dict] = None
    error_message: Optional[str] = None
    source: Optional[str] = None

class ClearChapterContentRequest(BaseModel):
    book_name: str  # Name of the generated book
    chapter_number: int  # Chapter number (1-based)

class ClearChapterContentResponse(BaseModel):
    success: bool
    message: str
    cleared_sections: Optional[List[str]] = None  # List of cleared section files
    cleared_directories: Optional[List[str]] = None  # List of cleared directories
    chapter_info: Optional[dict] = None
    error_message: Optional[str] = None

# New models for sanitized book content
class BookSection(BaseModel):
    title: str
    id: str
    slug: str
    author_id: Optional[str] = None
    collection_id: Optional[str] = None

class BookChapter(BaseModel):
    title: str
    summary: Optional[str] = None
    sections: List[BookSection]

class SanitizedBookResponse(BaseModel):
    success: bool
    book_title: Optional[str] = None
    book_summary: Optional[str] = None
    book_brief_summary: Optional[str] = None
    author_id: Optional[str] = None
    collection_id: Optional[str] = None
    chapters: Optional[List[BookChapter]] = None
    total_chapters: Optional[int] = None
    total_sections: Optional[int] = None
    error_message: Optional[str] = None
    source: Optional[str] = None

# In-memory storage (for demo purposes)
items_db = []
next_id = 1

def sanitize_educative_response(raw_data: dict, source: str) -> SanitizedBookResponse:
    """
    Sanitize and transform Educative API response into book-style format
    """
    try:
        # Extract basic book information
        instance = raw_data.get("instance", {})
        details = instance.get("details", {})
        
        book_title = details.get("title", "")
        book_summary = details.get("summary", "")
        book_brief_summary = details.get("brief_summary", "")
        
        # Extract author_id and collection_id from the response
        author_id = None
        collection_id = None
        
        # Extract table of contents first to look for author_id in pages
        toc = details.get("toc", {})
        categories = toc.get("categories", [])
        
        # Try to extract author_id from the first page in the first category
        for category in categories:
            if category.get("type") == "COLLECTION_CATEGORY":
                pages = category.get("pages", [])
                if pages:
                    first_page = pages[0]
                    if "author_id" in first_page:
                        author_id = str(first_page.get("author_id", ""))
                        if author_id and author_id != "None" and author_id != "":
                            break
                        else:
                            author_id = None
        
        # Fallback: Try to extract author_id from other possible locations if not found in pages
        if not author_id and "author" in details:
            author_data = details.get("author", {})
            if isinstance(author_data, dict):
                author_id = str(author_data.get("id", "")) or str(author_data.get("user_id", ""))
                # Only keep non-empty strings
                author_id = author_id if author_id and author_id != "None" and author_id != "" else None
            elif isinstance(author_data, (str, int)):
                # Convert to string and check if it's meaningful
                str_author = str(author_data)
                author_id = str_author if str_author and str_author != "None" and str_author != "" else None
        
        # Try to extract collection_id from instance or details
        if "id" in instance and instance.get("id"):
            collection_id = str(instance.get("id", ""))
        elif "collection_id" in details and details.get("collection_id"):
            collection_id = str(details.get("collection_id", ""))
        elif "id" in details and details.get("id"):
            collection_id = str(details.get("id", ""))
        
        # Extract table of contents and transform to chapters
        chapters = []
        total_sections = 0
        
        for category in categories:
            # Only include chapters with type "COLLECTION_CATEGORY"
            category_type = category.get("type", "")
            if category_type != "COLLECTION_CATEGORY":
                continue
                
            chapter_title = category.get("title", "Untitled Chapter")
            chapter_summary = category.get("summary", "")  # Extract chapter summary
            pages = category.get("pages", [])
            
            sections = []
            for page in pages:
                # Extract author_id and collection_id for each individual page
                page_author_id = page.get("author_id")
                if page_author_id:
                    page_author_id = str(page_author_id) if page_author_id and str(page_author_id) != "None" else None
                else:
                    page_author_id = author_id  # Use fallback author_id if page doesn't have one
                
                # Try multiple possible field names for page ID
                page_id = None
                for id_field in ["page_id", "id", "lesson_id", "content_id", "section_id"]:
                    if page.get(id_field):
                        page_id = str(page.get(id_field))
                        break
                
                # If still no ID found, generate a fallback ID based on slug or title
                if not page_id or page_id == "None" or page_id == "":
                    slug = page.get("slug", "")
                    if slug:
                        # Use a hash of the slug as a fallback ID
                        import hashlib
                        page_id = str(abs(hash(slug)) % (10**15))  # Generate a 15-digit ID
                    else:
                        # Last resort: use title hash
                        title = page.get("title", "untitled")
                        import hashlib
                        page_id = str(abs(hash(title)) % (10**15))
                
                section = BookSection(
                    title=page.get("title", "Untitled Section"),
                    id=page_id,
                    slug=page.get("slug", ""),
                    author_id=page_author_id,
                    collection_id=collection_id
                )
                sections.append(section)
                total_sections += 1
            
            chapter = BookChapter(
                title=chapter_title,
                summary=chapter_summary if chapter_summary else None,
                sections=sections
            )
            chapters.append(chapter)
        
        return SanitizedBookResponse(
            success=True,
            book_title=book_title,
            book_summary=book_summary,
            book_brief_summary=book_brief_summary,
            author_id=author_id,
            collection_id=collection_id,
            chapters=chapters,
            total_chapters=len(chapters),
            total_sections=total_sections,
            source=source
        )
        
    except Exception as e:
        return SanitizedBookResponse(
            success=False,
            error_message=f"Failed to sanitize response: {str(e)}",
            source=source
        )

# Root endpoint - Serve the main UI
@app.get("/")
async def read_root():
    """Serve the main web interface"""
    return FileResponse("static/index.html")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "educative-content-processor"}

# List generated books endpoint
@app.get("/api/books")
async def list_generated_books():
    """List all generated books from the generated_books directory"""
    try:
        generated_books_dir = Path("generated_books")
        if not generated_books_dir.exists():
            return {"books": []}
        
        books = []
        for book_dir in generated_books_dir.iterdir():
            if book_dir.is_dir():
                metadata_file = book_dir / "sections" / "section_metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        # Get creation time from directory
                        creation_time = datetime.fromtimestamp(book_dir.stat().st_ctime)
                        
                        books.append({
                            "id": book_dir.name,
                            "name": metadata.get("book_title", book_dir.name),
                            "course_name": book_dir.name.replace("_", "-"),
                            "created_at": creation_time.isoformat(),
                            "chapter_count": len(metadata.get("chapters", [])),
                            "status": "created",
                            "book_path": str(book_dir)
                        })
                    except json.JSONDecodeError:
                        continue
        
        return {"books": books}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing books: {str(e)}")

# Get book details endpoint
@app.get("/api/books/{book_id}")
async def get_book_details(book_id: str):
    """Get detailed information about a specific book"""
    try:
        book_dir = Path("generated_books") / book_id
        if not book_dir.exists():
            raise HTTPException(status_code=404, detail="Book not found")
        
        metadata_file = book_dir / "sections" / "section_metadata.json"
        if not metadata_file.exists():
            raise HTTPException(status_code=404, detail="Book metadata not found")
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Check content status for each section
        for chapter in metadata.get("chapters", []):
            for section in chapter.get("sections", []):
                section_file = book_dir / section["section_file"]
                if section_file.exists():
                    # Check if file has actual content (more than just basic structure)
                    content = section_file.read_text(encoding='utf-8')
                    if len(content) > 100:  # Basic check for actual content
                        section["content_status"] = "completed"
                    else:
                        section["content_status"] = "pending"
                else:
                    section["content_status"] = "pending"
        
        # Get creation time
        creation_time = datetime.fromtimestamp(book_dir.stat().st_ctime)
        
        return {
            "id": book_id,
            "name": metadata.get("book_title", book_id),
            "course_name": book_id.replace("_", "-"),
            "created_at": creation_time.isoformat(),
            "book_path": str(book_dir),
            "metadata": metadata,
            "chapters": metadata.get("chapters", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting book details: {str(e)}")

# Get all items
@app.get("/items", response_model=List[ItemResponse])
async def get_items():
    """Get all items"""
    return items_db

# Get item by ID
@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    """Get a specific item by ID"""
    for item in items_db:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

# Create new item
@app.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(item: Item):
    """Create a new item"""
    global next_id
    new_item = item.dict()
    new_item["id"] = next_id
    items_db.append(new_item)
    next_id += 1
    return new_item

# Update item
@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item: Item):
    """Update an existing item"""
    for i, existing_item in enumerate(items_db):
        if existing_item["id"] == item_id:
            updated_item = item.dict()
            updated_item["id"] = item_id
            items_db[i] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")

# Delete item
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """Delete an item"""
    for i, item in enumerate(items_db):
        if item["id"] == item_id:
            items_db.pop(i)
            return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

# Debug endpoint to test Educative API response
@app.post("/debug-educative-response")
async def debug_educative_response(request: GenerateBookContentRequest):
    """Debug endpoint to examine raw Educative API response"""
    try:
        # Construct the Educative API URL
        base_url = "https://www.educative.io/api/collection"
        url = f"{base_url}/{request.educative_course_name}?work_type=collection"
        
        # Determine which credentials to use
        if request.use_env_credentials:
            token = os.getenv("EDUCATIVE_TOKEN")
            cookie = os.getenv("EDUCATIVE_COOKIE")
        else:
            token = request.token
            cookie = request.cookie
        
        # Simple headers for debugging
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        if cookie:
            headers["Cookie"] = cookie
        
        # Make the request and return debug info
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, headers=headers)
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content_length": len(response.content),
                "encoding": response.encoding,
                "content_type": response.headers.get("content-type"),
                "first_100_bytes_hex": response.content[:100].hex() if response.content else None,
                "url": url,
                "has_cookie": bool(cookie),
                "has_token": bool(token)
            }
    except Exception as e:
        return {"error": str(e)}

# Generate book content from Educative course
@app.post("/generate-book-content", response_model=SanitizedBookResponse)
async def generate_book_content(request: GenerateBookContentRequest):
    """Generate sanitized book content by fetching data from Educative API"""
    try:
        # Construct the Educative API URL based on content type
        if request.content_type == "interview-prep":
            # For interview preparation content, use the interview-prep API
            base_url = "https://www.educative.io/api/interview-prep"
            url = f"{base_url}/{request.educative_course_name}?work_type=module"
        else:
            # For regular course content, use the collection API
            base_url = "https://www.educative.io/api/collection"
            url = f"{base_url}/{request.educative_course_name}?work_type=collection"
        
        # Determine which credentials to use
        if request.use_env_credentials:
            # Use environment variables
            token = os.getenv("EDUCATIVE_TOKEN")
            cookie = os.getenv("EDUCATIVE_COOKIE")
            credential_source = "environment"
        else:
            # Use provided credentials
            token = request.token
            cookie = request.cookie
            credential_source = "request"
        
        # Prepare headers to match what works in Postman (no compression request)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",  # Changed to match typical JSON requests
            "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
            # Removed Accept-Encoding to prevent compression
            "Connection": "keep-alive",
            "Sec-Ch-Ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=1, i",
            "X-Ed-Client": "v250728-rb-250730-0805",
        }
        
        # Set referer based on content type
        if request.content_type == "interview-prep":
            headers["Referer"] = f"https://www.educative.io/interview-prep/{request.educative_course_name}"
        else:
            headers["Referer"] = f"https://www.educative.io/courses/{request.educative_course_name}"
        
        # Add authentication headers
        if cookie:
            headers["Cookie"] = cookie
        
        # Add magicbox-auth token if available (extracted from cookie or provided separately)
        if token:
            # If token is provided separately, add it as a custom header
            headers["X-Educative-Token"] = token
        
        # Make the GET request to Educative API (don't explicitly request compression)
        async with httpx.AsyncClient(
            timeout=60.0, 
            follow_redirects=True
        ) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                # Check response details for debugging
                content_encoding = response.headers.get("content-encoding", "").lower()
                content_type = response.headers.get("content-type", "").lower()
                
                print(f"DEBUG: Content-Encoding: '{content_encoding}'")
                print(f"DEBUG: Content-Type: '{content_type}'")
                print(f"DEBUG: Response size: {len(response.content)} bytes")
                print(f"DEBUG: Response encoding: {response.encoding}")
                
                # Since Postman shows uncompressed JSON, try direct JSON parsing first
                try:
                    response_data = response.json()
                    print(f"DEBUG: Successfully parsed JSON response")
                    
                    # Sanitize and return the clean book data directly
                    return sanitize_educative_response(response_data, f"credentials_from_{credential_source}_direct_json")
                    
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    print(f"DEBUG: JSON parsing failed: {str(e)}")
                    return SanitizedBookResponse(
                        success=False,
                        error_message=f"Failed to parse Educative API response: {str(e)}",
                        source=f"credentials_from_{credential_source}"
                    )
            elif response.status_code == 401:
                return SanitizedBookResponse(
                    success=False,
                    error_message="Authentication failed. Please check your token/cookie credentials.",
                    source=f"credentials_from_{credential_source}"
                )
            elif response.status_code == 403:
                return SanitizedBookResponse(
                    success=False,
                    error_message="Access forbidden. You may not have permission to access this course.",
                    source=f"credentials_from_{credential_source}"
                )
            elif response.status_code == 404:
                return SanitizedBookResponse(
                    success=False,
                    error_message=f"Course '{request.educative_course_name}' not found. Please check the course name.",
                    source=f"credentials_from_{credential_source}"
                )
            else:
                # Handle other non-200 status codes
                try:
                    error_text = response.text[:500]
                except UnicodeDecodeError:
                    error_text = f"Binary response (length: {len(response.content)})"
                
                return SanitizedBookResponse(
                    success=False,
                    error_message=f"Failed to fetch data from Educative API. Status code: {response.status_code}, Response: {error_text}",
                    source=f"credentials_from_{credential_source}"
                )
                
    except httpx.TimeoutException:
        return SanitizedBookResponse(
            success=False,
            error_message="Request timeout while fetching data from Educative API (60s timeout)",
            source=f"credentials_from_{credential_source if 'credential_source' in locals() else 'unknown'}"
        )
    except httpx.RequestError as e:
        return SanitizedBookResponse(
            success=False,
            error_message=f"Network error while fetching data from Educative API: {str(e)}",
            source=f"credentials_from_{credential_source if 'credential_source' in locals() else 'unknown'}"
        )
    except UnicodeDecodeError as e:
        return SanitizedBookResponse(
            success=False,
            error_message=f"Encoding error while processing Educative API response: {str(e)}",
            source=f"credentials_from_{credential_source if 'credential_source' in locals() else 'unknown'}"
        )
    except json.JSONDecodeError as e:
        return SanitizedBookResponse(
            success=False,
            error_message=f"Invalid JSON response from Educative API: {str(e)}",
            source=f"credentials_from_{credential_source if 'credential_source' in locals() else 'unknown'}"
        )
    except Exception as e:
        return SanitizedBookResponse(
            success=False,
            error_message=f"Unexpected error: {str(e)}",
            source=f"credentials_from_{credential_source if 'credential_source' in locals() else 'unknown'}"
        )

# Generate LaTeX book from Educative course
@app.post("/generate-latex-book", response_model=LaTeXGenerationResponse)
async def generate_latex_book(request: GenerateLatexBookRequest):
    """Generate a complete LaTeX book from Educative course data"""
    try:
        # Import LaTeX generator
        from latex_generator import LaTeXBookGenerator
        
        # First, get the sanitized book data
        book_request = GenerateBookContentRequest(
            educative_course_name=request.educative_course_name,
            token=request.token,
            cookie=request.cookie,
            use_env_credentials=request.use_env_credentials
        )
        
        book_data = await generate_book_content(book_request)
        
        if not book_data.success:
            return LaTeXGenerationResponse(
                success=False,
                error_message=f"Failed to fetch book data: {book_data.error_message}",
                source=book_data.source
            )
        
        # Generate book name if not provided
        book_name = request.book_name or request.educative_course_name.replace('-', '_')
        
        # Initialize LaTeX generator
        latex_generator = LaTeXBookGenerator()
        
        # Generate and save the LaTeX book
        book_path = latex_generator.generate_and_save_book(book_data, book_name, request.content_type)
        
        # Get list of generated files
        book_path_obj = Path(book_path)
        generated_files = []
        if book_path_obj.exists():
            for file_path in book_path_obj.rglob('*'):
                if file_path.is_file():
                    generated_files.append(str(file_path.relative_to(book_path_obj)))
        
        return LaTeXGenerationResponse(
            success=True,
            book_path=book_path,
            generated_files=generated_files,
            book_data={
                "title": book_data.book_title,
                "summary": book_data.book_summary,
                "author_id": book_data.author_id,
                "collection_id": book_data.collection_id,
                "chapters": book_data.chapters or [],  # Return actual chapters array
                "chapter_count": len(book_data.chapters or []),
                "sections": book_data.total_sections
            },
            source=book_data.source
        )
        
    except ImportError:
        return LaTeXGenerationResponse(
            success=False,
            error_message="LaTeX generator module not available. Please ensure jinja2 is installed."
        )
    except Exception as e:
        return LaTeXGenerationResponse(
            success=False,
            error_message=f"Failed to generate LaTeX book: {str(e)}"
        )

@app.post("/generate-section-content", response_model=SectionContentResponse)
async def generate_section_content(request: GenerateSectionContentRequest):
    """
    Generate content for all sections within a specific chapter
    
    This endpoint fetches section content from Educative API and converts it to LaTeX.
    It requires that the book structure has been previously generated via /generate-latex-book.
    The endpoint will automatically discover and generate all sections for the specified chapter.
    """
    try:
        from section_processor import SectionContentProcessor
        from latex_generator import LaTeXBookGenerator
        import json
        
        # Validate that the book structure exists
        book_dir = Path("generated_books") / request.book_name
        sections_dir = book_dir / "sections"
        metadata_file = sections_dir / "section_metadata.json"
        
        if not metadata_file.exists():
            return SectionContentResponse(
                success=False,
                error_message="Book structure not found. Please call /generate-latex-book first to generate the book structure."
            )
        
        # Load section metadata
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Get content type from metadata, fallback to request if not available
        metadata_content_type = metadata.get("content_type", request.content_type)
        print(f"DEBUG: Content type from metadata: {metadata_content_type}, from request: {request.content_type}")
        
        # Use metadata content type if available, otherwise use request content type
        effective_content_type = metadata_content_type if metadata_content_type else request.content_type
        print(f"DEBUG: Using effective content type: {effective_content_type}")
        
        # Find the requested chapter and its sections
        target_chapter = None
        
        for chapter in metadata.get("chapters", []):
            if chapter.get("chapter_number") == request.chapter_number:
                target_chapter = chapter
                break
        
        if not target_chapter:
            return SectionContentResponse(
                success=False,
                error_message=f"Chapter {request.chapter_number} not found in book structure."
            )
        
        chapter_sections = target_chapter.get("sections", [])
        if not chapter_sections:
            return SectionContentResponse(
                success=False,
                error_message=f"No sections found for chapter {request.chapter_number}."
            )
        
        # Get authentication credentials
        if request.use_env_credentials:
            token = os.getenv("EDUCATIVE_TOKEN")
            cookie = os.getenv("EDUCATIVE_COOKIE")
        else:
            token = request.token
            cookie = request.cookie
        
        # First, try to get the book content to extract author_id and collection_id for each section
        # But if this fails, we'll use fallback values from metadata or defaults
        section_metadata_map = {}
        
        try:
            book_request = GenerateBookContentRequest(
                educative_course_name=request.educative_course_name,
                token=token,
                cookie=cookie,
                use_env_credentials=request.use_env_credentials,
                content_type=effective_content_type
            )
            
            book_data = await generate_book_content(book_request)
            
            if book_data.success and book_data.chapters:
                for chapter in book_data.chapters:
                    if chapter.sections:  # Check if sections exist
                        for section in chapter.sections:
                            section_metadata_map[section.id] = {
                                "author_id": section.author_id,
                                "collection_id": section.collection_id,
                                "title": section.title,
                                "slug": section.slug
                            }
            else:
                print(f"WARNING: Failed to fetch fresh book data: {book_data.error_message if hasattr(book_data, 'error_message') else 'Unknown error'}")
                print("INFO: Will use fallback author_id and collection_id values")
        
        except Exception as book_fetch_error:
            print(f"WARNING: Exception fetching book data: {str(book_fetch_error)}")
            print("INFO: Will use fallback author_id and collection_id values")
        
        # Initialize processors
        latex_generator = LaTeXBookGenerator()
        
        # Track generation results
        generated_sections = []
        failed_sections = []
        
        print(f"INFO: Starting generation of {len(chapter_sections)} sections for chapter {request.chapter_number}")
        
        # Process each section in the chapter
        for section_index, section_info in enumerate(chapter_sections):
            section_id = section_info.get("section_id", "")
            section_title = section_info.get("section_title", "")
            
            # Check if section_id is empty and skip or handle appropriately
            if not section_id or section_id.strip() == "":
                error_details = {
                    "section_id": section_id,
                    "section_title": section_title,
                    "error": f"Section ID is empty. This suggests the book structure was generated with incomplete data. Please regenerate the book structure using /generate-latex-book endpoint.",
                    "section_index": section_index + 1
                }
                failed_sections.append(error_details)
                print(f"ERROR: Section {section_index + 1} has empty ID: {section_title}")
                continue
            
            try:
                print(f"INFO: Processing section {section_index + 1}/{len(chapter_sections)}: {section_title} (ID: {section_id})")
                
                # Get section metadata from book data
                section_meta = section_metadata_map.get(section_id, {})
                
                # Get course-specific IDs or use fallbacks
                course_ids = get_course_ids(request.book_name)
                author_id = section_meta.get("author_id") or course_ids["author_id"]
                collection_id = section_meta.get("collection_id") or course_ids["collection_id"]
                
                # Initialize section processor with hierarchical context
                processor = SectionContentProcessor()
                processor.set_book_context(request.book_name, request.chapter_number, section_id)
                
                # Fetch section content from Educative API
                # Handle different API patterns based on content type
                if effective_content_type == "interview-prep":
                    # For interview-prep, use slug-based approach with smart course slug detection
                    section_slug = section_meta.get("slug") or section_info.get("section_slug", "")
                    
                    # Validate that we have a proper section slug for interview-prep
                    if not section_slug or section_slug.strip() == "":
                        print(f"WARNING: No section slug found for interview-prep content. Section ID: {section_id}")
                        print(f"         Available section_meta keys: {list(section_meta.keys()) if section_meta else 'None'}")
                        print(f"         Available section_info keys: {list(section_info.keys()) if section_info else 'None'}")
                        
                        # Try to use section_id as fallback, but this might not work
                        section_slug = section_id
                        print(f"         Using section_id as fallback slug: {section_slug}")
                    
                    # Smart course slug detection - try multiple course slug formats
                    course_slug_candidates = []
                    base_course_name = request.educative_course_name
                    
                    # Generate multiple course slug candidates
                    course_slug_candidates.append(base_course_name)  # Original name
                    
                    # Remove common prefixes and try variations
                    if base_course_name.startswith("grokking_the_"):
                        candidate = base_course_name.replace("grokking_the_", "")
                        course_slug_candidates.append(candidate)
                        course_slug_candidates.append(candidate.replace("_", "-"))
                    elif base_course_name.startswith("grokking-the-"):
                        candidate = base_course_name.replace("grokking-the-", "")
                        course_slug_candidates.append(candidate)
                        course_slug_candidates.append(candidate.replace("-", "_"))
                    
                    # Try hyphen vs underscore variations
                    if "_" in base_course_name:
                        course_slug_candidates.append(base_course_name.replace("_", "-"))
                    if "-" in base_course_name:
                        course_slug_candidates.append(base_course_name.replace("-", "_"))
                    
                    # Remove duplicates while preserving order
                    unique_candidates = []
                    for candidate in course_slug_candidates:
                        if candidate not in unique_candidates:
                            unique_candidates.append(candidate)
                    
                    print(f"DEBUG: Course slug candidates: {unique_candidates}")
                    print(f"DEBUG: Section slug: {section_slug}")
                    
                    # Try each course slug candidate with section slug combinations
                    section_data = None
                    successful_course_slug = None
                    successful_section_slug = None
                    all_attempts = []
                    
                    for course_slug in unique_candidates:
                        # For each course slug, try different section slug variations
                        section_slug_candidates = [section_slug]
                        
                        # Add section_id as alternative
                        if section_slug != section_id:
                            section_slug_candidates.append(section_id)
                        
                        # Try title-based slug if available
                        if section_info and "section_title" in section_info:
                            title_slug = section_info["section_title"].lower()
                            title_slug = title_slug.replace(" ", "-").replace("(", "").replace(")", "")
                            title_slug = re.sub(r'[^a-z0-9\-]', '', title_slug)
                            if title_slug not in section_slug_candidates:
                                section_slug_candidates.append(title_slug)
                        
                        for current_section_slug in section_slug_candidates:
                            try:
                                attempt = f"{course_slug}/{current_section_slug}"
                                all_attempts.append(attempt)
                                
                                print(f"TRYING: course_slug='{course_slug}', section_slug='{current_section_slug}'")
                                section_data = await processor.fetch_section_content(
                                    content_type="interview-prep",
                                    course_slug=course_slug,
                                    section_slug=current_section_slug,
                                    token=token,
                                    cookie=cookie
                                )
                                print(f"SUCCESS: Found content with course_slug='{course_slug}', section_slug='{current_section_slug}'")
                                successful_course_slug = course_slug
                                successful_section_slug = current_section_slug
                                break
                            except Exception as e:
                                print(f"FAILED: course_slug='{course_slug}', section_slug='{current_section_slug}' - {str(e)}")
                                continue
                        
                        if section_data:
                            break
                    
                    # If all attempts failed, report comprehensive error
                    if not section_data:
                        print(f"ERROR: All course/section slug combinations failed for section '{section_info.get('section_title', section_id)}'")
                        print(f"       Tried {len(all_attempts)} combinations: {all_attempts}")
                        raise Exception(f"No valid course/section slug combination found. Tried: {all_attempts}")
                
                else:
                    # For course content, use the traditional ID-based approach
                    page_id = section_meta.get("page_id") or section_id
                    author_id = section_meta.get("author_id") or course_ids["author_id"]
                    collection_id = section_meta.get("collection_id") or course_ids["collection_id"]
                    
                    print(f"DEBUG: Course API call - author_id: {author_id}, collection_id: {collection_id}, page_id: {page_id}")
                    
                    section_data = await processor.fetch_section_content(
                        content_type="course",
                        author_id=author_id,
                        collection_id=collection_id,
                        page_id=page_id,
                        token=token,
                        cookie=cookie
                    )
                
                # Process components and convert to LaTeX using async method
                latex_content, generated_images, component_types = await processor.process_section_components_async(section_data)
                
                # Get section title from the response or fallback
                final_section_title = section_data.get("summary", {}).get("title", section_title)
                
                # Create a proper section object for template rendering
                section_obj = BookSection(
                    id=section_id,
                    title=final_section_title,
                    slug=section_info.get("section_slug", ""),
                    author_id=course_ids["author_id"],
                    collection_id=course_ids["collection_id"]
                )
                
                # Generate complete section content using template
                final_latex = latex_generator.generate_section_content(
                    chapter_slug=target_chapter.get("chapter_slug", ""),
                    section=section_obj,
                    content=latex_content
                )
                
                # Save section file in hierarchical structure: files/chapter_X/section_Y.tex
                chapter_slug = target_chapter.get("chapter_slug", "")
                chapter_dir_name = f"chapter_{request.chapter_number}_{chapter_slug}"
                section_filename = f"section_{section_id}.tex"
                
                # Create chapter directory under files/
                chapter_section_dir = book_dir / "files" / chapter_dir_name
                chapter_section_dir.mkdir(parents=True, exist_ok=True)
                
                section_file_path = chapter_section_dir / section_filename
                
                # Write section content to file
                with open(section_file_path, 'w', encoding='utf-8') as f:
                    f.write(final_latex)
                
                # Update metadata to mark section as generated
                section_info["content_status"] = "generated"
                section_info["generated_timestamp"] = datetime.now().isoformat()
                section_info["component_types"] = component_types
                
                # Add to successful generations
                generated_sections.append({
                    "section_id": section_id,
                    "section_title": final_section_title,
                    "section_file_path": str(section_file_path.relative_to(book_dir)),
                    "author_id": author_id,
                    "collection_id": collection_id,
                    "generated_images": generated_images,
                    "component_types": component_types,
                    "latex_content_length": len(final_latex)
                })
                
                print(f"SUCCESS: Generated section {section_index + 1}: {final_section_title}")
                
            except Exception as section_error:
                error_details = {
                    "section_id": section_id,
                    "section_title": section_title,
                    "error": str(section_error),
                    "section_index": section_index + 1
                }
                failed_sections.append(error_details)
                print(f"ERROR: Failed to generate section {section_index + 1}: {section_title} - {str(section_error)}")
        
        # Save updated metadata
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        # Determine overall success
        total_sections = len(chapter_sections)
        successful_count = len(generated_sections)
        failed_count = len(failed_sections)
        
        overall_success = successful_count > 0  # Success if at least one section was generated
        
        return SectionContentResponse(
            success=overall_success,
            generated_sections=generated_sections,
            total_sections_generated=successful_count,
            failed_sections=failed_sections if failed_sections else None,
            chapter_info={
                "chapter_number": request.chapter_number,
                "chapter_title": target_chapter.get("chapter_title", ""),
                "chapter_slug": target_chapter.get("chapter_slug", ""),
                "total_sections": total_sections,
                "successful_sections": successful_count,
                "failed_sections": failed_count
            },
            source=f"chapter_{request.chapter_number}_batch_generation"
        )
        
    except ImportError:
        return SectionContentResponse(
            success=False,
            error_message="Section processor module not available. Please ensure required dependencies are installed."
        )
    except Exception as e:
        return SectionContentResponse(
            success=False,
            error_message=f"Failed to generate chapter content: {str(e)}",
            source=str(e)
        )

@app.post("/clear-chapter-content", response_model=ClearChapterContentResponse)
async def clear_chapter_content(request: ClearChapterContentRequest):
    """
    Clear all generated content for a specific chapter, allowing for fresh regeneration.
    
    This endpoint will:
    1. Remove all section content files for the specified chapter
    2. Update the metadata to mark sections as pending
    3. Allow the chapter to be regenerated from scratch
    """
    try:
        print(f"\n=== CLEARING CHAPTER {request.chapter_number} CONTENT ===")
        print(f"Book: {request.book_name}")
        
        # Construct paths
        book_dir = Path("generated_books") / request.book_name
        metadata_file = book_dir / "sections" / "section_metadata.json"
        
        if not book_dir.exists():
            return ClearChapterContentResponse(
                success=False,
                message=f"Book directory not found: {request.book_name}",
                error_message="Book not found"
            )
        
        if not metadata_file.exists():
            return ClearChapterContentResponse(
                success=False,
                message=f"Metadata file not found for book: {request.book_name}",
                error_message="Metadata not found"
            )
        
        # Load metadata
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Find the target chapter
        chapters = metadata.get("chapters", [])
        if request.chapter_number < 1 or request.chapter_number > len(chapters):
            return ClearChapterContentResponse(
                success=False,
                message=f"Invalid chapter number: {request.chapter_number}. Book has {len(chapters)} chapters.",
                error_message="Invalid chapter number"
            )
        
        target_chapter = chapters[request.chapter_number - 1]
        chapter_sections = target_chapter.get("sections", [])
        
        cleared_files = []
        cleared_directories = []
        
        # Clear each section file and update status
        for section_index, section in enumerate(chapter_sections):
            section_file_name = section.get("section_file", "")
            if section_file_name:
                section_file_path = book_dir / section_file_name
                
                # Remove the section file if it exists
                if section_file_path.exists():
                    try:
                        section_file_path.unlink()  # Delete the file
                        cleared_files.append(section_file_name)
                        print(f"Deleted section file: {section_file_name}")
                    except Exception as e:
                        print(f"Warning: Could not delete {section_file_name}: {str(e)}")
                
                # Update section status to pending
                section["content_status"] = "pending"
        
        # Clear chapter images directory
        chapter_images_dir = book_dir / "Images" / f"chapter_{request.chapter_number}"
        if chapter_images_dir.exists():
            try:
                import shutil
                shutil.rmtree(chapter_images_dir)
                cleared_directories.append(f"Images/chapter_{request.chapter_number}")
                print(f"Deleted images directory: Images/chapter_{request.chapter_number}")
            except Exception as e:
                print(f"Warning: Could not delete images directory: {str(e)}")
        
        # Clear chapter files directory
        chapter_files_dir = book_dir / "files" / target_chapter.get("chapter_slug", f"chapter_{request.chapter_number}")
        if chapter_files_dir.exists():
            try:
                import shutil
                shutil.rmtree(chapter_files_dir)
                cleared_directories.append(f"files/{target_chapter.get('chapter_slug', f'chapter_{request.chapter_number}')}")
                print(f"Deleted chapter files directory: {chapter_files_dir.name}")
            except Exception as e:
                print(f"Warning: Could not delete chapter files directory: {str(e)}")
        
        # Also try to remove by chapter file name pattern (alternative naming)
        chapter_file_name = target_chapter.get("chapter_file", "")
        if chapter_file_name:
            # Extract directory name from chapter file path
            chapter_file_path = Path(chapter_file_name)
            if len(chapter_file_path.parts) > 1:
                chapter_dir_name = chapter_file_path.parts[-2]  # Get parent directory name
                alt_chapter_files_dir = book_dir / "files" / chapter_dir_name
                if alt_chapter_files_dir.exists() and alt_chapter_files_dir != chapter_files_dir:
                    try:
                        import shutil
                        shutil.rmtree(alt_chapter_files_dir)
                        cleared_directories.append(f"files/{chapter_dir_name}")
                        print(f"Deleted alternative chapter files directory: {chapter_dir_name}")
                    except Exception as e:
                        print(f"Warning: Could not delete alternative chapter files directory: {str(e)}")
        
        # Save updated metadata
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        chapter_title = target_chapter.get("chapter_title", f"Chapter {request.chapter_number}")
        
        print(f"SUCCESS: Cleared {len(cleared_files)} section files and {len(cleared_directories)} directories for chapter {request.chapter_number}")
        
        return ClearChapterContentResponse(
            success=True,
            message=f"Successfully cleared content for '{chapter_title}'. {len(cleared_files)} section files and {len(cleared_directories)} directories removed.",
            cleared_sections=cleared_files,
            cleared_directories=cleared_directories,
            chapter_info={
                "chapter_number": request.chapter_number,
                "chapter_title": chapter_title,
                "total_sections": len(chapter_sections),
                "cleared_sections": len(cleared_files),
                "cleared_directories": len(cleared_directories)
            }
        )
        
    except Exception as e:
        print(f"ERROR: Failed to clear chapter content: {str(e)}")
        return ClearChapterContentResponse(
            success=False,
            message=f"Failed to clear chapter content: {str(e)}",
            error_message=str(e)
        )

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
