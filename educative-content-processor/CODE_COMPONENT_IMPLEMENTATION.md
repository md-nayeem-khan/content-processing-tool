# Code Component Implementation

## Overview
Added support for processing 'Code' type content components from the Educative backend API. Code components are rendered as syntax-highlighted code blocks in the generated LaTeX/PDF output.

## Implementation Date
2025-10-11

## Changes Made

### 1. Section Processor (`section_processor.py`)

#### Added `_process_code()` Method
- **Location**: Lines 1085-1169
- **Purpose**: Processes Code components and converts them to LaTeX `lstlisting` environments
- **Features**:
  - Extracts code content, language, caption, and title from backend response
  - Maps Educative language names to LaTeX listings package language names
  - Supports 20+ programming languages including Python, JavaScript, Java, C++, Shell, SQL, etc.
  - Properly escapes LaTeX special characters in captions
  - Generates formatted code blocks with syntax highlighting

#### Language Mapping
The implementation includes a comprehensive language mapping table:
```python
language_map = {
    'javascript': 'JavaScript',
    'python': 'Python',
    'java': 'Java',
    'cpp': 'C++',
    'shell': 'bash',
    'sql': 'SQL',
    'html': 'HTML',
    'css': 'CSS',
    # ... and more
}
```

#### Integration Points
- **Async Processing**: Added Code handler to `process_section_components_async()` (line 196-198)
- **Sync Processing**: Added Code handler to `process_section_components()` (line 273-275)

### 2. LaTeX Template (`templates/book-template/amd.sty`)

#### Added Listings Package
- **Line 20**: Added `\RequirePackage{listings}` for code listing support

#### Configured Listings Styling
- **Lines 25-48**: Added comprehensive `\lstset{}` configuration with:
  - Monospace font for code
  - Line numbers on the left
  - Single-line frame border
  - Automatic line breaking
  - Gray line numbers
  - Proper spacing and margins
  - Escape characters for special LaTeX commands

## Backend Response Structure

The Code component from the backend has the following structure:

```json
{
    "type": "Code",
    "mode": "edit",
    "content": {
        "version": "8.0",
        "caption": "Description of the code",
        "language": "shell",
        "title": "",
        "content": "actual code content here...",
        "runnable": false,
        "showSolution": false,
        "entryFileName": "filename",
        // ... other metadata
    }
}
```

## Generated LaTeX Output

For a Code component, the system generates:

```latex
\textbf{Caption text here}

\begin{lstlisting}[language=bash]
code content here
line 2
line 3
\end{lstlisting}
```

## Supported Languages

The implementation supports the following languages with proper syntax highlighting:
- **Web**: JavaScript, TypeScript, HTML, CSS, JSON
- **Backend**: Python, Java, C++, C, C#, Go, Rust, PHP, Ruby, Swift, Kotlin
- **Database**: SQL
- **Shell**: Bash, Shell
- **Config**: YAML, XML, Dockerfile
- **Documentation**: Markdown

## Testing

### Test Script: `test_code_component.py`
- Tests Code component processing with sample HAProxy configuration
- Verifies LaTeX output contains:
  - Proper `lstlisting` environment
  - Caption formatting
  - Code content preservation
- Saves output to `test_code_output.tex` for inspection

### Test Results
✅ All tests passed successfully
- Code component type correctly detected
- LaTeX environment properly generated
- Caption and content correctly formatted
- Language mapping works as expected

## Usage Example

When the backend provides a Code component:

```python
{
    "type": "Code",
    "content": {
        "caption": "Python Hello World",
        "language": "python",
        "content": "print('Hello, World!')"
    }
}
```

The system generates:

```latex
\textbf{Python Hello World}

\begin{lstlisting}[language=Python]
print('Hello, World!')
\end{lstlisting}
```

## Benefits

1. **Syntax Highlighting**: Code blocks are rendered with proper syntax highlighting in PDF
2. **Line Numbers**: Automatic line numbering for better code reference
3. **Professional Formatting**: Consistent, professional appearance with frames and spacing
4. **Multi-Language Support**: Handles 20+ programming languages
5. **Automatic Line Breaking**: Long lines are automatically wrapped
6. **Caption Support**: Descriptive captions help readers understand code purpose

## Future Enhancements

Potential improvements for future versions:
1. Add support for line highlighting (emphasizing specific lines)
2. Support for code execution output display
3. Custom color schemes per language
4. Support for inline code snippets (currently only block-level)
5. Add support for code diff/comparison views

## Files Modified

1. `section_processor.py` - Added Code component handler
2. `templates/book-template/amd.sty` - Added listings package and configuration
3. `test_code_component.py` - Created test script (new file)
4. `CODE_COMPONENT_IMPLEMENTATION.md` - This documentation (new file)

## Dependencies

- **LaTeX Package**: `listings` (now included in template)
- **Python**: No new dependencies required (uses existing infrastructure)

## Compatibility

- ✅ Works with both async and sync processing methods
- ✅ Compatible with existing component types
- ✅ No breaking changes to existing functionality
- ✅ Follows existing code patterns and conventions

## Notes

- The `listings` package is widely supported in LaTeX distributions
- Code blocks automatically fit within page margins
- Special LaTeX characters in captions are properly escaped
- Empty or missing code content is handled gracefully
- Unknown languages fall back to plain text formatting
