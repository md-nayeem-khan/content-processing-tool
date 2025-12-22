"""
Section Content Processor for Markdown Content
Handles conversion of Markdown to LaTeX using Pandoc (REQUIRED)

Note: Pandoc must be installed on the system for this module to work.
Visit https://pandoc.org/installing.html for installation instructions.
"""

import re
from pathlib import Path
from typing import Optional

# Lazy import flag
PANDOC_AVAILABLE = None

def _lazy_import_pypandoc():
    """Lazy import pypandoc only when needed"""
    global PANDOC_AVAILABLE
    if PANDOC_AVAILABLE is None:
        try:
            import pypandoc
            PANDOC_AVAILABLE = True
        except ImportError:
            PANDOC_AVAILABLE = False
    return PANDOC_AVAILABLE

class MarkdownProcessor:
    """Process Markdown content and convert to LaTeX"""
    
    def __init__(self, output_dir: str = "generated_books"):
        self.output_dir = Path(output_dir)
        
    def markdown_to_latex(self, markdown_content: str, use_pandoc: bool = True) -> str:
        """
        Convert markdown content to LaTeX using Pandoc (REQUIRED)
        
        Args:
            markdown_content: Raw markdown content
            use_pandoc: Whether to use pandoc for conversion (must be True)
            
        Returns:
            LaTeX formatted content
            
        Raises:
            RuntimeError: If pandoc is not available or conversion fails
        """
        if not markdown_content or not markdown_content.strip():
            return "% No content provided\n"
        
        # Force pandoc usage - no fallback
        if not _lazy_import_pypandoc():
            raise RuntimeError(
                "Pandoc is required but not available. "
                "Please install pandoc from https://pandoc.org/installing.html "
                "and ensure pypandoc is installed: pip install pypandoc"
            )
        
        try:
            import pypandoc
            latex_content = pypandoc.convert_text(
                markdown_content,
                'latex',
                format='markdown',
                extra_args=[
                    '--wrap=preserve',
                    '--standalone',
                    '--no-highlight'
                ]
            )
            
            # Extract only the body content (remove document wrapper)
            latex_content = self._extract_latex_body(latex_content)
            return latex_content
            
        except Exception as e:
            raise RuntimeError(f"Pandoc conversion failed: {e}. Ensure pandoc is properly installed.")
    
    def _extract_latex_body(self, latex_content: str) -> str:
        """Extract body content from standalone LaTeX document"""
        # Remove \documentclass, \begin{document}, \end{document}, etc.
        body_pattern = r'\\begin\{document\}(.*?)\\end\{document\}'
        match = re.search(body_pattern, latex_content, re.DOTALL)
        
        if match:
            body = match.group(1).strip()
            # Remove any remaining preamble commands
            body = re.sub(r'\\(title|author|date)\{[^}]*\}', '', body)
            body = re.sub(r'\\maketitle', '', body)
            return body.strip()
        
        return latex_content
    
    def _basic_markdown_to_latex(self, markdown_content: str) -> str:
        """
        Basic markdown to LaTeX conversion without pandoc
        Handles common markdown syntax
        """
        latex = markdown_content
        
        # Headers
        latex = re.sub(r'^# (.+)$', r'\\section{\1}', latex, flags=re.MULTILINE)
        latex = re.sub(r'^## (.+)$', r'\\subsection{\1}', latex, flags=re.MULTILINE)
        latex = re.sub(r'^### (.+)$', r'\\subsubsection{\1}', latex, flags=re.MULTILINE)
        latex = re.sub(r'^#### (.+)$', r'\\paragraph{\1}', latex, flags=re.MULTILINE)
        
        # Bold and italic
        latex = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', latex)
        latex = re.sub(r'\*(.+?)\*', r'\\textit{\1}', latex)
        latex = re.sub(r'__(.+?)__', r'\\textbf{\1}', latex)
        latex = re.sub(r'_(.+?)_', r'\\textit{\1}', latex)
        
        # Inline code
        latex = re.sub(r'`(.+?)`', r'\\texttt{\1}', latex)
        
        # Code blocks
        latex = re.sub(
            r'```(\w+)?\n(.*?)```',
            lambda m: f'\\begin{{lstlisting}}[language={m.group(1) or ""}]\n{m.group(2)}\\end{{lstlisting}}',
            latex,
            flags=re.DOTALL
        )
        
        # Lists (basic support)
        # Unordered lists
        latex = re.sub(r'^\* (.+)$', r'\\item \1', latex, flags=re.MULTILINE)
        latex = re.sub(r'^- (.+)$', r'\\item \1', latex, flags=re.MULTILINE)
        
        # Wrap consecutive \item commands in itemize environment
        latex = self._wrap_list_items(latex, 'itemize')
        
        # Links
        latex = re.sub(r'\[(.+?)\]\((.+?)\)', r'\\href{\2}{\1}', latex)
        
        # Escape special LaTeX characters in remaining text
        # (Be careful not to escape already converted LaTeX commands)
        
        return latex
    
    def _wrap_list_items(self, text: str, env_type: str = 'itemize') -> str:
        """Wrap consecutive \\item commands in list environment"""
        lines = text.split('\n')
        result = []
        in_list = False
        
        for line in lines:
            if line.strip().startswith('\\item'):
                if not in_list:
                    result.append(f'\\begin{{{env_type}}}')
                    in_list = True
                result.append(line)
            else:
                if in_list:
                    result.append(f'\\end{{{env_type}}}')
                    in_list = False
                result.append(line)
        
        if in_list:
            result.append(f'\\end{{{env_type}}}')
        
        return '\n'.join(result)
    
    def process_chapter_content(self, book_id: str, chapter_index: int, markdown_content: str) -> str:
        """
        Process and save chapter content
        
        Args:
            book_id: Book identifier
            chapter_index: Chapter index (0-based)
            markdown_content: Raw markdown content
            
        Returns:
            Path to saved LaTeX file
        """
        # Convert markdown to LaTeX
        latex_content = self.markdown_to_latex(markdown_content)
        
        # Save to file
        book_dir = self.output_dir / book_id / "sections"
        book_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = book_dir / f"chapter_{chapter_index + 1}_content.tex"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        return str(output_file.relative_to(self.output_dir / book_id))
