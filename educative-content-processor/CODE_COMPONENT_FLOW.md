# Code Component Processing Flow

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Educative Backend API                        │
│                                                                  │
│  {                                                               │
│    "type": "Code",                                              │
│    "content": {                                                 │
│      "caption": "Description",                                  │
│      "language": "python",                                      │
│      "content": "code here..."                                  │
│    }                                                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Section Content Processor                           │
│                                                                  │
│  process_section_components() / _async()                        │
│         │                                                        │
│         ├─► Detect component_type == "Code"                     │
│         │                                                        │
│         └─► Call _process_code(component)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    _process_code() Method                        │
│                                                                  │
│  1. Extract data:                                               │
│     - code_text = content.get("content")                        │
│     - language = content.get("language")                        │
│     - caption = content.get("caption")                          │
│                                                                  │
│  2. Map language:                                               │
│     - "python" → "Python"                                       │
│     - "javascript" → "JavaScript"                               │
│     - "shell" → "bash"                                          │
│     - etc.                                                      │
│                                                                  │
│  3. Escape caption:                                             │
│     - _escape_latex(caption)                                    │
│                                                                  │
│  4. Build LaTeX:                                                │
│     - \textbf{caption}                                          │
│     - \begin{lstlisting}[language=X]                            │
│     - code content                                              │
│     - \end{lstlisting}                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LaTeX Output                                │
│                                                                  │
│  \textbf{Python Hello World}                                    │
│                                                                  │
│  \begin{lstlisting}[language=Python]                            │
│  def hello():                                                   │
│      print('Hello, World!')                                     │
│  \end{lstlisting}                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LaTeX Compilation                               │
│                                                                  │
│  Uses amd.sty with:                                             │
│  - \RequirePackage{listings}                                    │
│  - \lstset{...} configuration                                   │
│                                                                  │
│  Renders with:                                                  │
│  - Syntax highlighting                                          │
│  - Line numbers                                                 │
│  - Frame border                                                 │
│  - Proper spacing                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        PDF Output                                │
│                                                                  │
│  ┌───────────────────────────────────────────────────────┐     │
│  │ Python Hello World                                     │     │
│  │                                                        │     │
│  │  1  def hello():                                       │     │
│  │  2      print('Hello, World!')                         │     │
│  │                                                        │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                  │
│  (with syntax highlighting colors)                              │
└─────────────────────────────────────────────────────────────────┘
```

## Component Interaction

```
┌──────────────────┐
│  SlateHTML       │
│  MarkdownEditor  │
│  DrawIOWidget    │
│  StructuredQuiz  │
│  Columns         │
│  MarkMap         │
│  SpoilerEditor   │
│  Notepad         │
│  Table           │
│  Latex           │
│  Code            │◄─── NEW!
└──────────────────┘
         │
         ▼
┌──────────────────┐
│ Component Router │
│  (if/elif chain) │
└──────────────────┘
         │
         ▼
┌──────────────────┐
│ Specific Handler │
│ (_process_code)  │
└──────────────────┘
         │
         ▼
┌──────────────────┐
│ LaTeX Generator  │
└──────────────────┘
```

## Language Mapping Flow

```
Backend Language → Language Map → LaTeX Language
─────────────────────────────────────────────────
"python"        →  language_map  →  "Python"
"javascript"    →  language_map  →  "JavaScript"
"shell"         →  language_map  →  "bash"
"cpp"           →  language_map  →  "C++"
"sql"           →  language_map  →  "SQL"
"unknown"       →  language_map  →  "unknown" (fallback)
```

## Error Handling Flow

```
┌─────────────────┐
│ Code Component  │
└─────────────────┘
        │
        ▼
┌─────────────────┐
│ Extract Content │
└─────────────────┘
        │
        ├─► No code_text? → Return ""
        │
        ├─► No language?  → Use plain lstlisting
        │
        ├─► No caption?   → Skip caption line
        │
        └─► All good      → Generate full output
```

## Data Flow Example

### Step 1: Backend JSON
```json
{
  "type": "Code",
  "content": {
    "caption": "HAProxy Config",
    "language": "shell",
    "content": "mode HTTP\nacl app path_end -i /api"
  }
}
```

### Step 2: Component Detection
```python
component_type = component.get("type")  # "Code"
if component_type == "Code":
    latex_content = self._process_code(component)
```

### Step 3: Data Extraction
```python
content = component.get("content", {})
code_text = content.get("content", "")      # "mode HTTP\nacl..."
language = content.get("language", "")      # "shell"
caption = content.get("caption", "")        # "HAProxy Config"
```

### Step 4: Language Mapping
```python
language_map = {"shell": "bash", ...}
listings_language = language_map.get("shell")  # "bash"
```

### Step 5: LaTeX Generation
```python
result = [
    "\\textbf{HAProxy Config}",
    "",
    "\\begin{lstlisting}[language=bash]",
    "mode HTTP\nacl app path_end -i /api",
    "\\end{lstlisting}"
]
return '\n'.join(result)
```

### Step 6: Final Output
```latex
\textbf{HAProxy Config}

\begin{lstlisting}[language=bash]
mode HTTP
acl app path_end -i /api
\end{lstlisting}
```

## Integration Points

### File: `section_processor.py`

```python
# Line 196-198: Async integration
elif component_type == "Code":
    latex_content = self._process_code(component)
    latex_parts.append(latex_content)

# Line 273-275: Sync integration
elif component_type == "Code":
    latex_content = self._process_code(component)
    latex_parts.append(latex_content)

# Line 1093-1177: Handler implementation
def _process_code(self, component: Dict[str, Any]) -> str:
    # Implementation here
```

### File: `amd.sty`

```latex
% Line 20: Package import
\RequirePackage{listings}

% Lines 25-48: Configuration
\lstset{
    basicstyle=\ttfamily\small,
    breaklines=true,
    frame=single,
    numbers=left,
    % ... more settings
}
```

## Performance Characteristics

```
Operation          Time Complexity    Space Complexity
─────────────────────────────────────────────────────
Extract data       O(1)               O(1)
Map language       O(1)               O(1)
Escape caption     O(n)               O(n)
Build LaTeX        O(n)               O(n)
─────────────────────────────────────────────────────
Total              O(n)               O(n)

where n = length of code content
```

## Testing Flow

```
Test Script
    │
    ├─► Create Code component
    │
    ├─► Initialize processor
    │
    ├─► Process component
    │
    ├─► Verify output
    │   ├─► Check component type
    │   ├─► Check lstlisting presence
    │   ├─► Check caption
    │   └─► Check code content
    │
    └─► Save to file
```

## Summary

The Code component flows through the system in a clean, linear fashion:
1. **Input**: JSON from backend
2. **Detection**: Component type routing
3. **Processing**: Language mapping and LaTeX generation
4. **Output**: Formatted lstlisting environment
5. **Rendering**: LaTeX compilation to PDF

The implementation is **simple, efficient, and maintainable**.
