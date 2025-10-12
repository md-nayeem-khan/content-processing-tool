from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import json
import os
from datetime import datetime
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(
    title="Markdown Content Processor",
    description="A fully offline FastAPI application for converting markdown content to LaTeX books",
    version="1.0.0"
)

# Mount static files directory
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models for request/response
class CreateBookRequest(BaseModel):
    book_name: str
    description: Optional[str] = None

class CreateBookResponse(BaseModel):
    success: bool
    book_id: str
    message: str
    error_message: Optional[str] = None

class BookSection(BaseModel):
    title: str
    id: str
    slug: str
    content_file: Optional[str] = None
    content_status: str = "pending"  # pending, completed
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class BookChapter(BaseModel):
    title: str
    summary: Optional[str] = None
    sections: List[BookSection] = []
    chapter_number: Optional[int] = None
    created_at: Optional[str] = None

class CreateChapterRequest(BaseModel):
    book_id: str
    chapter_title: str
    chapter_summary: Optional[str] = None

class CreateChapterResponse(BaseModel):
    success: bool
    message: str
    chapter_index: Optional[int] = None
    error_message: Optional[str] = None

class UpdateChapterRequest(BaseModel):
    book_id: str
    chapter_index: int
    chapter_title: Optional[str] = None
    chapter_summary: Optional[str] = None

class UpdateChapterResponse(BaseModel):
    success: bool
    message: str
    error_message: Optional[str] = None

class DeleteChapterRequest(BaseModel):
    book_id: str
    chapter_index: int

class DeleteChapterResponse(BaseModel):
    success: bool
    message: str
    error_message: Optional[str] = None

class CreateSectionRequest(BaseModel):
    book_id: str
    chapter_index: int
    section_title: str

class CreateSectionResponse(BaseModel):
    success: bool
    message: str
    section_id: Optional[str] = None
    error_message: Optional[str] = None

class UpdateSectionContentRequest(BaseModel):
    book_id: str
    chapter_index: int
    section_id: str
    markdown_content: str

class UpdateSectionContentResponse(BaseModel):
    success: bool
    message: str
    error_message: Optional[str] = None

class DeleteSectionRequest(BaseModel):
    book_id: str
    chapter_index: int
    section_id: str

class DeleteSectionResponse(BaseModel):
    success: bool
    message: str
    error_message: Optional[str] = None

class GenerateLatexBookRequest(BaseModel):
    book_id: str

class LaTeXGenerationResponse(BaseModel):
    success: bool
    book_path: Optional[str] = None
    generated_files: Optional[List[str]] = None
    error_message: Optional[str] = None

# Helper functions
def get_books_db_path() -> Path:
    """Get the path to the books database file"""
    db_dir = Path("generated_books")
    db_dir.mkdir(exist_ok=True)
    return db_dir / "books_db.json"

def load_books_db() -> dict:
    """Load books database from JSON file"""
    db_path = get_books_db_path()
    if db_path.exists():
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"books": []}

def save_books_db(db: dict):
    """Save books database to JSON file"""
    db_path = get_books_db_path()
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def slugify(text: str) -> str:
    """Convert text to a valid slug"""
    import re
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '_', slug)
    return slug.strip('_')

def create_book_directory(book_id: str):
    """Create directory structure for a book"""
    book_dir = Path("generated_books") / book_id
    book_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (book_dir / "sections").mkdir(exist_ok=True)
    (book_dir / "Images").mkdir(exist_ok=True)
    (book_dir / "files").mkdir(exist_ok=True)
    
    return book_dir

# API Endpoints

# Root endpoint - Serve the main UI
@app.get("/")
async def read_root():
    """Serve the main web interface"""
    return FileResponse("static/index.html")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "markdown-content-processor"}

# List all books
@app.get("/api/books")
async def list_books():
    """List all books"""
    try:
        db = load_books_db()
        books = db.get("books", [])
        
        # Add chapter count to each book
        for book in books:
            book["chapter_count"] = len(book.get("chapters", []))
        
        return {"books": books}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing books: {str(e)}")

# Get book details
@app.get("/api/books/{book_id}")
async def get_book_details(book_id: str):
    """Get detailed information about a specific book"""
    try:
        db = load_books_db()
        books = db.get("books", [])
        
        book = next((b for b in books if b["id"] == book_id), None)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        return book
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting book details: {str(e)}")

# Create a new book
@app.post("/api/books", response_model=CreateBookResponse)
async def create_book(request: CreateBookRequest):
    """Create a new book"""
    try:
        db = load_books_db()
        
        # Generate book ID from name
        book_id = slugify(request.book_name)
        
        # Check if book already exists
        existing_book = next((b for b in db.get("books", []) if b["id"] == book_id), None)
        if existing_book:
            return CreateBookResponse(
                success=False,
                book_id=book_id,
                message="Book already exists",
                error_message="A book with this name already exists"
            )
        
        # Create book directory structure
        create_book_directory(book_id)
        
        # Create book entry
        new_book = {
            "id": book_id,
            "name": request.book_name,
            "description": request.description or "",
            "created_at": datetime.now().isoformat(),
            "status": "created",
            "chapters": []
        }
        
        # Add to database
        if "books" not in db:
            db["books"] = []
        db["books"].append(new_book)
        save_books_db(db)
        
        # Generate initial Main.tex file immediately
        try:
            from latex_generator import LaTeXBookGenerator
            generator = LaTeXBookGenerator()
            generator.generate_book(new_book, book_id)
        except Exception as latex_error:
            print(f"Warning: Failed to generate initial LaTeX files: {latex_error}")
            # Don't fail the book creation if LaTeX generation fails
        
        return CreateBookResponse(
            success=True,
            book_id=book_id,
            message="Book created successfully"
        )
        
    except Exception as e:
        return CreateBookResponse(
            success=False,
            book_id="",
            message="Failed to create book",
            error_message=str(e)
        )

# Create a new chapter
@app.post("/api/chapters", response_model=CreateChapterResponse)
async def create_chapter(request: CreateChapterRequest):
    """Create a new chapter in a book"""
    try:
        db = load_books_db()
        books = db.get("books", [])
        
        # Find the book
        book = next((b for b in books if b["id"] == request.book_id), None)
        if not book:
            return CreateChapterResponse(
                success=False,
                message="Book not found",
                error_message="The specified book does not exist"
            )
        
        # Create new chapter
        chapter_index = len(book.get("chapters", []))
        new_chapter = {
            "title": request.chapter_title,
            "summary": request.chapter_summary or "",
            "sections": [],
            "chapter_number": chapter_index + 1,
            "created_at": datetime.now().isoformat()
        }
        
        # Add chapter to book
        if "chapters" not in book:
            book["chapters"] = []
        book["chapters"].append(new_chapter)
        
        # Save database
        save_books_db(db)
        
        # Regenerate Main.tex to include the new chapter
        try:
            from latex_generator import LaTeXBookGenerator
            generator = LaTeXBookGenerator()
            generator.generate_book(book, request.book_id)
        except Exception as latex_error:
            print(f"Warning: Failed to regenerate LaTeX files: {latex_error}")
        
        return CreateChapterResponse(
            success=True,
            message="Chapter created successfully",
            chapter_index=chapter_index
        )
        
    except Exception as e:
        return CreateChapterResponse(
            success=False,
            message="Failed to create chapter",
            error_message=str(e)
        )

# Update chapter metadata
@app.post("/api/chapters/update", response_model=UpdateChapterResponse)
async def update_chapter(request: UpdateChapterRequest):
    """Update chapter title and summary"""
    try:
        db = load_books_db()
        books = db.get("books", [])
        
        # Find the book
        book = next((b for b in books if b["id"] == request.book_id), None)
        if not book:
            return UpdateChapterResponse(
                success=False,
                message="Book not found",
                error_message="The specified book does not exist"
            )
        
        # Validate chapter index
        chapters = book.get("chapters", [])
        if request.chapter_index < 0 or request.chapter_index >= len(chapters):
            return UpdateChapterResponse(
                success=False,
                message="Invalid chapter index",
                error_message="The specified chapter does not exist"
            )
        
        # Update chapter metadata
        if request.chapter_title:
            chapters[request.chapter_index]["title"] = request.chapter_title
        if request.chapter_summary is not None:
            chapters[request.chapter_index]["summary"] = request.chapter_summary
        chapters[request.chapter_index]["updated_at"] = datetime.now().isoformat()
        
        # Save database
        save_books_db(db)
        
        # Regenerate LaTeX with updated chapter info
        try:
            from latex_generator import LaTeXBookGenerator
            generator = LaTeXBookGenerator()
            generator.generate_book(book, request.book_id)
        except Exception as latex_error:
            print(f"Warning: Failed to regenerate LaTeX files: {latex_error}")
        
        return UpdateChapterResponse(
            success=True,
            message="Chapter updated successfully"
        )
        
    except Exception as e:
        return UpdateChapterResponse(
            success=False,
            message="Failed to update chapter",
            error_message=str(e)
        )

# Delete a chapter
@app.post("/api/chapters/delete", response_model=DeleteChapterResponse)
async def delete_chapter(request: DeleteChapterRequest):
    """Delete a chapter from a book"""
    try:
        db = load_books_db()
        books = db.get("books", [])
        
        # Find the book
        book = next((b for b in books if b["id"] == request.book_id), None)
        if not book:
            return DeleteChapterResponse(
                success=False,
                message="Book not found",
                error_message="The specified book does not exist"
            )
        
        # Validate chapter index
        chapters = book.get("chapters", [])
        if request.chapter_index < 0 or request.chapter_index >= len(chapters):
            return DeleteChapterResponse(
                success=False,
                message="Invalid chapter index",
                error_message="The specified chapter does not exist"
            )
        
        # Delete chapter content file if exists
        chapter = chapters[request.chapter_index]
        if "content_file" in chapter:
            content_file = Path("generated_books") / request.book_id / chapter["content_file"]
            if content_file.exists():
                content_file.unlink()
        
        # Remove chapter from list
        chapters.pop(request.chapter_index)
        
        # Renumber remaining chapters
        for i, ch in enumerate(chapters):
            ch["chapter_number"] = i + 1
        
        # Save database
        save_books_db(db)
        
        # Regenerate Main.tex to reflect deleted chapter
        try:
            from latex_generator import LaTeXBookGenerator
            generator = LaTeXBookGenerator()
            generator.generate_book(book, request.book_id)
        except Exception as latex_error:
            print(f"Warning: Failed to regenerate LaTeX files: {latex_error}")
        
        return DeleteChapterResponse(
            success=True,
            message="Chapter deleted successfully"
        )
        
    except Exception as e:
        return DeleteChapterResponse(
            success=False,
            message="Failed to delete chapter",
            error_message=str(e)
        )

# Create a new section under a chapter
@app.post("/api/sections", response_model=CreateSectionResponse)
async def create_section(request: CreateSectionRequest):
    """Create a new section under a chapter"""
    try:
        db = load_books_db()
        books = db.get("books", [])
        
        # Find the book
        book = next((b for b in books if b["id"] == request.book_id), None)
        if not book:
            return CreateSectionResponse(
                success=False,
                message="Book not found",
                error_message="The specified book does not exist"
            )
        
        # Validate chapter index
        chapters = book.get("chapters", [])
        if request.chapter_index < 0 or request.chapter_index >= len(chapters):
            return CreateSectionResponse(
                success=False,
                message="Invalid chapter index",
                error_message="The specified chapter does not exist"
            )
        
        # Generate section ID (numeric like educative) and slug
        import random
        section_id = str(random.randint(1000000000000000, 9999999999999999))  # 16-digit ID
        section_slug = slugify(request.section_title)
        
        # Create new section
        new_section = {
            "title": request.section_title,
            "id": section_id,
            "slug": section_slug,
            "content_status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        # Add section to chapter
        if "sections" not in chapters[request.chapter_index]:
            chapters[request.chapter_index]["sections"] = []
        chapters[request.chapter_index]["sections"].append(new_section)
        
        # Save database
        save_books_db(db)
        
        # Regenerate LaTeX to include the new section
        try:
            from latex_generator import LaTeXBookGenerator
            generator = LaTeXBookGenerator()
            generator.generate_book(book, request.book_id)
        except Exception as latex_error:
            print(f"Warning: Failed to regenerate LaTeX files: {latex_error}")
        
        return CreateSectionResponse(
            success=True,
            message="Section created successfully",
            section_id=section_id
        )
        
    except Exception as e:
        return CreateSectionResponse(
            success=False,
            message="Failed to create section",
            error_message=str(e)
        )

# Update section content
@app.post("/api/sections/content", response_model=UpdateSectionContentResponse)
async def update_section_content(request: UpdateSectionContentRequest):
    """Update the markdown content of a section"""
    try:
        db = load_books_db()
        books = db.get("books", [])
        
        # Find the book
        book = next((b for b in books if b["id"] == request.book_id), None)
        if not book:
            return UpdateSectionContentResponse(
                success=False,
                message="Book not found",
                error_message="The specified book does not exist"
            )
        
        # Validate chapter index
        chapters = book.get("chapters", [])
        if request.chapter_index < 0 or request.chapter_index >= len(chapters):
            return UpdateSectionContentResponse(
                success=False,
                message="Invalid chapter index",
                error_message="The specified chapter does not exist"
            )
        
        # Find the section
        sections = chapters[request.chapter_index].get("sections", [])
        section = next((s for s in sections if s["id"] == request.section_id), None)
        if not section:
            return UpdateSectionContentResponse(
                success=False,
                message="Section not found",
                error_message="The specified section does not exist"
            )
        
        # Save markdown content to file
        book_dir = Path("generated_books") / request.book_id / "sections"
        book_dir.mkdir(parents=True, exist_ok=True)
        
        chapter_num = request.chapter_index + 1
        section_file = book_dir / f"chapter_{chapter_num}_section_{section['slug']}.md"
        with open(section_file, 'w', encoding='utf-8') as f:
            f.write(request.markdown_content)
        
        # Update section metadata
        section["content_file"] = str(section_file.relative_to(Path("generated_books") / request.book_id))
        section["content_status"] = "completed"
        section["updated_at"] = datetime.now().isoformat()
        
        # Save database
        save_books_db(db)
        
        # Regenerate LaTeX with updated section content
        try:
            from latex_generator import LaTeXBookGenerator
            generator = LaTeXBookGenerator()
            generator.generate_book(book, request.book_id)
        except Exception as latex_error:
            print(f"Warning: Failed to regenerate LaTeX files: {latex_error}")
        
        return UpdateSectionContentResponse(
            success=True,
            message="Section content updated successfully"
        )
        
    except Exception as e:
        return UpdateSectionContentResponse(
            success=False,
            message="Failed to update section content",
            error_message=str(e)
        )

# Delete a section
@app.post("/api/sections/delete", response_model=DeleteSectionResponse)
async def delete_section(request: DeleteSectionRequest):
    """Delete a section from a chapter"""
    try:
        db = load_books_db()
        books = db.get("books", [])
        
        # Find the book
        book = next((b for b in books if b["id"] == request.book_id), None)
        if not book:
            return DeleteSectionResponse(
                success=False,
                message="Book not found",
                error_message="The specified book does not exist"
            )
        
        # Validate chapter index
        chapters = book.get("chapters", [])
        if request.chapter_index < 0 or request.chapter_index >= len(chapters):
            return DeleteSectionResponse(
                success=False,
                message="Invalid chapter index",
                error_message="The specified chapter does not exist"
            )
        
        # Find and remove the section
        sections = chapters[request.chapter_index].get("sections", [])
        section_index = next((i for i, s in enumerate(sections) if s["id"] == request.section_id), None)
        
        if section_index is None:
            return DeleteSectionResponse(
                success=False,
                message="Section not found",
                error_message="The specified section does not exist"
            )
        
        # Delete section content file if exists
        section = sections[section_index]
        if "content_file" in section:
            content_file = Path("generated_books") / request.book_id / section["content_file"]
            if content_file.exists():
                content_file.unlink()
        
        # Remove section from list
        sections.pop(section_index)
        
        # Save database
        save_books_db(db)
        
        # Regenerate LaTeX to reflect deleted section
        try:
            from latex_generator import LaTeXBookGenerator
            generator = LaTeXBookGenerator()
            generator.generate_book(book, request.book_id)
        except Exception as latex_error:
            print(f"Warning: Failed to regenerate LaTeX files: {latex_error}")
        
        return DeleteSectionResponse(
            success=True,
            message="Section deleted successfully"
        )
        
    except Exception as e:
        return DeleteSectionResponse(
            success=False,
            message="Failed to delete section",
            error_message=str(e)
        )

# Generate LaTeX book
@app.post("/api/generate-latex", response_model=LaTeXGenerationResponse)
async def generate_latex_book(request: GenerateLatexBookRequest):
    """Generate LaTeX book from markdown content"""
    try:
        from latex_generator import LaTeXBookGenerator
        
        db = load_books_db()
        books = db.get("books", [])
        
        # Find the book
        book = next((b for b in books if b["id"] == request.book_id), None)
        if not book:
            return LaTeXGenerationResponse(
                success=False,
                error_message="Book not found"
            )
        
        # Generate LaTeX book
        generator = LaTeXBookGenerator()
        result = generator.generate_book(book, request.book_id)
        
        return LaTeXGenerationResponse(
            success=result.get('success', True),
            book_path=result.get('book_path'),
            generated_files=result.get('generated_files', [])
        )
        
    except Exception as e:
        return LaTeXGenerationResponse(
            success=False,
            error_message=f"Failed to generate LaTeX: {str(e)}"
        )

# Run the application
if __name__ == "__main__":
    # Ensure required directories exist
    Path("generated_books").mkdir(exist_ok=True)
    Path("static").mkdir(exist_ok=True)
    
    print("=" * 60)
    print("🚀 Starting Markdown Content Processor")
    print("=" * 60)
    print(f"📍 Server: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print(f"🔍 Health: http://localhost:8000/health")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
