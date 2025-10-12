# Quiz Component - Quick Reference

## Component Type
**Type:** `Quiz`

## Key Features
✅ Multiple-choice questions  
✅ Multiple-answer support  
✅ Correct answer marking  
✅ Explanations for answers  
✅ HTML to LaTeX conversion  
✅ Custom quiz titles  

## Backend Structure (Minimal)
```json
{
    "type": "Quiz",
    "content": {
        "title": "Optional Quiz Title",
        "questions": [
            {
                "questionTextHtml": "<p>Question?</p>",
                "multipleAnswers": false,
                "questionOptions": [
                    {
                        "mdHtml": "<p>Option text</p>",
                        "correct": true,
                        "explanation": {
                            "mdHtml": "<p>Why this is correct</p>"
                        }
                    }
                ]
            }
        ]
    }
}
```

## LaTeX Output Example
```latex
\subsection*{Quiz}
\vspace{0.3cm}
\noindent
\textbf{Question 1:} What is 2+2?
\\[0.2cm]
\begin{itemize}
    \item \textbf{[CORRECT]} 4
\\[0.1cm]
\textit{Explanation:} 
Basic arithmetic: 2 + 2 = 4
    \item 3
    \item 5
\end{itemize}
```

## Processing Method
```python
processor._process_quiz(component)
```

## Integration Points
- **Async:** Line 171-173 in `section_processor.py`
- **Sync:** Line 252-254 in `section_processor.py`
- **Method:** Line 651-731 in `section_processor.py`

## Testing
```bash
# Basic test
python test_quiz_processor.py

# Compilation test
python test_quiz_compilation.py
pdflatex test_quiz_compile.tex
```

## Common Customizations

### Change Correct Answer Marker
```python
# Line 715 in section_processor.py
latex_parts.append(f"    \\item \\textbf{{[✓]}} {opt_latex.strip()}")
```

### Adjust Question Spacing
```python
# Line 679 in section_processor.py
latex_parts.append("\\vspace{0.5cm}")  # Increase from 0.3cm
```

### Hide Correct Answers
```python
# Line 714-715 in section_processor.py
# Comment out or remove the [CORRECT] marker
latex_parts.append(f"    \\item {opt_latex.strip()}")
```

## Supported Fields

### Question Object
- `questionText` - Plain text (fallback)
- `questionTextHtml` - HTML format (preferred)
- `questionOptions` - Array of options
- `multipleAnswers` - Boolean flag
- `id` - Unique identifier (not used in output)

### Option Object
- `text` - Plain text (fallback)
- `mdHtml` - HTML format (preferred)
- `correct` - Boolean flag
- `explanation.mdText` - Plain explanation (fallback)
- `explanation.mdHtml` - HTML explanation (preferred)
- `id` - Unique identifier (not used in output)

### Quiz Content
- `title` - Custom quiz title
- `titleMdHtml` - HTML title (not currently used)
- `comp_id` - Component ID (not used in output)
- `questions` - Array of question objects

## HTML Conversion
Uses `_html_to_latex_pandoc()` for:
- Question text
- Option text
- Explanations

Handles:
- `<p>` → Paragraphs
- `<strong>` → `\textbf{}`
- `<em>` → `\textit{}`
- `<code>` → `\texttt{}`
- Special characters → Escaped

## Error Handling
- Empty questions → Skipped
- Missing HTML → Falls back to plain text
- Missing explanations → Not displayed
- Pandoc failure → Uses `_escape_latex()` fallback

## Dependencies
- `pypandoc` - HTML to LaTeX conversion
- Standard LaTeX packages (inputenc, fontenc)

## Related Documentation
- Full docs: `QUIZ_COMPONENT_DOCUMENTATION.md`
- Section processor: `section_processor.py`
- Test files: `test_quiz_*.py`
