# Code Syntax Highlighting Colors

## Color Scheme

The code listings now feature professional syntax highlighting with the following color scheme:

### Color Definitions

| Element | Color Name | RGB Value | Hex | Visual |
|---------|-----------|-----------|-----|--------|
| **Keywords** | Code Blue | (0.13, 0.29, 0.53) | #21496F | 🔵 Dark Blue |
| **Keywords (Alt)** | Code Purple | (0.58, 0, 0.82) | #9400D1 | 🟣 Purple |
| **Comments** | Code Green | (0, 0.6, 0) | #009900 | 🟢 Green |
| **Strings** | Code Orange | (0.8, 0.4, 0) | #CC6600 | 🟠 Orange |
| **Numbers** | Code Gray | (0.5, 0.5, 0.5) | #808080 | ⚫ Gray |
| **Background** | Back Colour | (0.97, 0.97, 0.97) | #F7F7F7 | ⬜ Light Gray |
| **Frame** | Black 30% | - | - | ⬛ Light Border |

## Syntax Element Styling

### Keywords (Blue, Bold)
- Language keywords: `def`, `class`, `if`, `for`, `while`, `return`, etc.
- Control flow: `break`, `continue`, `try`, `except`, `finally`
- Type declarations: `int`, `void`, `public`, `private`, `static`
- **Style**: Bold, Dark Blue (#21496F)

### Secondary Keywords (Purple, Bold)
- Built-in functions and special keywords
- Module/import keywords: `import`, `from`, `package`
- Special identifiers
- **Style**: Bold, Purple (#9400D1)

### Comments (Green, Italic)
- Single-line comments: `//`, `#`, `--`
- Multi-line comments: `/* */`, `""" """`
- Documentation strings
- **Style**: Italic, Green (#009900)

### Strings (Orange)
- Single-quoted strings: `'text'`
- Double-quoted strings: `"text"`
- Template literals: `` `text` ``
- **Style**: Regular, Orange (#CC6600)

### Line Numbers (Gray)
- Left margin line numbers
- **Style**: Tiny, Gray (#808080)

### Background
- Light gray background for better readability
- **Color**: Very Light Gray (#F7F7F7)

## Example Output

### Python Code
```python
# This is a comment (GREEN, italic)
def hello_world():  # 'def' is BLUE bold, 'hello_world' is black
    """Docstring""" # String is ORANGE
    print('Hello!')  # 'print' is BLUE bold, 'Hello!' is ORANGE
    return 42        # 'return' is BLUE bold, 42 is black
```

**Rendered colors:**
- `#` comment → 🟢 Green italic
- `def`, `return` → 🔵 Blue bold
- `'Hello!'`, `"""Docstring"""` → 🟠 Orange
- `hello_world`, `42` → ⚫ Black

### JavaScript Code
```javascript
// Comment (GREEN, italic)
function greet(name) {  // 'function' is BLUE bold
    const message = `Hello, ${name}!`;  // 'const' is BLUE bold, string is ORANGE
    return message;  // 'return' is BLUE bold
}
```

**Rendered colors:**
- `//` comment → 🟢 Green italic
- `function`, `const`, `return` → 🔵 Blue bold
- `` `Hello, ${name}!` `` → 🟠 Orange
- `greet`, `name`, `message` → ⚫ Black

### Java Code
```java
/* Multi-line comment (GREEN, italic) */
public class Main {  // 'public', 'class' are BLUE bold
    public static void main(String[] args) {
        System.out.println("Hello!");  // String is ORANGE
    }
}
```

**Rendered colors:**
- `/* */` comment → 🟢 Green italic
- `public`, `class`, `static`, `void` → 🔵 Blue bold
- `"Hello!"` → 🟠 Orange
- `Main`, `System`, `args` → ⚫ Black

## Configuration Details

### LaTeX Configuration (amd.sty)

```latex
% Color definitions
\definecolor{codegreen}{rgb}{0,0.6,0}      % Comments
\definecolor{codegray}{rgb}{0.5,0.5,0.5}   % Line numbers
\definecolor{codepurple}{rgb}{0.58,0,0.82} % Alt keywords
\definecolor{codeblue}{rgb}{0.13,0.29,0.53}% Keywords
\definecolor{codeorange}{rgb}{0.8,0.4,0}   % Strings
\definecolor{backcolour}{rgb}{0.97,0.97,0.97} % Background

% Syntax highlighting settings
\lstset{
    keywordstyle=\color{codeblue}\bfseries,      % Keywords: blue, bold
    keywordstyle=[2]\color{codepurple}\bfseries, % Alt keywords: purple, bold
    commentstyle=\color{codegreen}\itshape,      % Comments: green, italic
    stringstyle=\color{codeorange},              % Strings: orange
    identifierstyle=\color{black},               % Identifiers: black
    numberstyle=\tiny\color{codegray},           % Line numbers: gray
    backgroundcolor=\color{backcolour},          % Background: light gray
    rulecolor=\color{black!30}                   % Frame: light border
}
```

## Visual Comparison

### Before (No Colors)
```
1  import logging as log
2  log.basicConfig(level=log.DEBUG)
3  for i in range(6):
4      if i == 0:
5          log.debug('Debug level')
```
*All text in black, no distinction between keywords and strings*

### After (With Colors)
```
1  import logging as log          # 'import' and 'as' in BLUE
2  log.basicConfig(level=log.DEBUG)
3  for i in range(6):              # 'for' and 'in' in BLUE
4      if i == 0:                  # 'if' in BLUE
5          log.debug('Debug level') # 'Debug level' in ORANGE
```
*Keywords in blue, strings in orange, better visual hierarchy*

## Benefits

1. **Better Readability** - Colors help distinguish code elements
2. **Professional Appearance** - Modern syntax highlighting
3. **Visual Hierarchy** - Important keywords stand out
4. **Reduced Eye Strain** - Light background with good contrast
5. **Language Recognition** - Consistent colors across languages

## Customization

To change colors, edit `templates/book-template/amd.sty`:

```latex
% Modify these RGB values (0-1 range)
\definecolor{codeblue}{rgb}{0.13,0.29,0.53}  % Change keyword color
\definecolor{codeorange}{rgb}{0.8,0.4,0}     % Change string color
\definecolor{codegreen}{rgb}{0,0.6,0}        % Change comment color
```

## Supported Languages

All 20+ supported languages benefit from syntax highlighting:
- Python, JavaScript, Java, C++, C, C#
- Go, Rust, PHP, Ruby, Swift, Kotlin
- SQL, HTML, CSS, XML, JSON
- Bash, Shell, YAML, Dockerfile, Markdown

Each language's keywords are automatically highlighted according to the listings package language definitions.
