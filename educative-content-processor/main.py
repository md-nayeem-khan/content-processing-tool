from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import httpx
import json
import os
import gzip
import zlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Content Processing API",
    description="A FastAPI application for content processing",
    version="1.0.0"
)

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

class GenerateBookContentResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error_message: Optional[str] = None
    source: Optional[str] = None  # To indicate whether env or provided credentials were used

# New models for sanitized book content
class BookSection(BaseModel):
    title: str
    id: str
    slug: str

class BookChapter(BaseModel):
    title: str
    summary: Optional[str] = None
    sections: List[BookSection]

class SanitizedBookResponse(BaseModel):
    success: bool
    book_title: Optional[str] = None
    book_summary: Optional[str] = None
    book_brief_summary: Optional[str] = None
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
        
        # Extract table of contents and transform to chapters
        toc = details.get("toc", {})
        categories = toc.get("categories", [])
        
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
                section = BookSection(
                    title=page.get("title", "Untitled Section"),
                    id=str(page.get("page_id", "")),
                    slug=page.get("slug", "")
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

# Root endpoint
@app.get("/")
async def read_root():
    """Welcome endpoint"""
    return {"message": "Welcome to Content Processing API", "docs": "/docs"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "content-processing-api"}

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
        # Construct the Educative API URL
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
            "Referer": f"https://www.educative.io/courses/{request.educative_course_name}",
        }
        
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

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
