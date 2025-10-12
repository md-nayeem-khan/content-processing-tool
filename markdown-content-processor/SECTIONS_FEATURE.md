# Sections Feature - Hierarchical Content Structure

## Overview

The markdown-content-processor now supports a **hierarchical content structure** with sections under chapters, following the educative-content-processor pattern.

## Structure

```
Book
├── Chapter 1
│   ├── Section 1.1
│   ├── Section 1.2
│   └── Section 1.3
├── Chapter 2
│   ├── Section 2.1
│   └── Section 2.2
└── Chapter 3
    ├── Section 3.1
    ├── Section 3.2
    └── Section 3.3
```

## Data Model

### BookSection
```python
class BookSection(BaseModel):
    title: str                    # Section title
    id: str                       # Unique section ID (UUID)
    slug: str                     # URL-friendly slug
    content_file: Optional[str]   # Path to markdown file
    content_status: str           # "pending" or "completed"
    created_at: Optional[str]     # ISO timestamp
    updated_at: Optional[str]     # ISO timestamp
```

### BookChapter
```python
class BookChapter(BaseModel):
    title: str                    # Chapter title
    summary: Optional[str]        # Chapter summary
    sections: List[BookSection]   # List of sections
    chapter_number: Optional[int] # Chapter number
    created_at: Optional[str]     # ISO timestamp
```

## API Endpoints

### Section Management

#### 1. Create Section
```http
POST /api/sections
Content-Type: application/json

{
  "book_id": "my_book",
  "chapter_index": 0,
  "section_title": "Introduction to Python"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Section created successfully",
  "section_id": "a1b2c3d4"
}
```

#### 2. Update Section Content
```http
POST /api/sections/content
Content-Type: application/json

{
  "book_id": "my_book",
  "chapter_index": 0,
  "section_id": "a1b2c3d4",
  "markdown_content": "# Introduction\n\nPython is..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Section content updated successfully"
}
```

#### 3. Delete Section
```http
POST /api/sections/delete
Content-Type: application/json

{
  "book_id": "my_book",
  "chapter_index": 0,
  "section_id": "a1b2c3d4"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Section deleted successfully"
}
```

### Chapter Update (Modified)

#### Update Chapter Metadata
```http
POST /api/chapters/update
Content-Type: application/json

{
  "book_id": "my_book",
  "chapter_index": 0,
  "chapter_title": "New Chapter Title",
  "chapter_summary": "Updated summary"
}
```

## File Structure

### Content Files

Sections are stored as individual markdown files:

```
generated_books/my_book/
├── sections/
│   ├── chapter_1_section_introduction.md
│   ├── chapter_1_section_basics.md
│   ├── chapter_2_section_advanced.md
│   └── chapter_2_section_examples.md
```

### Generated LaTeX

Chapters now include sections dynamically:

```latex
\chapter{Chapter Title}

\intro{Chapter summary}

\section{Section 1 Title}
% Section content from markdown

\section{Section 2 Title}
% Section content from markdown
```

## Workflow

### Creating Content

1. **Create Book**
   ```
   User: Creates "Python Guide"
   System: ✅ Book created with Main.tex
   ```

2. **Add Chapter**
   ```
   User: Adds "Introduction" chapter
   System: ✅ Chapter created
   System: ✅ Main.tex updated
   ```

3. **Add Sections**
   ```
   User: Adds "What is Python?" section
   System: ✅ Section created with ID
   System: ✅ LaTeX regenerated
   
   User: Adds "Installing Python" section
   System: ✅ Section created
   System: ✅ LaTeX regenerated
   ```

4. **Add Content to Sections**
   ```
   User: Edits "What is Python?" section
   User: Enters markdown content
   System: ✅ Content saved to file
   System: ✅ LaTeX regenerated with content
   ```

### Example Database Structure

```json
{
  "books": [
    {
      "id": "python_guide",
      "name": "Python Guide",
      "description": "A comprehensive guide",
      "chapters": [
        {
          "title": "Introduction",
          "summary": "Getting started with Python",
          "chapter_number": 1,
          "sections": [
            {
              "title": "What is Python?",
              "id": "a1b2c3d4",
              "slug": "what_is_python",
              "content_file": "sections/chapter_1_section_what_is_python.md",
              "content_status": "completed",
              "created_at": "2025-01-12T01:00:00",
              "updated_at": "2025-01-12T01:05:00"
            },
            {
              "title": "Installing Python",
              "id": "e5f6g7h8",
              "slug": "installing_python",
              "content_status": "pending",
              "created_at": "2025-01-12T01:10:00"
            }
          ]
        }
      ]
    }
  ]
}
```

## LaTeX Generation

### Chapter Template (chapter.tex.j2)

```latex
\documentclass[../Main.tex]{subfiles}

\begin{document}
\chapter{ {{chapter.title | escape_latex}} }

{% if chapter.summary %}
\intro{
{{chapter.summary | escape_latex}}
}
{% endif %}

{% if chapter.sections %}
% Sections dynamically generated from user input
{% for section in chapter.sections %}
\section{ {{section.title | escape_latex}} }

% Section ID: {{section.id}}
% Slug: {{section.slug}}
% Status: {{section.content_status}}

{{section.latex_content}}

{% endfor %}
{% else %}
% No sections added yet - chapter created but empty
{% endif %}

\end{document}
```

### Generated Output Example

For a chapter with 2 sections:

```latex
\chapter{Introduction to Python}

\intro{
This chapter introduces Python programming language.
}

% Sections dynamically generated from user input
\section{What is Python?}

% Section ID: a1b2c3d4
% Slug: what_is_python
% Status: completed

Python is a high-level programming language...

\section{Installing Python}

% Section ID: e5f6g7h8
% Slug: installing_python
% Status: completed

To install Python, visit python.org...
```

## Benefits

### ✅ Better Organization
- Content organized hierarchically
- Clear structure: Book → Chapter → Section
- Each section has its own file

### ✅ Granular Control
- Add/edit/delete individual sections
- Track status per section
- Independent content management

### ✅ Flexibility
- Chapters can have any number of sections
- Sections can be reordered (future feature)
- Easy to manage large books

### ✅ Follows Industry Pattern
- Same structure as educative-content-processor
- Familiar to users of educational platforms
- Professional book organization

## Migration from Old Structure

### Old Structure (Chapter-level content)
```
Chapter 1
  └── Single markdown file with all content
```

### New Structure (Section-level content)
```
Chapter 1
  ├── Section 1.1 → markdown file
  ├── Section 1.2 → markdown file
  └── Section 1.3 → markdown file
```

### Migration Steps

For existing books without sections:

1. **Option 1: Keep as-is**
   - Chapters without sections still work
   - Template shows "No sections added yet"

2. **Option 2: Convert to sections**
   - Create a single section per chapter
   - Move chapter content to section content
   - More flexible for future edits

## UI Updates (To Be Implemented)

The UI will be updated to support:

1. **Chapter View**
   - Show sections list under each chapter
   - "+" button to add sections
   - Section status indicators

2. **Section Management**
   - Edit section title
   - Edit section content (markdown)
   - Delete section
   - Reorder sections (future)

3. **Visual Hierarchy**
   ```
   📖 Chapter 1: Introduction
      📄 Section 1.1: What is Python? ✅
      📄 Section 1.2: Installing Python ⏳
      ➕ Add Section
   ```

## Testing

### Test 1: Create Section
```bash
curl -X POST http://localhost:8000/api/sections \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": "test",
    "chapter_index": 0,
    "section_title": "Introduction"
  }'
```

### Test 2: Add Content
```bash
curl -X POST http://localhost:8000/api/sections/content \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": "test",
    "chapter_index": 0,
    "section_id": "a1b2c3d4",
    "markdown_content": "# Introduction\n\nThis is the intro..."
  }'
```

### Test 3: Verify LaTeX
```bash
cd generated_books/test
cat files/chapter_1_*.tex
# Should show section with content
```

## Future Enhancements

1. **Section Reordering**
   - Drag-and-drop in UI
   - Update order in database
   - Regenerate LaTeX

2. **Section Templates**
   - Predefined section structures
   - Quick start templates
   - Common patterns

3. **Section Metadata**
   - Estimated reading time
   - Difficulty level
   - Tags/categories

4. **Bulk Operations**
   - Import multiple sections
   - Export sections
   - Duplicate sections

## Summary

The sections feature provides:
- ✅ **Hierarchical structure**: Book → Chapter → Section
- ✅ **Granular content management**: Edit individual sections
- ✅ **Automatic LaTeX generation**: Sections dynamically included
- ✅ **Industry-standard pattern**: Follows educative-content-processor
- ✅ **Flexible organization**: Any number of sections per chapter

This makes the markdown-content-processor more robust and suitable for creating complex, well-organized books.

---

**Version**: 1.3.0
**Date**: January 12, 2025
**Status**: ✅ Backend Complete, UI Update Pending
