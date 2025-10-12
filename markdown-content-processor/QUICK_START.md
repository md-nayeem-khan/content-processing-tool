# Quick Start Guide - Markdown Content Processor

## Installation

### 1. Navigate to the project directory
```bash
cd d:\projects\content-processing-tool\markdown-content-processor
```

### 2. Create and activate virtual environment
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Install Pandoc for better markdown conversion
Download and install from: https://pandoc.org/installing.html

Then install Python wrapper:
```bash
pip install pypandoc
```

## Running the Application

### Start the server
```bash
python main.py
```

You should see:
```
============================================================
🚀 Starting Markdown Content Processor
============================================================
📍 Server: http://localhost:8000
📚 API Docs: http://localhost:8000/docs
🔍 Health: http://localhost:8000/health
============================================================
```

### Access the application
Open your browser and navigate to:
- **Main UI**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Basic Usage

### Step 1: Create a Book
1. Click the **"Create New Book"** button
2. Enter:
   - **Book Name**: e.g., "My First Book"
   - **Description**: e.g., "A collection of my markdown notes"
3. Click **"Create Book"**

### Step 2: Add Chapters
1. Click on your newly created book
2. Click the **"➕ Add Chapter"** button
3. Enter:
   - **Chapter Title**: e.g., "Introduction"
   - **Chapter Summary**: (optional) Brief description
   - **Markdown Content**: Your markdown text
4. Click **"Save Chapter"**

### Step 3: Add More Chapters
Repeat Step 2 to add as many chapters as you need.

### Step 4: Generate LaTeX
Use the API to generate LaTeX files:

```bash
curl -X POST http://localhost:8000/api/generate-latex \
  -H "Content-Type: application/json" \
  -d "{\"book_id\": \"my_first_book\"}"
```

Or use the API documentation interface at http://localhost:8000/docs

### Step 5: Compile to PDF (Optional)
If you have LaTeX installed:

```bash
cd generated_books/my_first_book
pdflatex Main.tex
biber Main
pdflatex Main.tex
pdflatex Main.tex
```

## Example Markdown Content

Here's a sample chapter content you can use:

```markdown
# Introduction to Markdown

This is a sample chapter demonstrating markdown features.

## Basic Formatting

You can use **bold text** and *italic text* for emphasis.

## Code Examples

Inline code: `print("Hello, World!")`

Code block:
```python
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
```

## Lists

### Unordered List
- Item 1
- Item 2
- Item 3

### Ordered List
1. First item
2. Second item
3. Third item

## Links

Visit [GitHub](https://github.com) for more information.

## Sections

### Subsection 1
Content for subsection 1.

### Subsection 2
Content for subsection 2.
```

## Project Structure After First Run

```
markdown-content-processor/
├── generated_books/
│   ├── books_db.json           # Your books database
│   └── my_first_book/          # Your book directory
│       ├── Main.tex            # Main LaTeX file
│       ├── amd.sty             # Style file
│       ├── theorems.tex        # Theorem definitions
│       ├── References.bib      # Bibliography
│       ├── sections/           # Your markdown files
│       │   └── chapter_1.md
│       ├── files/              # Generated LaTeX chapters
│       │   ├── 0.0.0.titlepage.tex
│       │   ├── 0.Preface.tex
│       │   ├── 0.zommaire.tex
│       │   └── chapter_1.tex
│       └── Images/             # Book images (empty initially)
```

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, modify `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
```

### Pandoc Not Found
If you get pandoc errors, the system will fall back to basic conversion automatically. For best results, install pandoc.

### LaTeX Compilation Errors
Make sure you have a LaTeX distribution installed:
- **Windows**: MiKTeX or TeX Live
- **Linux**: `sudo apt-get install texlive-full`
- **Mac**: MacTeX

## API Endpoints Quick Reference

### Books
- `GET /api/books` - List all books
- `GET /api/books/{book_id}` - Get book details
- `POST /api/books` - Create new book

### Chapters
- `POST /api/chapters` - Create chapter
- `POST /api/chapters/content` - Update chapter content
- `POST /api/chapters/delete` - Delete chapter

### Generation
- `POST /api/generate-latex` - Generate LaTeX book

## Next Steps

1. **Explore the UI**: Try creating multiple books and chapters
2. **Test Markdown**: Experiment with different markdown syntax
3. **Generate LaTeX**: Create your first LaTeX book
4. **Compile PDF**: If you have LaTeX installed, compile to PDF
5. **Customize**: Modify templates in `latex_templates/` for custom styling

## Getting Help

- Check `README.md` for detailed documentation
- Check `PROJECT_SUMMARY.md` for technical details
- Visit http://localhost:8000/docs for interactive API documentation

## Tips

1. **Save Often**: The UI doesn't have auto-save, so save your work frequently
2. **Markdown Preview**: Use a markdown editor with preview for complex content
3. **Chapter Order**: Chapters are displayed in the order they were created
4. **Content Status**: Green badge = completed, Orange badge = pending
5. **LaTeX Errors**: Check the generated `.tex` files if compilation fails

Happy writing! 📝
