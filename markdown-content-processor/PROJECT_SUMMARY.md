# Markdown Content Processor - Project Summary

## Overview
A fully offline content processing tool that converts raw markdown content into beautifully formatted LaTeX books. This project is based on the `educative-content-processor` pattern but adapted for manual, offline markdown content processing.

## Key Differences from Educative Content Processor

### 1. **No API Integration**
- ❌ No Educative API calls
- ❌ No external dependencies for content fetching
- ✅ Fully offline operation
- ✅ All content provided manually by users

### 2. **Manual Chapter Creation**
- Users create chapters one by one via the UI
- Click the "+" button in book details to add chapters
- No automatic chapter generation from API responses

### 3. **Raw Markdown Input**
- Users provide markdown content directly in the UI
- Content is stored locally in the `generated_books` directory
- Markdown is converted to LaTeX using Pandoc (with fallback)

### 4. **Simplified Workflow**
```
Create Book → Add Chapters → Enter Content → Generate LaTeX
```

## Project Structure

```
markdown-content-processor/
├── main.py                      # FastAPI application with offline endpoints
├── latex_generator.py           # LaTeX book generation logic
├── section_processor.py         # Markdown to LaTeX conversion
├── requirements.txt             # Python dependencies
├── README.md                    # User documentation
├── PROJECT_SUMMARY.md          # This file
├── .gitignore                   # Git ignore rules
│
├── static/                      # Frontend UI files
│   ├── index.html              # Main page - book library
│   └── book.html               # Book details - chapter management
│
├── templates/                   # LaTeX template files
│   └── book-template/
│       ├── amd.sty             # LaTeX style package
│       ├── theorems.tex        # Theorem environments
│       └── References.bib      # Bibliography template
│
├── latex_templates/             # Jinja2 templates for LaTeX
│   ├── main.tex.j2             # Main document template
│   └── chapter.tex.j2          # Chapter template
│
└── generated_books/             # Generated book output (created at runtime)
    ├── books_db.json           # Book metadata database
    └── [book-id]/              # Individual book directories
        ├── Main.tex            # Main LaTeX file
        ├── amd.sty             # Copied style file
        ├── theorems.tex        # Copied theorems
        ├── References.bib      # Copied bibliography
        ├── sections/           # Markdown content files
        ├── files/              # Generated LaTeX chapter files
        └── Images/             # Book images
```

## API Endpoints

### Book Management
- `GET /` - Serve main UI
- `GET /health` - Health check
- `GET /api/books` - List all books
- `GET /api/books/{book_id}` - Get book details
- `POST /api/books` - Create new book

### Chapter Management
- `POST /api/chapters` - Create new chapter
- `POST /api/chapters/content` - Update chapter content
- `POST /api/chapters/delete` - Delete chapter

### LaTeX Generation
- `POST /api/generate-latex` - Generate LaTeX book from markdown

## Features

### ✅ Implemented
1. **Book Management**
   - Create books with name and description
   - List all books in library
   - View book details

2. **Chapter Management**
   - Add chapters manually via UI
   - Edit chapter title, summary, and content
   - Delete chapters
   - Chapter status tracking (pending/completed)

3. **UI Components**
   - Modern, responsive design
   - Book library grid view
   - Chapter management interface
   - Modal dialogs for creating/editing

4. **LaTeX Generation**
   - Book structure generation
   - Template-based LaTeX files
   - Front matter (title page, preface, TOC)
   - Chapter files with markdown content

5. **Markdown Processing**
   - Pandoc integration (with fallback)
   - Basic markdown to LaTeX conversion
   - Code block support
   - List and formatting support

### 🚧 To Be Implemented Later
1. **Enhanced Markdown Conversion**
   - Image processing and embedding
   - Table conversion
   - Advanced formatting

2. **LaTeX Compilation**
   - Direct PDF generation
   - Compilation error handling
   - Preview functionality

3. **Content Management**
   - Import/export functionality
   - Bulk chapter operations
   - Content templates

## Usage Workflow

### 1. Start the Server
```bash
cd markdown-content-processor
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py
```

### 2. Create a Book
1. Open http://localhost:8000
2. Click "Create New Book"
3. Enter book name and description
4. Click "Create Book"

### 3. Add Chapters
1. Click on a book to open details
2. Click "➕ Add Chapter"
3. Enter chapter title and summary
4. Paste or write markdown content
5. Click "Save Chapter"

### 4. Generate LaTeX
1. Once chapters are ready, use the API:
```bash
curl -X POST http://localhost:8000/api/generate-latex \
  -H "Content-Type: application/json" \
  -d '{"book_id": "your-book-id"}'
```

2. Find generated files in `generated_books/[book-id]/`

### 5. Compile to PDF
```bash
cd generated_books/[book-id]
pdflatex Main.tex
biber Main
pdflatex Main.tex
pdflatex Main.tex
```

## Technical Details

### Data Storage
- **Format**: JSON file (`generated_books/books_db.json`)
- **Structure**: 
  ```json
  {
    "books": [
      {
        "id": "book-slug",
        "name": "Book Name",
        "description": "Description",
        "created_at": "ISO timestamp",
        "status": "created",
        "chapters": [
          {
            "title": "Chapter Title",
            "summary": "Summary",
            "content_file": "sections/chapter_1.md",
            "content_status": "completed",
            "chapter_number": 1
          }
        ]
      }
    ]
  }
  ```

### Markdown to LaTeX Conversion
1. **Primary**: Uses Pandoc if available
2. **Fallback**: Basic regex-based conversion
3. **Supported Syntax**:
   - Headers (# ## ### ####)
   - Bold (**text** or __text__)
   - Italic (*text* or _text_)
   - Inline code (`code`)
   - Code blocks (```language```)
   - Lists (- or *)
   - Links ([text](url))

### LaTeX Template System
- Uses Jinja2 for template rendering
- Separates structure (templates) from content
- Supports custom styling via `amd.sty`
- Includes theorem environments

## Dependencies

### Required
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `python-dotenv` - Environment management
- `jinja2` - Template engine

### Optional
- `pypandoc` - Markdown to LaTeX conversion (recommended)
- LaTeX distribution (for PDF compilation)

## Comparison with Educative Content Processor

| Feature | Educative Processor | Markdown Processor |
|---------|-------------------|-------------------|
| Content Source | Educative API | Manual input |
| Online/Offline | Online (API calls) | Fully offline |
| Chapter Creation | Automatic from API | Manual via UI |
| Content Input | API response | Raw markdown |
| Authentication | Required (token/cookie) | Not required |
| Use Case | Educative courses | Any markdown content |

## Future Enhancements

1. **Content Import**
   - Import from existing markdown files
   - Bulk chapter import
   - GitHub integration

2. **Export Options**
   - Export to different formats
   - Backup/restore functionality
   - Share books between users

3. **Editor Improvements**
   - Live markdown preview
   - Syntax highlighting
   - Auto-save functionality

4. **LaTeX Features**
   - Custom templates
   - Style customization
   - Multiple output formats

## Notes for Developers

### Adding New Endpoints
1. Define Pydantic models in `main.py`
2. Create endpoint function with `@app.post()` or `@app.get()`
3. Update UI to call the new endpoint

### Modifying Templates
1. Edit Jinja2 templates in `latex_templates/`
2. Update `latex_generator.py` if structure changes
3. Test with sample book generation

### Customizing UI
1. Edit HTML files in `static/`
2. Styles are inline (can be extracted to CSS)
3. JavaScript is vanilla (no framework dependencies)

## License
MIT License

## Support
For issues or questions, refer to the README.md file.
