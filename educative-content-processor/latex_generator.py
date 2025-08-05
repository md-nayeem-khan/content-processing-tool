"""
LaTeX Book Generator using Jinja2 Templates
"""

from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, List
import os
import shutil
import re
from pathlib import Path
from datetime import datetime

from main import SanitizedBookResponse, BookChapter, BookSection

class LaTeXBookGenerator:
    """Generate LaTeX books from sanitized Educative data using Jinja2 templates"""
    
    def __init__(self, template_dir: str = "templates/latex-book", output_dir: str = "generated_books"):
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        
        # Initialize Jinja2 environment with LaTeX-friendly settings
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml']),  # Don't autoescape LaTeX
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
        
        # Convert to lowercase and replace spaces with underscores
        slug = text.lower()
        # Remove or replace special characters
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '_', slug)
        # Remove leading/trailing underscores
        slug = slug.strip('_')
        return slug
        
    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters"""
        if not text:
            return ""
        
        # LaTeX special characters that need escaping
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
    
    def generate_book(self, book_data: SanitizedBookResponse, book_name: str, content_type: str = "course") -> Dict[str, str]:
        """
        Generate complete LaTeX book from sanitized book data
        
        Args:
            book_data: Sanitized book response from Educative API
            book_name: Name for the generated book (used for directory)
            
        Returns:
            Dictionary mapping file paths to generated content
        """
        if not book_data.success:
            raise ValueError(f"Cannot generate book from failed response: {book_data.error_message}")
        
        generated_files = {}
        
        # Pre-compute chapter slugs for template rendering
        chapters_with_slugs = []
        for chapter in book_data.chapters or []:
            chapter_with_slug = chapter.dict()  # Convert to dict to add slug
            chapter_with_slug['chapter_slug'] = self._slugify(chapter.title)
            chapters_with_slugs.append(chapter_with_slug)
        
        # Generate main.tex
        main_template = self.env.get_template('main.tex.j2')
        main_content = main_template.render(
            book_title=book_data.book_title,
            book_summary=book_data.book_summary,
            book_brief_summary=book_data.book_brief_summary,
            chapters=chapters_with_slugs,
            total_chapters=book_data.total_chapters,
            total_sections=book_data.total_sections
        )
        generated_files['main.tex'] = main_content
        
        # Generate custom preface
        preface_template = self.env.get_template('preface.tex.j2')
        preface_content = preface_template.render(
            book_title=book_data.book_title,
            book_summary=book_data.book_summary,
            book_brief_summary=book_data.book_brief_summary,
            total_chapters=book_data.total_chapters,
            total_sections=book_data.total_sections
        )
        generated_files['files/0.Preface.tex'] = preface_content
        
        # Generate individual chapter files with dynamic section inclusion
        chapter_template = self.env.get_template('chapter.tex.j2')
        
        for i, chapter in enumerate(book_data.chapters or [], 1):
            chapter_slug = self._slugify(chapter.title)
            chapter_content = chapter_template.render(
                chapter=chapter,
                chapter_number=i,
                chapter_slug=chapter_slug
            )
            # Use consistent chapter file naming
            chapter_filename = f'files/chapter_{i}_{chapter_slug}.tex'
            generated_files[chapter_filename] = chapter_content
        
        # Generate section metadata file for Phase 3 reference
        section_metadata = self._generate_section_metadata(book_data, content_type)
        generated_files['sections/section_metadata.json'] = section_metadata
        
        return generated_files
    
    def _generate_section_metadata(self, book_data: SanitizedBookResponse, content_type: str = "course") -> str:
        """Generate metadata file for sections to help with Phase 3 content generation"""
        import json
        
        metadata = {
            "book_title": book_data.book_title,
            "content_type": content_type,
            "generation_timestamp": datetime.now().isoformat(),
            "chapters": []
        }
        
        for i, chapter in enumerate(book_data.chapters or [], 1):
            chapter_slug = self._slugify(chapter.title)
            chapter_info = {
                "chapter_number": i,
                "chapter_title": chapter.title,
                "chapter_slug": chapter_slug,
                "chapter_file": f"files/chapter_{i}_{chapter_slug}.tex",
                "sections": []
            }
            
            for section in chapter.sections:
                section_info = {
                    "section_id": section.id,
                    "section_title": section.title,
                    "section_slug": section.slug,
                    "section_file": f"files/chapter_{i}_{chapter_slug}/section_{section.id}.tex",
                    "content_status": "pending"  # Will be updated when content is generated
                }
                chapter_info["sections"].append(section_info)
            
            metadata["chapters"].append(chapter_info)
        
        return json.dumps(metadata, indent=2)
    
    def generate_section_content(self, chapter_slug: str, section: BookSection, content: str = None) -> str:
        """
        Generate individual section content file
        
        Args:
            chapter_slug: Slugified chapter title for consistent naming
            section: Section object with metadata
            content: Optional section content (for Phase 3)
            
        Returns:
            Generated section content as string
        """
        section_template = self.env.get_template('section.tex.j2')
        
        return section_template.render(
            section=section,
            section_content=content,
            generation_timestamp=datetime.now().isoformat()
        )
    
    def save_book_to_disk(self, generated_files: Dict[str, str], book_name: str) -> str:
        """
        Save generated LaTeX files to disk with proper directory structure
        
        Args:
            generated_files: Dictionary mapping file paths to content
            book_name: Name for the book directory
            
        Returns:
            Path to the generated book directory
        """
        book_dir = self.output_dir / book_name
        book_dir.mkdir(parents=True, exist_ok=True)
        
        # Create sections directory for Phase 3 content
        sections_dir = book_dir / 'sections'
        sections_dir.mkdir(exist_ok=True)
        
        # Copy template assets (amd.sty, theorems.tex, etc.)
        template_book_dir = Path("templates/book-template")
        if template_book_dir.exists():
            # Copy style files
            for asset_file in ['amd.sty', 'theorems.tex', 'References.bib']:
                src = template_book_dir / asset_file
                if src.exists():
                    shutil.copy2(src, book_dir / asset_file)
            
            # Copy Images directory
            images_src = template_book_dir / 'Images'
            images_dst = book_dir / 'Images'
            if images_src.exists():
                shutil.copytree(images_src, images_dst, dirs_exist_ok=True)
            
            # Copy static files from template (excluding preface which we'll generate)
            static_files_src = template_book_dir / 'files'
            files_dir = book_dir / 'files'
            files_dir.mkdir(exist_ok=True)
            
            # Copy static template files (excluding preface)
            for static_file in ['0.0.0.titlepage.tex', '0.zommaire.tex']:
                src = static_files_src / static_file
                if src.exists():
                    shutil.copy2(src, files_dir / static_file)
        
        # Write generated files
        for file_path, content in generated_files.items():
            full_path = book_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return str(book_dir)
    
    def generate_and_save_book(self, book_data: SanitizedBookResponse, book_name: str, content_type: str = "course") -> str:
        """
        Complete workflow: generate and save LaTeX book to disk
        
        Args:
            book_data: Sanitized book response from Educative API
            book_name: Name for the generated book
            
        Returns:
            Path to the generated book directory
        """
        generated_files = self.generate_book(book_data, book_name, content_type)
        return self.save_book_to_disk(generated_files, book_name)


# Example usage function
def example_usage():
    """Example of how to use the LaTeX book generator"""
    
    # Sample book data (would come from your API)
    sample_book_data = SanitizedBookResponse(
        success=True,
        book_title="Learn HTML, CSS, and JavaScript from Scratch",
        book_summary="A comprehensive guide to web development",
        book_brief_summary="Web development fundamentals",
        chapters=[
            BookChapter(
                title="Semantic Web Page Layout with HTML",
                summary="Learn how to use HTML for structuring semantic, accessible, and well-organized web pages effectively.",
                sections=[
                    BookSection(title="What is HTML?", id="1", slug="what-is-html"),
                    BookSection(title="HTML Structure", id="2", slug="html-structure"),
                ]
            )
        ],
        total_chapters=1,
        total_sections=2,
        source="example"
    )
    
    # Generate the book
    generator = LaTeXBookGenerator()
    book_path = generator.generate_and_save_book(sample_book_data, "html-css-js-guide")
    
    print(f"Book generated at: {book_path}")
    return book_path

if __name__ == "__main__":
    example_usage()
