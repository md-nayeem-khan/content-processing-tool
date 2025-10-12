# LaTeX Component - Quick Reference

## What It Does
Processes mathematical equations from Educative's `Latex` component type and converts them to proper LaTeX math environments.

## Backend Structure
```json
{
    "type": "Latex",
    "content": {
        "text": "E = mc^2",           // ← We use this
        "mdhtml": "...",               // ← Ignored (HTML rendering)
        "mode": "edit"                 // ← Currently not used
    }
}
```

## Output Examples

### Input (unwrapped)
```json
{
    "type": "Latex",
    "content": {
        "text": "E = mc^2"
    }
}
```

### Output
```latex
\[
E = mc^2
\]
```

### Input (already wrapped - preserved)
```json
{
    "type": "Latex",
    "content": {
        "text": "$$E = mc^2$$"
    }
}
```

### Output
```latex
$$E = mc^2$$
```

## Supported Math Delimiters
- **Display math**: `\[...\]` or `$$...$$` (preserved as-is)
- **Inline math**: `$...$` (preserved as-is)
- **Unwrapped**: Automatically wrapped in `\[...\]`

## Testing
```bash
# Quick test
python test_latex_simple.py

# Comprehensive test
python test_latex_component.py
```

## Implementation Location
- **File**: `section_processor.py`
- **Method**: `_process_latex()`
- **Lines**: Added to both async (line ~192) and sync (line ~269) processing loops

## Status
✅ **Fully Implemented** - Ready for production use
