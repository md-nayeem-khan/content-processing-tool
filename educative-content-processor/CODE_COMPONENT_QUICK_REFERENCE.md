# Code Component - Quick Reference

## What is it?
The Code component displays syntax-highlighted code blocks in the generated PDF books.

## Backend Structure
```json
{
    "type": "Code",
    "content": {
        "caption": "Code description",
        "language": "python|javascript|java|...",
        "content": "actual code here",
        "title": "optional title"
    }
}
```

## LaTeX Output
```latex
\textbf{Caption}

\begin{lstlisting}[language=Python]
code here
\end{lstlisting}
```

## Supported Languages
| Backend Name | LaTeX Name | Notes |
|-------------|------------|-------|
| python | Python | ✅ Full support |
| javascript | JavaScript | ✅ Full support |
| typescript | JavaScript | Uses JS highlighting |
| java | Java | ✅ Full support |
| cpp, c++ | C++ | ✅ Full support |
| c | C | ✅ Full support |
| csharp, c# | C | Approximation |
| shell, bash | bash | ✅ Full support |
| sql | SQL | ✅ Full support |
| html | HTML | ✅ Full support |
| css | CSS | ✅ Full support |
| php | PHP | ✅ Full support |
| ruby | Ruby | ✅ Full support |
| go | Go | ✅ Full support |
| rust | Rust | ✅ Full support |
| swift | Swift | ✅ Full support |
| kotlin | Kotlin | ✅ Full support |
| xml | XML | ✅ Full support |
| json | JavaScript | Uses JS highlighting |
| yaml | Python | Uses Python highlighting |
| dockerfile | bash | Uses bash highlighting |
| markdown | TeX | Uses TeX highlighting |

## Code Location
- **Handler**: `section_processor.py` → `_process_code()` method (line 1085)
- **Integration**: Lines 196-198 (async) and 273-275 (sync)
- **LaTeX Config**: `templates/book-template/amd.sty` (lines 20, 25-48)

## Testing
```bash
python test_code_component.py
```

## Example Usage

### Input (Backend JSON)
```json
{
    "type": "Code",
    "content": {
        "caption": "HAProxy Configuration",
        "language": "shell",
        "content": "mode HTTP\nacl slidesApp path_end -i /presentation"
    }
}
```

### Output (LaTeX)
```latex
\textbf{HAProxy Configuration}

\begin{lstlisting}[language=bash]
mode HTTP
acl slidesApp path_end -i /presentation
\end{lstlisting}
```

### Result (PDF)
- Syntax-highlighted code block
- Line numbers on the left
- Framed box around code
- Caption above the code

## Styling Features
- ✅ **Syntax highlighting with colors**
  - Keywords: Blue (bold)
  - Strings: Orange
  - Comments: Green (italic)
  - Numbers: Gray
- ✅ Line numbers (left margin)
- ✅ Light gray background
- ✅ Frame border
- ✅ Automatic line wrapping
- ✅ Monospace font
- ✅ Professional appearance

See `CODE_SYNTAX_COLORS.md` for detailed color scheme information.

## Common Issues & Solutions

### Issue: Code appears on one line
**Cause**: Backend sends code without newlines
**Solution**: Already handled - LaTeX will format properly

### Issue: Special characters break LaTeX
**Cause**: LaTeX special chars in caption
**Solution**: Already handled - captions are escaped

### Issue: Unknown language
**Cause**: Language not in mapping table
**Solution**: Falls back to plain text (no highlighting)

### Issue: Code too wide for page
**Cause**: Long lines without breaks
**Solution**: Already handled - `breaklines=true` in config

## Adding New Languages

To add a new language:

1. Edit `section_processor.py`
2. Find the `language_map` dictionary in `_process_code()`
3. Add your mapping:
   ```python
   'newlang': 'LaTeXName',
   ```
4. Test with sample code

## Performance Notes
- ✅ No external dependencies
- ✅ Fast processing (pure text manipulation)
- ✅ No image generation required
- ✅ Works offline

## Related Components
- **MarkdownEditor**: For markdown text
- **SlateHTML**: For rich text
- **Latex**: For math equations
- **Table**: For tabular data

## Version History
- **v1.0** (2025-10-11): Initial implementation with 20+ language support
