# Chart Component - Quick Reference

## What It Does

Converts Chart.js charts from Educative platform into LaTeX tables for PDF generation.

## Backend Response Format

```json
{
  "type": "Chart",
  "content": {
    "config": "{...JSON...}",
    "caption": "Chart description"
  }
}
```

## Conversion Example

### Input: Line Chart
```
Labels: 2012, 2013, 2014
Data: 0.8, 1.0, 1.1
Title: "User Growth"
```

### Output: LaTeX Table
```latex
\begin{table}[htbp]
\centering
\begin{tabular}{|p{...}|p{...}|}
\hline
\textbf{Year} & \textbf{Users} \\
\hline
2012 & 0.8 \\
2013 & 1.0 \\
2014 & 1.1 \\
\hline
\end{tabular}
\caption{User Growth}
\end{table}
```

## Key Features

- ✅ Preserves all data points
- ✅ Supports multiple datasets (multi-column tables)
- ✅ Includes chart title and caption
- ✅ Shows axis labels
- ✅ Auto-adjusts column widths
- ✅ Adds conversion note: "[Chart data presented in table format]"

## Testing

```bash
# Quick test
python test_chart_component.py

# Generate sample LaTeX
python test_chart_output.py
```

## Implementation Location

- **File**: `section_processor.py`
- **Method**: `_process_chart(component)`
- **Lines**: 1160-1289

## Supported Chart Types

All chart types → Table format:
- Line charts
- Bar charts
- Area charts
- Pie charts
- Multi-dataset charts

## Example Use Cases

1. **Single dataset**: Time series data → 2-column table
2. **Multiple datasets**: Comparison data → Multi-column table
3. **With units**: Axis labels shown in table note

## Notes

- Charts cannot be rendered visually in LaTeX PDFs without complex libraries
- Table format preserves all data while being PDF-friendly
- Colors and interactivity are not preserved
