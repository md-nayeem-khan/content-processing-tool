# LaTeX Component Implementation

## Overview
The system now supports the `Latex` component type from the Educative backend. This component is used to render mathematical equations and formulas.

## Backend Response Structure

```json
{
    "type": "Latex",
    "mode": "edit",
    "content": {
        "version": "1.0",
        "text": "CPU_{time\\ per\\ program} = Instruction_{per\\ program} \\times CPI \\times CPU_{time\\ per\\ clock\\ cycle}",
        "mdhtml": "<span class=\"katex-display\">...</span>",
        "isEquationValid": true,
        "comp_id": "ZhxqdoQ7L8-J9KfNG_xGX"
    },
    "iteration": 0,
    "hash": 13,
    "status": "normal",
    "contentID": "zayKkgpQ99O_WydaEPr5A",
    "widgetCopyId": "6012425262465024",
    "children": [{"text": ""}]
}
```

## Implementation Details

### Key Fields
- **`type`**: "Latex" - Identifies this as a LaTeX equation component
- **`content.text`**: The raw LaTeX equation text (this is what we use)
- **`content.mdhtml`**: HTML rendering using KaTeX (not used for LaTeX output)
- **`content.mode`**: "edit" or "display" mode (currently not affecting output)
- **`content.isEquationValid`**: Boolean indicating if the equation is valid

### Processing Logic

The `_process_latex()` method in `section_processor.py`:

1. **Extracts** the LaTeX equation text from `content.text`
2. **Checks** if the equation is already wrapped in math delimiters:
   - Display math: `$$...$$` or `\[...\]`
   - Inline math: `$...$`
3. **Wraps** unwrapped equations in display math environment `\[...\]`
4. **Returns** the properly formatted LaTeX

### LaTeX Output Format

For unwrapped equations:
```latex
\[
CPU_{time\ per\ program} = Instruction_{per\ program} \times CPI \times CPU_{time\ per\ clock\ cycle}
\]
```

For already wrapped equations (preserved as-is):
```latex
$$E = mc^2$$
```

or

```latex
$x^2 + y^2 = z^2$
```

## Code Changes

### Modified Files
- **`section_processor.py`**:
  - Added `elif component_type == "Latex":` handling in both async and sync processing methods
  - Added `_process_latex()` method to handle LaTeX component processing

### Method Signature
```python
def _process_latex(self, component: Dict[str, Any]) -> str:
    """
    Process Latex components - renders mathematical equations
    
    The backend provides:
    - content.text: Raw LaTeX equation text
    - content.mdhtml: HTML rendering (not used for LaTeX output)
    - content.mode: 'edit' or 'display' mode
    
    Returns:
        LaTeX equation wrapped in appropriate math environment
    """
```

## Testing

### Test Files
- **`test_latex_component.py`**: Comprehensive test with multiple scenarios
- **`test_latex_simple.py`**: Simple verification test

### Test Scenarios
1. ✅ Unwrapped equation (gets wrapped in `\[...\]`)
2. ✅ Already wrapped display math (`$$...$$` preserved)
3. ✅ Inline math (`$...$` preserved)

### Running Tests
```bash
python test_latex_simple.py
python test_latex_component.py
```

## Usage Example

```python
from section_processor import SectionContentProcessor

processor = SectionContentProcessor()
processor.set_book_context("my_book", chapter_number=1)

section_data = {
    "components": [
        {
            "type": "Latex",
            "content": {
                "text": "E = mc^2"
            }
        }
    ]
}

latex_output, images, types = processor.process_section_components(section_data)
print(latex_output)
# Output: \[
#         E = mc^2
#         \]
```

## Integration Points

The Latex component handler integrates seamlessly with:
- **Async processing**: `process_section_components_async()`
- **Sync processing**: `process_section_components()`
- **Component type detection**: Automatically added to `component_types` list
- **Error handling**: Wrapped in try-except like other components

## Math Environment Choice

We use `\[...\]` for display equations because:
- ✅ Unnumbered equations (most common use case)
- ✅ Standard LaTeX syntax
- ✅ Compatible with most LaTeX processors
- ✅ Cleaner than `$$...$$` (which is TeX syntax, not LaTeX)

For numbered equations, users can wrap their content in `\begin{equation}...\end{equation}` in the backend.

## Future Enhancements

Potential improvements:
1. Support for `content.mode` to distinguish inline vs display math
2. Validation of LaTeX syntax before processing
3. Support for equation numbering based on backend flags
4. Custom math environment selection (equation, align, etc.)

## Notes

- The `mdhtml` field contains KaTeX-rendered HTML, which we ignore for LaTeX output
- LaTeX equations are passed through without escaping special characters
- Empty or missing `content.text` returns an empty string
- The component integrates with the existing error handling framework
