# Table Component Processing Documentation

## Overview

The system now efficiently supports the **Table** type content from Educative's backend API. Tables are converted to LaTeX `tabular` environments with proper formatting, alignment, and styling.

## Backend Response Structure

The Table component from the backend has the following structure:

```json
{
    "type": "Table",
    "mode": "view",
    "content": {
        "version": "2.0",
        "numberOfRows": 10,
        "numberOfColumns": 2,
        "columnWidths": [272, 517],
        "data": [
            ["<p>Cell 1</p>", "<p>Cell 2</p>"],
            ["<p>Cell 3</p>", "<p>Cell 4</p>"]
        ],
        "template": 1,
        "title": "Optional Table Title",
        "titleAlignment": "align-center"
    }
}
```

### Key Fields

- **numberOfRows**: Total number of rows in the table
- **numberOfColumns**: Total number of columns in the table
- **columnWidths**: Array of column widths (for reference, not used in LaTeX conversion)
- **data**: 2D array where each cell contains HTML content (typically `<p>` tags with text)
- **template**: Table style template (1 = header row style with double line separator)
- **title**: Optional table title/caption
- **titleAlignment**: Alignment for the title (e.g., "align-center")

## Implementation Details

### Processing Flow

1. **Component Detection**: The `process_section_components_async()` and `process_section_components()` methods detect `Table` type components
2. **Table Processing**: The `_process_table()` method converts the table data to LaTeX
3. **Cell Processing**: Each cell's HTML content is processed by `_process_table_cell()`
4. **LaTeX Generation**: Generates proper LaTeX `table` and `tabular` environments

### Features

#### 1. **Automatic Column Specification**
- Left-aligned columns with borders: `|l|l|l|`
- Adjusts automatically based on `numberOfColumns`

#### 2. **Header Row Handling**
- When `template=1`, the first row is treated as a header
- Double horizontal line (`\hline\hline`) after header row
- Single horizontal line after other rows

#### 3. **HTML Content Processing**
- Uses **Pandoc** for HTML to LaTeX conversion (when available)
- Fallback to manual HTML processing if Pandoc is unavailable
- Supports:
  - Paragraph tags with alignment classes (`ql-align-center`, `ql-align-right`)
  - Text formatting: `<strong>`, `<b>`, `<em>`, `<i>`, `<code>`
  - Nested HTML structures

#### 4. **LaTeX Special Character Escaping**
- Smart escaping that preserves LaTeX commands
- Escapes: `&`, `%`, `$`, `#`, `_`
- Uses `_escape_latex_in_text()` method to avoid breaking LaTeX commands

#### 5. **Table Styling**
- `\small` font size for better fit
- Centered table placement
- Optional title displayed above and as caption below
- Bordered cells with `\hline` separators

### Generated LaTeX Structure

```latex
\textbf{Table Title}

\begin{table}[htbp]
\centering
\small
\begin{tabular}{|l|l|}
\hline
Header 1 & Header 2 \\
\hline
\hline
Row 1 Col 1 & Row 1 Col 2 \\
\hline
Row 2 Col 1 & Row 2 Col 2 \\
\hline
\end{tabular}
\caption{Table Title}
\end{table}
```

## Methods Added

### `_process_table(component: Dict[str, Any]) -> str`

Main method that processes Table components and converts them to LaTeX.

**Parameters:**
- `component`: Dictionary containing the Table component data

**Returns:**
- String containing LaTeX table code

**Features:**
- Extracts table metadata (rows, columns, data, title, template)
- Generates column specification
- Processes each cell with HTML content
- Adds proper horizontal lines and separators
- Handles header rows with double lines

### `_process_table_cell(cell_html: str) -> str`

Processes individual table cell HTML content to LaTeX.

**Parameters:**
- `cell_html`: HTML string from a table cell

**Returns:**
- String containing LaTeX-formatted cell content

**Features:**
- Uses Pandoc for HTML conversion (preferred)
- Fallback to manual HTML processing
- Removes paragraph breaks (tables don't support `\n\n`)
- Cleans up excessive whitespace
- Preserves text formatting (bold, italic, code)

### `_escape_latex_in_text(text: str) -> str`

Smart LaTeX character escaping that preserves existing LaTeX commands.

**Parameters:**
- `text`: Text string that may contain LaTeX commands

**Returns:**
- String with special characters escaped but LaTeX commands preserved

**Features:**
- Splits text by LaTeX commands
- Escapes only non-command text
- Preserves `\textbf{}`, `\textit{}`, `\centering`, etc.

## Usage Example

```python
import asyncio
from section_processor import SectionContentProcessor

# Sample table component
table_component = {
    "type": "Table",
    "content": {
        "numberOfRows": 2,
        "numberOfColumns": 2,
        "data": [
            ["<p>Name</p>", "<p>Value</p>"],
            ["<p>Item 1</p>", "<p>100</p>"]
        ],
        "template": 1,
        "title": "Sample Data"
    }
}

# Process the table
async def process_table():
    processor = SectionContentProcessor()
    processor.set_book_context("my_book", chapter_number=1, section_id="section1")
    
    section_data = {"components": [table_component]}
    latex_content, images, types = await processor.process_section_components_async(section_data)
    
    print(latex_content)

asyncio.run(process_table())
```

## Testing

Two test files are provided:

### 1. `test_table_simple.py`
Simple test with a small 3x2 table to verify basic functionality.

```bash
python test_table_simple.py
```

### 2. `test_table_processing.py`
Comprehensive test with the full 10x2 table from the backend response example.

```bash
python test_table_processing.py
```

Both tests verify:
- ✅ Table environment generation
- ✅ Tabular environment generation
- ✅ Header row processing
- ✅ Data row processing
- ✅ Column separators (`&`)
- ✅ Row separators (`\\`)
- ✅ Horizontal lines (`\hline`)

## Performance Considerations

### Efficiency Features

1. **Lazy Pandoc Import**: Pandoc is only imported when needed
2. **Fallback Processing**: If Pandoc fails, manual HTML processing is used
3. **Smart Escaping**: Only escapes characters that need escaping
4. **Minimal Regex**: Uses efficient regex patterns for HTML processing
5. **Single Pass Processing**: Each cell is processed once

### Memory Efficiency

- Processes cells one at a time (not loading entire table into memory)
- Uses string concatenation with `join()` for efficiency
- No unnecessary data copying

### Time Complexity

- **O(n × m)** where n = rows, m = columns
- Each cell is processed independently
- No nested loops beyond the table dimensions

## Edge Cases Handled

1. **Empty Tables**: Returns `\textit{Empty table}` if no data
2. **Missing Title**: Works without title/caption
3. **HTML Entities**: Properly converts HTML entities (e.g., `&rsquo;` → `'`)
4. **Nested HTML**: Handles complex nested HTML structures
5. **Special Characters**: Escapes LaTeX special characters correctly
6. **Alignment Classes**: Processes `ql-align-center` and `ql-align-right` classes

## Future Enhancements

Possible improvements for future versions:

1. **Column Width Control**: Use `columnWidths` to set LaTeX column widths
2. **Cell Merging**: Support for `mergeInfo` to merge cells
3. **Custom Styles**: Process `customStyles` for cell-specific formatting
4. **Responsive Tables**: Use `longtable` for tables that span multiple pages
5. **Advanced Alignment**: Support for more alignment options (center, right)

## Compatibility

- ✅ Works with both async and sync processing methods
- ✅ Compatible with existing component processors
- ✅ Integrates with Pandoc when available
- ✅ Fallback mode for environments without Pandoc
- ✅ Supports all existing LaTeX templates

## Dependencies

- **Required**: None (fallback mode works without dependencies)
- **Optional**: `pypandoc` (for better HTML conversion)

## Error Handling

The implementation includes robust error handling:

```python
try:
    if component_type == "Table":
        latex_content = self._process_table(component)
        latex_parts.append(latex_content)
except Exception as e:
    latex_parts.append(f"\\textit{{Error processing {component_type}: {str(e)}}}")
```

Errors are caught and displayed as italic text in the output, ensuring the document generation continues even if a table fails to process.
