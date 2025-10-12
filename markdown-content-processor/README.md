# Markdown Content Processor

A fully offline content processing tool that converts raw markdown content into beautifully formatted LaTeX books.

## Features

- **Fully Offline**: No API calls required - all processing happens locally
- **Manual Content Input**: Users provide raw markdown content directly
- **Book Management**: Create and manage multiple books
- **Chapter Management**: Add chapters one by one with manual content
- **Dynamic LaTeX Generation**: Main.tex file is dynamically generated based on chapters
- **Template-Based**: Uses Jinja2 templates for flexible LaTeX generation
- **Modern UI**: Clean, intuitive web interface

## Key Differences from Educative Content Processor

- **No API Integration**: Completely offline, no external API calls
- **Manual Chapter Creation**: Users create chapters manually via UI (+ button)
- **Raw Markdown Input**: Users provide markdown content directly
- **Simplified Workflow**: Focused on markdown-to-LaTeX conversion

## Installation

1. Create a virtual environment:
```bash
python -m venv .venv
```

2. Activate the virtual environment:
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the server:
```bash
python main.py
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

3. Create a new book:
   - Click "Create New Book"
   - Enter book name and description
   - Click "Create Book"

4. Add chapters:
   - Click on a book to view details
   - Click the "+" button to add a new chapter
   - Enter chapter title and content
   - Save the chapter

5. LaTeX Files:
   - The `Main.tex` file is **automatically generated** when you create a book
   - It's **automatically updated** when you add, edit, or delete chapters
   - Find your LaTeX files in `generated_books/[book-id]/`
   - You can also manually regenerate using the API if needed

## Project Structure

```
markdown-content-processor/
├── main.py                 # FastAPI application
├── latex_generator.py      # LaTeX generation logic
├── section_processor.py    # Markdown to LaTeX conversion
├── requirements.txt        # Python dependencies
├── static/                 # Frontend files
│   ├── index.html         # Main page (book list)
│   └── book.html          # Book details page
├── templates/             # LaTeX templates
│   └── book-template/     # Book template files
├── latex_templates/       # Jinja2 templates for LaTeX
└── generated_books/       # Generated book output
```

## Technologies

- **Backend**: FastAPI, Python
- **Frontend**: HTML, CSS, JavaScript
- **LaTeX**: Pandoc, Jinja2
- **Storage**: File-based JSON

## License

MIT License
