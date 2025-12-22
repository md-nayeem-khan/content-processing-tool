# EditorCode Component Implementation

## Overview
Added support for the **EditorCode** component type, which is used for inline code snippets in Educative content.

## Component Structure

### Input JSON Format
```json
{
    "type": "EditorCode",
    "mode": "edit",
    "content": {
        "language": "javascript",
        "content": "deliverContent(origin_id, server_list, content_type, content_version, description)",
        "version": "1.0",
        "comp_id": "vWL41yBruScOCv_RqiKcL"
    },
    "iteration": 1,
    "status": "normal",
    "contentID": "mEwlqb9BvPGYY1TG6ea5r"
}
```

### Key Fields
- **type**: `"EditorCode"`
- **mode**: `"edit"` or `"view"` 
- **content.language**: Programming language (e.g., `"javascript"`, `"python"`, `"java"`)
- **content.content**: The actual code snippet
- **content.version**: Version information

## Implementation

### Function: `_process_editor_code()`
**Location**: `section_processor.py` (line ~1723)

```python
def _process_editor_code(self, component: Dict[str, Any]) -> str:
    """
    Process EditorCode components - renders inline code snippets
    
    Extracts:
    - content.language: Programming language
    - content.content: The actual code
    
    Returns:
        LaTeX code listing with proper formatting
    """
```

### Processing Flow

1. **Extract content** from `component["content"]["content"]`
2. **Get language** from `component["content"]["language"]`
3. **Map language** to LaTeX listings package format
4. **Generate LaTeX** using `\begin{lstlisting}[language=X]...\end{lstlisting}`

### Language Mapping
The function maps Educative language names to LaTeX listings package names:

| Educative | LaTeX Listings |
|-----------|----------------|
| javascript | JavaScript |
| python | Python |
| java | Java |
| cpp, c++ | C++ |
| sql | SQL |
| typescript | JavaScript |
| shell, bash | bash |
| json | JavaScript |
| yaml | Python |

## LaTeX Output Format

### With Language
```latex
\begin{lstlisting}[language=JavaScript]
deliverContent(origin_id, server_list, content_type, content_version, description)
\end{lstlisting}
```

### Without Language
```latex
\begin{lstlisting}
code content here
\end{lstlisting}
```

## Component Registration

Added to both processing methods:

### Async Processing (line ~220)
```python
elif component_type == "EditorCode":
    latex_content = self._process_editor_code(component)
    latex_parts.append(latex_content)
```

### Sync Processing (line ~318)
```python
elif component_type == "EditorCode":
    latex_content = self._process_editor_code(component)
    latex_parts.append(latex_content)
```

## Test Results

✅ All tests passed successfully

### Test Cases
1. **JavaScript function** - Single line code
2. **Python class** - Multi-line with indentation
3. **SQL query** - Database query with formatting
4. **C++ code** - Code with special characters

### Example Output
**Input (JavaScript):**
```javascript
deliverContent(origin_id, server_list, content_type, content_version, description)
```

**Output (LaTeX):**
```latex
\begin{lstlisting}[language=JavaScript]
deliverContent(origin_id, server_list, content_type, content_version, description)
\end{lstlisting}
```

## Usage in Section Processing

The EditorCode component is automatically processed when encountered in section components:

```python
section_data = {
    "components": [
        {
            "type": "SlateHTML",
            "content": {"html": "<p>Here's some code:</p>"}
        },
        {
            "type": "EditorCode",
            "content": {
                "language": "python",
                "content": "print('Hello, World!')"
            }
        }
    ]
}
```

## Files Modified
1. **section_processor.py**
   - Added `_process_editor_code()` function (line ~1723)
   - Added component handler in async processing (line ~220)
   - Added component handler in sync processing (line ~318)

## Test Files Created
1. **test_editor_code.py** - Unit tests for `_process_editor_code()`
2. **test_editor_code_section.py** - Integration test with full section
3. **test_editor_code_output.py** - Generate sample LaTeX output
4. **test_editor_code_output.tex** - Generated LaTeX examples

## Features
- ✅ Supports all major programming languages
- ✅ Preserves code formatting and indentation
- ✅ Compatible with LaTeX listings package
- ✅ Handles code with and without language specification
- ✅ Works in both async and sync processing modes
- ✅ Seamlessly integrates with existing component processing

## Related Components
- **Code** component: Used for larger code blocks with captions
- **EditorCode** component: Used for inline code snippets (this implementation)
