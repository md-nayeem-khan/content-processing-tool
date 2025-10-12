# Dynamic LaTeX Generation in Markdown Content Processor

## Overview

The Markdown Content Processor dynamically generates the `Main.tex` file based on the chapters created by the user. This ensures that the LaTeX document structure always reflects the current state of the book.

## How It Works

### 1. Dynamic Chapter Mapping

When you create chapters in the UI, they are stored in the book's metadata. When generating LaTeX:

1. **Chapter Slugification**: Each chapter title is converted to a slug (e.g., "Introduction to Python" → "introduction_to_python")
2. **Dynamic File Naming**: Chapter files are named as `chapter_N_slug.tex` where N is the chapter number
3. **Main.tex Generation**: The `Main.tex` file is regenerated to include all current chapters

### 2. Template-Based Generation

The system uses Jinja2 templates to generate LaTeX files:

#### Main.tex Template (`latex_templates/main.tex.j2`)
```latex
\documentclass[A4,12pt,twoside]{book}
\usepackage{amd}

\newcommand{\BigTitle}{
    {{book_title}}
}

\newcommand{\LittleTitle}{
    {{book_description}}
}

\begin{document}

% Front matter
\subfile{files/0.0.0.titlepage}
\subfile{files/0.Preface}
\subfile{files/0.zommaire}

% Main content - dynamically generated chapters
{% for chapter in chapters %}
\subfile{files/chapter_{{chapter.chapter_number}}_{{chapter.chapter_slug}}}
{% endfor %}

% Bibliography
\printbibliography

\end{document}
```

### 3. Generation Process

When you call the LaTeX generation API:

```python
# 1. Load book data from database
book_data = {
    "id": "my_book",
    "name": "My Awesome Book",
    "description": "A great book",
    "chapters": [
        {
            "title": "Introduction",
            "summary": "Getting started",
            "content_file": "sections/chapter_1.md"
        },
        {
            "title": "Advanced Topics",
            "summary": "Deep dive",
            "content_file": "sections/chapter_2.md"
        }
    ]
}

# 2. Generate slugs for each chapter
chapters_with_slugs = [
    {
        "chapter_number": 1,
        "chapter_slug": "introduction",
        "title": "Introduction",
        ...
    },
    {
        "chapter_number": 2,
        "chapter_slug": "advanced_topics",
        "title": "Advanced Topics",
        ...
    }
]

# 3. Render Main.tex with chapter references
# Result:
# \subfile{files/chapter_1_introduction}
# \subfile{files/chapter_2_advanced_topics}

# 4. Generate individual chapter files
# - files/chapter_1_introduction.tex
# - files/chapter_2_advanced_topics.tex
```

## File Structure

After generation, your book directory looks like:

```
generated_books/my_book/
├── Main.tex                          # Dynamically generated main file
├── amd.sty                           # Style package
├── theorems.tex                      # Theorem definitions
├── References.bib                    # Bibliography
├── sections/                         # Your markdown content
│   ├── chapter_1.md
│   └── chapter_2.md
├── files/                            # Generated LaTeX files
│   ├── 0.0.0.titlepage.tex          # Title page
│   ├── 0.Preface.tex                # Preface (with chapter count)
│   ├── 0.zommaire.tex               # Table of contents
│   ├── chapter_1_introduction.tex   # Chapter 1 content
│   └── chapter_2_advanced_topics.tex # Chapter 2 content
└── Images/                           # Book images
```

## Example: Main.tex Output

For a book with 3 chapters, the generated `Main.tex` would look like:

```latex
% Main LaTeX document template for Markdown Content Processor
% Generated dynamically based on book chapters
\documentclass[A4,12pt,twoside]{book}
\usepackage{amd}

% Book Information
\newcommand{\BigTitle}{
    Python Programming Guide
}

\newcommand{\LittleTitle}{
    A comprehensive guide to Python
}

\begin{document}

% Front matter
\newgeometry{top=8cm,bottom=.5in,left=2cm,right=2cm}
\subfile{files/0.0.0.titlepage}
\restoregeometry
\subfile{files/0.Preface}
\subfile{files/0.zommaire}

% Main content - dynamically generated chapters
% Total chapters: 3
\subfile{files/chapter_1_introduction}
\subfile{files/chapter_2_basic_syntax}
\subfile{files/chapter_3_advanced_topics}

% Bibliography
\nocite{*}
\printbibliography

\end{document}
```

## Adding/Removing Chapters

### When You Add a Chapter

1. Create chapter via UI (click "+" button)
2. Enter chapter title and content
3. Save chapter
4. Regenerate LaTeX:
   ```bash
   curl -X POST http://localhost:8000/api/generate-latex \
     -H "Content-Type: application/json" \
     -d '{"book_id": "my_book"}'
   ```
5. **Main.tex is regenerated** with the new chapter included
6. New chapter file is created: `files/chapter_N_slug.tex`

### When You Delete a Chapter

1. Delete chapter via UI
2. Chapters are renumbered automatically
3. Regenerate LaTeX
4. **Main.tex is regenerated** with updated chapter list
5. Old chapter files remain but are not referenced

## Comparison with Static Approach

### ❌ Static Approach (Not Used)
```latex
% Fixed chapter list - must manually edit
\subfile{files/chapter_1}
\subfile{files/chapter_2}
\subfile{files/chapter_3}
```

**Problems:**
- Must manually edit Main.tex when adding chapters
- Chapter numbering gets out of sync
- Error-prone

### ✅ Dynamic Approach (Used)
```latex
% Automatically generated from book data
{% for chapter in chapters %}
\subfile{files/chapter_{{chapter.chapter_number}}_{{chapter.chapter_slug}}}
{% endfor %}
```

**Benefits:**
- ✅ Always in sync with book data
- ✅ Automatic chapter numbering
- ✅ No manual editing required
- ✅ Consistent naming

## Chapter File Naming Convention

The system uses a consistent naming pattern:

```
chapter_[NUMBER]_[SLUG].tex
```

**Examples:**
- "Introduction" → `chapter_1_introduction.tex`
- "Getting Started" → `chapter_2_getting_started.tex`
- "Advanced Topics!" → `chapter_3_advanced_topics.tex`

**Slug Rules:**
1. Convert to lowercase
2. Replace spaces with underscores
3. Remove special characters
4. Remove leading/trailing underscores

## Regenerating LaTeX

You should regenerate LaTeX whenever:

1. ✅ You add a new chapter
2. ✅ You delete a chapter
3. ✅ You update chapter content
4. ✅ You change chapter titles
5. ✅ You change book metadata

### Via API
```bash
curl -X POST http://localhost:8000/api/generate-latex \
  -H "Content-Type: application/json" \
  -d '{"book_id": "your_book_id"}'
```

### Via API Docs
1. Go to http://localhost:8000/docs
2. Find `/api/generate-latex` endpoint
3. Click "Try it out"
4. Enter book_id
5. Click "Execute"

## Integration with Markdown Processing

When generating chapter files:

1. **Read markdown content** from `sections/chapter_N.md`
2. **Convert to LaTeX** using Pandoc (or fallback converter)
3. **Inject into chapter template**:
   ```latex
   \documentclass[../Main.tex]{subfiles}
   \begin{document}
   \chapter{Chapter Title}
   
   % Converted markdown content goes here
   {{chapter_content}}
   
   \end{document}
   ```
4. **Save as** `files/chapter_N_slug.tex`

## Preface Generation

The preface is also dynamically generated with book statistics:

```latex
\chapter*{Preface}

This book was generated using the Markdown Content Processor...

\textbf{Book Statistics:}
\begin{itemize}
    \item Total Chapters: 5
    \item Generated: January 12, 2025
\end{itemize}
```

## Best Practices

### 1. Regenerate After Changes
Always regenerate LaTeX after making changes to chapters:
```bash
# After adding/editing chapters
curl -X POST http://localhost:8000/api/generate-latex \
  -H "Content-Type: application/json" \
  -d '{"book_id": "my_book"}'
```

### 2. Use Descriptive Chapter Titles
Good titles create readable file names:
- ✅ "Introduction to Python" → `chapter_1_introduction_to_python.tex`
- ❌ "Ch1" → `chapter_1_ch1.tex`

### 3. Keep Chapter Order
Chapters are included in the order they were created. To reorder:
1. Note the content
2. Delete and recreate in desired order
3. Regenerate LaTeX

### 4. Check Generated Files
After generation, verify:
```bash
cd generated_books/my_book
cat Main.tex  # Check chapter references
ls files/     # Verify all chapter files exist
```

## Troubleshooting

### Issue: Chapter not appearing in PDF
**Solution:** Regenerate LaTeX to update Main.tex

### Issue: Wrong chapter order
**Solution:** Chapters follow creation order. Delete and recreate in correct order.

### Issue: Missing chapter file
**Solution:** Ensure chapter has content saved, then regenerate LaTeX

### Issue: LaTeX compilation error
**Solution:** Check that all referenced chapter files exist in `files/` directory

## Summary

The dynamic Main.tex generation ensures that:
- ✅ Your LaTeX structure always matches your book data
- ✅ Chapters are automatically numbered and referenced
- ✅ No manual editing of LaTeX files required
- ✅ Consistent and predictable file naming
- ✅ Easy to add, remove, or modify chapters

This approach mirrors the educative-content-processor pattern while being adapted for manual markdown content input.
