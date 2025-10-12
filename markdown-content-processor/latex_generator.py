"""
LaTeX Book Generator for Markdown Content Processor
Generates LaTeX books from markdown content using Jinja2 templates
"""

from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, List
import os
import shutil
import re
from pathlib import Path
from datetime import datetime

class LaTeXBookGenerator:
    """Generate LaTeX books from markdown content using Jinja2 templates"""
    
    def __init__(self, template_dir: str = "latex_templates", output_dir: str = "generated_books"):
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        
        # Initialize Jinja2 environment with LaTeX-friendly settings
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            block_start_string='{% ',
            block_end_string=' %}',
            variable_start_string='{{',
            variable_end_string='}}',
            comment_start_string='{#',
            comment_end_string='#}',
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom LaTeX filters
        self.env.filters['escape_latex'] = self._escape_latex
        self.env.filters['slugify'] = self._slugify
        
    def _slugify(self, text: str) -> str:
        """Convert text to a valid file slug"""
        if not text:
            return ""
        
        slug = text.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '_', slug)
        return slug.strip('_')
        
    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters"""
        if not text:
            return ""
        
        latex_special_chars = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '^': r'\textasciicircum{}',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '\\': r'\textbackslash{}',
        }
        
        for char, escaped in latex_special_chars.items():
            text = text.replace(char, escaped)
        
        return text
    
    def generate_book(self, book_data: dict, book_id: str) -> Dict[str, str]:
        """
        Generate complete LaTeX book from book data
        
        Args:
            book_data: Book data with chapters and metadata
            book_id: Book identifier (used for directory)
            
        Returns:
            Dictionary with generation results
        """
        generated_files = {}
        
        # Create book directory structure
        book_dir = self.output_dir / book_id
        book_dir.mkdir(parents=True, exist_ok=True)
        
        files_dir = book_dir / "files"
        files_dir.mkdir(exist_ok=True)
        
        images_dir = book_dir / "Images"
        images_dir.mkdir(exist_ok=True)
        
        # Copy template files (amd.sty, theorems.tex, etc.)
        self._copy_template_files(book_dir)
        
        # Pre-compute chapter slugs for template rendering
        chapters_with_slugs = []
        for idx, chapter in enumerate(book_data.get('chapters', []), start=1):
            chapter_with_slug = chapter.copy()
            chapter_with_slug['chapter_slug'] = self._slugify(chapter.get('title', f'Chapter {idx}'))
            chapter_with_slug['chapter_number'] = idx
            chapters_with_slugs.append(chapter_with_slug)
        
        # Generate main.tex dynamically with chapter references
        main_template = self.env.get_template('main.tex.j2')
        main_content = main_template.render(
            book_title=book_data.get('name', 'Untitled Book'),
            book_description=book_data.get('description', ''),
            chapters=chapters_with_slugs,
            total_chapters=len(chapters_with_slugs)
        )
        
        main_file = book_dir / "Main.tex"
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(main_content)
        
        generated_files['Main.tex'] = str(main_file)
        
        # Generate chapter files dynamically
        chapter_template = self.env.get_template('chapter.tex.j2')
        
        for chapter_info in chapters_with_slugs:
            idx = chapter_info['chapter_number']
            chapter_slug = chapter_info['chapter_slug']
            
            # Create chapter subdirectory for sections
            chapter_subdir = files_dir / f"chapter_{idx}_{chapter_slug}"
            chapter_subdir.mkdir(exist_ok=True)
            
            # Process sections for this chapter
            sections_with_content = []
            for section in chapter_info.get('sections', []):
                section_with_content = section.copy()
                
                # Generate individual section file
                if 'content_file' in section:
                    content_file = book_dir / section['content_file']
                    if content_file.exists():
                        with open(content_file, 'r', encoding='utf-8') as f:
                            markdown_content = f.read()
                        
                        # Convert markdown to LaTeX
                        from section_processor import MarkdownProcessor
                        processor = MarkdownProcessor()
                        latex_content = processor.markdown_to_latex(markdown_content)
                        
                        # Save section content to its own file
                        section_file = chapter_subdir / f"section_{section['id']}.tex"
                        with open(section_file, 'w', encoding='utf-8') as f:
                            f.write(latex_content)
                        
                        generated_files[f"chapter_{idx}_{chapter_slug}/section_{section['id']}.tex"] = str(section_file)
                
                sections_with_content.append(section_with_content)
            
            # Update chapter info with processed sections
            chapter_info['sections'] = sections_with_content
            
            # Render chapter template with section references
            chapter_latex = chapter_template.render(
                chapter=chapter_info
            )
            
            # Use consistent naming: chapter_1_slug.tex
            chapter_filename = f"chapter_{idx}_{chapter_slug}.tex"
            chapter_file = files_dir / chapter_filename
            with open(chapter_file, 'w', encoding='utf-8') as f:
                f.write(chapter_latex)
            
            generated_files[chapter_filename] = str(chapter_file)
        
        # Generate front matter files (titlepage, preface, table of contents)
        self._generate_front_matter(files_dir, book_data)
        
        return {
            'success': True,
            'book_path': str(book_dir),
            'generated_files': list(generated_files.keys())
        }
    
    def _copy_template_files(self, book_dir: Path):
        """Copy template support files to book directory"""
        template_book_dir = Path("templates/book-template")
        
        if not template_book_dir.exists():
            print(f"Warning: Template directory not found: {template_book_dir}")
            return
        
        # Copy amd.sty
        if (template_book_dir / "amd.sty").exists():
            shutil.copy2(template_book_dir / "amd.sty", book_dir / "amd.sty")
        
        # Copy theorems.tex
        if (template_book_dir / "theorems.tex").exists():
            shutil.copy2(template_book_dir / "theorems.tex", book_dir / "theorems.tex")
        
        # Copy References.bib
        if (template_book_dir / "References.bib").exists():
            shutil.copy2(template_book_dir / "References.bib", book_dir / "References.bib")
    
    def _generate_front_matter(self, files_dir: Path, book_data: dict):
        """Generate front matter files (titlepage, preface, TOC)"""
        
        chapter_count = len(book_data.get('chapters', []))
        
        # Title page
        titlepage_content = r"""\documentclass[../Main.tex]{subfiles}
\begin{document}
\thispagestyle{empty}
\begin{center}
    \vspace*{2cm}
    {\Huge\bfseries \BigTitle}\\[1cm]
    {\Large \LittleTitle}\\[2cm]
    {\large Generated with Markdown Content Processor}\\[1cm]
    {\large """ + datetime.now().strftime("%B %Y") + r"""}
\end{center}
\end{document}
"""
        
        with open(files_dir / "0.0.0.titlepage.tex", 'w', encoding='utf-8') as f:
            f.write(titlepage_content)
        
        # Preface with chapter count
        description = book_data.get('description', 'No description provided.')
        preface_content = r"""\documentclass[../Main.tex]{subfiles}
\begin{document}
\chapter*{Preface}
\addcontentsline{toc}{chapter}{Preface}

This book was generated using the Markdown Content Processor, a tool for converting markdown content into beautifully formatted LaTeX documents.

\vspace{1cm}

\textbf{Book Description:}

""" + description + r"""

\vspace{1cm}

\textbf{Book Statistics:}
\begin{itemize}
    \item Total Chapters: """ + str(chapter_count) + r"""
    \item Generated: """ + datetime.now().strftime("%B %d, %Y") + r"""
\end{itemize}

\end{document}
"""
        
        with open(files_dir / "0.Preface.tex", 'w', encoding='utf-8') as f:
            f.write(preface_content)
        
        # Table of contents
        toc_content = r"""\documentclass[../Main.tex]{subfiles}
\begin{document}
\tableofcontents
\end{document}
"""
        
        with open(files_dir / "0.zommaire.tex", 'w', encoding='utf-8') as f:
            f.write(toc_content)
