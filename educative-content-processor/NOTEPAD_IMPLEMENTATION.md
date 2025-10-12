# Notepad Component Support Implementation

## Overview
Added support for processing **Notepad** content type in the section processor. Notepad components are AI-assisted learning exercises used in Educative courses.

## Implementation Details

### What is Notepad?
Notepad is an interactive component where:
- **title**: Contains the question/prompt for the learner
- **systemPrompt**: Contains structured AI evaluation guidelines including a `REFERENCE ANSWER` section

### Processing Logic
The `_process_notepad()` method extracts:
1. **Question**: From the `content.title` field
2. **Reference Answer**: From the `# REFERENCE ANSWER` section in `content.systemPrompt`

### LaTeX Output Format
```latex
\textbf{Question:}

[Question text from title]

\textbf{Reference Answer:}

[Answer content from systemPrompt, converted from Markdown to LaTeX]
```

## Files Modified

### `section_processor.py`
1. **Added new method** `_process_notepad()` (lines 883-926)
   - Extracts question from `content.title`
   - Uses regex to extract REFERENCE ANSWER section from `content.systemPrompt`
   - Converts markdown answer to LaTeX using Pandoc
   - Properly escapes LaTeX special characters in the title

2. **Updated async processing** in `process_section_components_async()` (line 184-186)
   - Added Notepad case handler

3. **Updated sync processing** in `process_section_components()` (line 253-255)
   - Added Notepad case handler

## Example Input/Output

### Input (Backend Response)
```json
{
    "type": "Notepad",
    "content": {
        "title": "Sequence of steps to build large-scale distributed systems",
        "systemPrompt": "# REFERENCE ANSWER\nThe five steps in correct sequence are:\n1. Determine system requirements and constraints\n2. Recognize components\n3. Generate design\n4. Identify shortcomings in the initial design\n5. Discuss trade-offs and improve iteratively\n\n# ADDITIONAL TIPS\n..."
    }
}
```

### Output (LaTeX)
```latex
\textbf{Question:}

Sequence of steps to build large-scale distributed systems

\textbf{Reference Answer:}

The five steps in correct sequence are:

\begin{enumerate}
\def\labelenumi{\arabic{enumi}.}
\tightlist
\item
Determine system requirements and constraints
\item
Recognize components
\item
Generate design
\item
Identify shortcomings in the initial design
\item
Discuss trade-offs and improve iteratively
\end{enumerate}
```

## Testing
Created `test_notepad.py` to verify:
- Question extraction from title
- Reference answer extraction from systemPrompt
- Proper LaTeX formatting
- Special character escaping

Test results: **All assertions passed** ✓

## Technical Notes

### Regex Pattern
The implementation uses this regex to extract the REFERENCE ANSWER section:
```python
r'#\s*REFERENCE\s+ANSWER\s*\n(.+?)(?=\n#|$)'
```
- Matches `# REFERENCE ANSWER` with flexible whitespace
- Captures content until the next `#` section or end of string
- Case-insensitive matching

### Markdown List Formatting Fix
Before converting to LaTeX, the implementation ensures proper markdown formatting:
```python
# Add blank line before first numbered list item (required for Pandoc)
answer_text = re.sub(r'([^\n])\n(1\.\s)', r'\1\n\n\2', answer_text)
# Add blank line before first bulleted list item
answer_text = re.sub(r'([^\n])\n([*-]\s[^\n])', r'\1\n\n\2', answer_text, count=1)
```

This is critical because Pandoc requires a blank line before a list to recognize it as a proper list structure. Without this, numbered items are treated as inline text.

### Character Escaping
- Question title: Uses `_escape_latex()` for proper LaTeX escaping
- Answer content: Uses `_markdown_to_latex_pandoc()` for Markdown-to-LaTeX conversion with proper list formatting

## Integration
The Notepad processor is now fully integrated into both:
- **Async workflow**: `process_section_components_async()`
- **Sync workflow**: `process_section_components()` (legacy)

Both workflows will automatically detect and process Notepad components when encountered in course content.
