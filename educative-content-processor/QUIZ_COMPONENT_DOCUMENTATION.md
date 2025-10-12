# Quiz Component Documentation

## Overview

The Quiz component processor handles multiple-choice quiz questions from Educative content and converts them to well-formatted LaTeX output suitable for PDF generation.

## Component Type

**Type:** `Quiz`

## Backend Response Structure

```json
{
    "type": "Quiz",
    "mode": "edit",
    "content": {
        "questions": [
            {
                "questionText": "Question text in plain format",
                "questionTextHtml": "<p>Question text in HTML format</p>",
                "questionOptions": [
                    {
                        "text": "Option text",
                        "mdHtml": "<p>Option text in HTML</p>",
                        "id": "unique-option-id",
                        "correct": true,
                        "explanation": {
                            "mdText": "Explanation text",
                            "mdHtml": "<p>Explanation in HTML</p>"
                        }
                    }
                ],
                "multipleAnswers": false,
                "id": "unique-question-id"
            }
        ],
        "comp_id": "component-id",
        "title": "Quiz Title",
        "titleMdHtml": ""
    }
}
```

## Features

### 1. Question Processing
- Converts HTML question text to LaTeX using Pandoc
- Falls back to plain text if HTML is not available
- Supports numbered questions (Question 1, Question 2, etc.)

### 2. Multiple Choice Options
- Displays all answer options as itemized list
- Marks correct answers with **[CORRECT]** label
- Converts HTML option text to LaTeX

### 3. Multiple Answer Support
- Detects `multipleAnswers: true` flag
- Adds "(Select all that apply.)" hint for multi-select questions
- Properly marks all correct answers

### 4. Explanations
- Shows explanations for correct answers
- Converts HTML explanations to LaTeX
- Only displays explanations when provided (non-empty)

### 5. Quiz Title
- Displays custom quiz title if provided
- Falls back to "Quiz" if no title specified
- Rendered as `\subsection*{}`

## LaTeX Output Structure

```latex
\subsection*{Quiz Title}
\vspace{0.3cm}
\noindent
\textbf{Question 1:} Question text here?
\\[0.2cm]
\begin{itemize}
    \item \textbf{[CORRECT]} Correct option
\\[0.1cm]
\textit{Explanation:} 
Explanation text for correct answer.
    \item Incorrect option 1
    \item Incorrect option 2
\end{itemize}
\vspace{0.3cm}
\noindent
\textbf{Question 2:} Another question?
\\
\textit{(Select all that apply.)}
\\[0.2cm]
\begin{itemize}
    \item \textbf{[CORRECT]} First correct option
\\[0.1cm]
\textit{Explanation:} 
Explanation for first correct answer.
    \item Incorrect option
    \item \textbf{[CORRECT]} Second correct option
\\[0.1cm]
\textit{Explanation:} 
Explanation for second correct answer.
\end{itemize}
```

## Implementation Details

### Method: `_process_quiz(component: Dict[str, Any]) -> str`

**Location:** `section_processor.py`

**Process Flow:**
1. Extract quiz content and questions array
2. Add quiz title (custom or default "Quiz")
3. For each question:
   - Convert question text from HTML to LaTeX
   - Add multiple-answer hint if applicable
   - Process each answer option:
     - Convert option text from HTML to LaTeX
     - Mark correct answers with [CORRECT]
     - Add explanation if provided
4. Return formatted LaTeX string

### HTML to LaTeX Conversion

The processor uses `_html_to_latex_pandoc()` method to convert:
- Question text HTML → LaTeX
- Option text HTML → LaTeX  
- Explanation HTML → LaTeX

This ensures proper formatting of:
- Bold text (`<strong>` → `\textbf{}`)
- Italic text (`<em>` → `\textit{}`)
- Code snippets (`<code>` → `\texttt{}`)
- Special characters (escaped properly)

## Usage Example

```python
from section_processor import SectionContentProcessor

# Initialize processor
processor = SectionContentProcessor(output_dir="generated_books")
processor.set_book_context("my-book", chapter_number=1, section_id="quiz-section")

# Quiz component data
quiz_component = {
    "type": "Quiz",
    "content": {
        "questions": [...],
        "title": "Chapter Quiz"
    }
}

# Process quiz
latex_output = processor._process_quiz(quiz_component)
```

## Integration

The Quiz component is automatically processed when encountered in section components:

### Async Processing
```python
elif component_type == "Quiz":
    latex_content = self._process_quiz(component)
    latex_parts.append(latex_content)
```

### Sync Processing (Legacy)
```python
elif component_type == "Quiz":
    latex_content = self._process_quiz(component)
    latex_parts.append(latex_content)
```

## Testing

### Test File: `test_quiz_processor.py`

Run the test:
```bash
python test_quiz_processor.py
```

### Compilation Test: `test_quiz_compilation.py`

Generate a full LaTeX document with quiz:
```bash
python test_quiz_compilation.py
```

Compile the generated document:
```bash
pdflatex test_quiz_compile.tex
```

## LaTeX Requirements

The Quiz component requires these LaTeX packages (already included in standard templates):
- `inputenc` - UTF-8 encoding support
- `fontenc` - Font encoding
- Standard itemize environment (built-in)

## Styling Customization

To customize quiz appearance, modify the following in `_process_quiz()`:

### Question Spacing
```python
latex_parts.append("\\vspace{0.3cm}")  # Adjust spacing between questions
```

### Option Spacing
```python
latex_parts.append("\\\\[0.2cm]")  # Adjust spacing before options
```

### Explanation Spacing
```python
latex_parts.append("\\\\[0.1cm]")  # Adjust spacing before explanation
```

### Correct Answer Marker
```python
latex_parts.append(f"    \\item \\textbf{{[CORRECT]}} {opt_latex.strip()}")
# Change [CORRECT] to any other marker (e.g., ✓, ✔, ANSWER)
```

## Known Limitations

1. **Images in Questions:** Currently, images embedded in question/option HTML are not extracted. Only text content is processed.

2. **Complex HTML:** Very complex HTML structures in questions may not convert perfectly. The Pandoc converter handles most common cases.

3. **Answer Randomization:** The LaTeX output shows answers in the order provided by the backend. No randomization is applied.

4. **Interactive Elements:** This is a static PDF output, so interactive quiz features (clicking, scoring) are not supported.

## Future Enhancements

Potential improvements for the Quiz component:

1. **Answer Key Section:** Generate a separate answer key at the end of the chapter
2. **Hide Answers Option:** Add flag to hide correct answers and explanations
3. **Score Calculation:** Add metadata for total points/scoring
4. **Question Categories:** Support for categorizing questions by topic
5. **Difficulty Levels:** Display difficulty indicators (Easy, Medium, Hard)
6. **Image Support:** Extract and display images in questions/options
7. **Custom Styling:** Support for custom quiz box styling with colors/borders

## Related Components

- **StructuredQuiz:** Legacy quiz format with simpler question/answer structure
- **Table:** For displaying quiz results or comparison tables
- **SpoilerEditor:** For hiding answers until revealed

## Version History

- **v1.0** (2025-10-11): Initial implementation with full support for:
  - Multiple-choice questions
  - Multiple-answer questions
  - Explanations
  - HTML to LaTeX conversion
  - Custom quiz titles
