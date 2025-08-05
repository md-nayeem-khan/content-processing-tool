"""
Section Content Processor for Educative Components
Handles conversion of Educative section components to LaTeX using Pandoc
"""

import json
import re
import httpx
import aiohttp
import aiofiles
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
import base64
import asyncio
# Lazy import flags - libraries will be imported only when needed
PANDOC_AVAILABLE = None
CAIROSVG_AVAILABLE = None
PIL_AVAILABLE = None
WAND_AVAILABLE = None

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

def _lazy_import_cairosvg():
    """Lazy import cairosvg only when needed"""
    global CAIROSVG_AVAILABLE
    if CAIROSVG_AVAILABLE is None:
        try:
            import cairosvg
            CAIROSVG_AVAILABLE = True
        except (ImportError, Exception):
            CAIROSVG_AVAILABLE = False
    return CAIROSVG_AVAILABLE

def _lazy_import_pil():
    """Lazy import PIL only when needed"""
    global PIL_AVAILABLE
    if PIL_AVAILABLE is None:
        try:
            from PIL import Image
            PIL_AVAILABLE = True
        except ImportError:
            PIL_AVAILABLE = False
    return PIL_AVAILABLE

def _lazy_import_wand():
    """Lazy import Wand only when needed"""
    global WAND_AVAILABLE
    if WAND_AVAILABLE is None:
        try:
            from wand.image import Image as WandImage
            WAND_AVAILABLE = True
        except (ImportError, Exception):
            WAND_AVAILABLE = False
    return WAND_AVAILABLE

class SectionContentProcessor:
    """Process Educative section components and convert to LaTeX"""
    
    def __init__(self, output_dir: str = "generated_books"):
        self.output_dir = Path(output_dir)
        self.images_dir = None  # Will be set per book
        self.current_chapter_number = None
        self.current_section_id = None
        
    def set_book_context(self, book_name: str, chapter_number: int = None, section_id: str = None):
        """Set the context for a specific book, chapter, and section"""
        book_path = self.output_dir / book_name
        self.images_dir = book_path / "Images"  # Capital I to match existing structure
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Set current chapter and section for hierarchical organization
        self.current_chapter_number = chapter_number
        self.current_section_id = section_id
        
    async def fetch_section_content(self, content_type: str, course_slug: str = None, 
                                  section_slug: str = None, author_id: str = None, 
                                  collection_id: str = None, page_id: str = None,
                                  token: str = None, cookie: str = None) -> Dict[str, Any]:
        """
        Fetch section content from Educative API (supports both course and interview-prep types)
        
        Args:
            content_type: Type of content ('course' or 'interview-prep')
            course_slug: Course slug (for interview-prep)
            section_slug: Section slug (for interview-prep) 
            author_id: Educative author ID (for course)
            collection_id: Educative collection ID (for course)
            page_id: Section page ID (for course)
            token: Authentication token
            cookie: Authentication cookie
            
        Returns:
            Section content data
        """
        # Construct URL based on content type
        if content_type == "interview-prep":
            if not course_slug or not section_slug:
                raise ValueError("course_slug and section_slug are required for interview-prep content")
            url = f"https://www.educative.io/api/interview-prep/{course_slug}/page/{section_slug}?work_type=module"
        else:  # Default to course type
            if not author_id or not collection_id or not page_id:
                raise ValueError("author_id, collection_id, and page_id are required for course content")
            url = f"https://www.educative.io/api/collection/{author_id}/{collection_id}/page/{page_id}?work_type=collection"
        
        print(f"DEBUG: Fetching {content_type} content from: {url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Referer": "https://www.educative.io/"
        }
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if cookie:
            headers["Cookie"] = cookie
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def process_section_components_async(self, section_data: Dict[str, Any]) -> Tuple[str, List[str], List[str]]:
        """
        Process section components and convert to LaTeX (ASYNC VERSION)
        
        Args:
            section_data: Raw section data from Educative API
            
        Returns:
            Tuple of (latex_content, generated_images, component_types)
        """
        components = section_data.get("components", [])
        latex_parts = []
        generated_images = []
        component_types = []
        
        for component in components:
            component_type = component.get("type", "Unknown")
            component_types.append(component_type)
            
            try:
                if component_type == "SlateHTML":
                    latex_content = self._process_slate_html(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "MarkdownEditor":
                    latex_content = self._process_markdown_editor(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "DrawIOWidget":
                    latex_content, image_files = await self._process_drawio_widget_async(component)
                    latex_parts.append(latex_content)
                    generated_images.extend(image_files)
                    
                elif component_type == "StructuredQuiz":
                    latex_content = self._process_structured_quiz(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "Columns":
                    latex_content, images = await self._process_columns_async(component)
                    latex_parts.append(latex_content)
                    generated_images.extend(images)
                    
                elif component_type == "MarkMap":
                    latex_content = self._process_markmap(component)
                    latex_parts.append(latex_content)
                    
                else:
                    # Handle unknown component types
                    latex_parts.append(f"\\textit{{Component type '{component_type}' not yet supported.}}")
                    
            except Exception as e:
                latex_parts.append(f"\\textit{{Error processing {component_type}: {str(e)}}}")
        
        # Join all components
        full_latex = "\n\n".join(latex_parts)
        
        # Apply final fixes that might span component boundaries
        full_latex = self._apply_final_latex_fixes(full_latex)
        
        return full_latex, generated_images, list(set(component_types))

    def process_section_components(self, section_data: Dict[str, Any]) -> Tuple[str, List[str], List[str]]:
        """
        Process section components and convert to LaTeX (LEGACY SYNC VERSION)
        
        Args:
            section_data: Raw section data from Educative API
            
        Returns:
            Tuple of (latex_content, generated_images, component_types)
        """
        components = section_data.get("components", [])
        latex_parts = []
        generated_images = []
        component_types = []
        
        for component in components:
            component_type = component.get("type", "Unknown")
            component_types.append(component_type)
            
            try:
                if component_type == "SlateHTML":
                    latex_content = self._process_slate_html(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "MarkdownEditor":
                    latex_content = self._process_markdown_editor(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "DrawIOWidget":
                    latex_content, image_files = self._process_drawio_widget(component)
                    latex_parts.append(latex_content)
                    generated_images.extend(image_files)
                    
                elif component_type == "StructuredQuiz":
                    latex_content = self._process_structured_quiz(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "Columns":
                    latex_content, images = self._process_columns(component)
                    latex_parts.append(latex_content)
                    generated_images.extend(images)
                    
                elif component_type == "MarkMap":
                    latex_content = self._process_markmap(component)
                    latex_parts.append(latex_content)
                    
                else:
                    # Handle unknown component types
                    latex_parts.append(f"\\textit{{Component type '{component_type}' not yet supported.}}")
                    
            except Exception as e:
                latex_parts.append(f"\\textit{{Error processing {component_type}: {str(e)}}}")
        
        # Join all components
        full_latex = "\n\n".join(latex_parts)
        
        # Apply final fixes that might span component boundaries
        full_latex = self._apply_final_latex_fixes(full_latex)
        
        return full_latex, generated_images, list(set(component_types))
    
    def _apply_final_latex_fixes(self, latex_content: str) -> str:
        """Apply final LaTeX fixes after all components are processed and joined"""
        if not latex_content:
            return latex_content
            
        # Apply the specific problem fixes that might span component boundaries
        
        # Fix "April 2008,I joined" -> "April 2008, I joined"
        latex_content = re.sub(r'(\d{4}),([A-Z])', r'\1, \2', latex_content)
        
        # Fix "problem,---for example" -> "problem---for example"  
        latex_content = re.sub(r',---', r'---', latex_content)
        
        # Fix other missing spaces after punctuation that might span components
        latex_content = re.sub(r'([.!?,;:])([A-Z])', r'\1 \2', latex_content)
        
        # Fix sentence boundaries that might be split across components
        latex_content = re.sub(r'\.([A-Z][a-z])', r'. \1', latex_content)
        
        # NEW: Fix line breaks that split words inappropriately
        # Fix cases like "build-\ning" -> "building" 
        latex_content = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', latex_content)
        
        # NEW: Fix specific problematic line breaks identified in testing
        latex_content = re.sub(r'Since\s*\n\s*System', 'Since System', latex_content)
        latex_content = re.sub(r'Amazon\s*\n\s*launched', 'Amazon launched', latex_content)
        latex_content = re.sub(r'Most\s*\n\s*engineers', 'Most engineers', latex_content)
        latex_content = re.sub(r'With\s*\n\s*the\s+right', 'With the right', latex_content)
        latex_content = re.sub(r'In\s*\n\s*April', 'In April', latex_content)
        latex_content = re.sub(r'However\s*\n\s*,', 'However,', latex_content)
        latex_content = re.sub(r'Therefore\s*\n\s*,', 'Therefore,', latex_content)
        
        # Fix other common mid-sentence line breaks
        latex_content = re.sub(r'([a-z])\s*\n\s*([a-z])', r'\1 \2', latex_content)
        
        # NEW: Fix line breaks in the middle of sentences
        # Join lines that don't end with proper sentence terminators
        lines = latex_content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            current_line = lines[i].strip()
            
            # Skip empty lines and LaTeX commands
            if not current_line or current_line.startswith('%') or current_line.startswith('\\'):
                fixed_lines.append(lines[i])
                i += 1
                continue
            
            # Check if this line should be joined with the next
            if (i + 1 < len(lines)):
                next_line = lines[i + 1].strip()
                
                # Join if:
                # 1. Current line doesn't end with sentence terminators or LaTeX commands
                # 2. Next line exists and isn't empty
                # 3. Next line doesn't start with LaTeX commands or comments
                # 4. Current line doesn't end with certain patterns that should stay separate
                should_join = (
                    current_line and 
                    not current_line.endswith(('.', '!', '?', ':', '}', '\\\\')) and
                    not current_line.endswith(('\\end{', '\\begin{')) and
                    next_line and
                    not next_line.startswith('\\') and
                    not next_line.startswith('%') and
                    not next_line.startswith('\\begin') and
                    not next_line.startswith('\\end') and
                    # Don't join if current line looks like it should end a paragraph
                    not re.search(r'\.\s*$', current_line)
                )
                
                if should_join:
                    # Join with next line
                    joined_line = current_line + ' ' + next_line
                    fixed_lines.append(joined_line)
                    i += 2  # Skip the next line since we joined it
                else:
                    fixed_lines.append(lines[i])
                    i += 1
            else:
                fixed_lines.append(lines[i])
                i += 1
        
        latex_content = '\n'.join(fixed_lines)
        
        # NEW: Fix specific spacing issues around LaTeX commands
        # Fix "Microsoft}working" -> "Microsoft} working"
        latex_content = re.sub(r'(\}+)([a-zA-Z])', r'\1 \2', latex_content)
        
        # Fix ". In\nApril" -> ". In April" 
        latex_content = re.sub(r'\. ([A-Z])\n([a-z])', r'. \1\2', latex_content)
        
        # Clean up any double spaces created by fixes
        latex_content = re.sub(r'  +', ' ', latex_content)
        
        # Clean up excessive newlines but preserve structure
        latex_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', latex_content)
        
        return latex_content
    
    def _process_slate_html(self, component: Dict[str, Any]) -> str:
        """Process SlateHTML components using Pandoc"""
        html_content = component.get("content", {}).get("html", "")
        if not html_content:
            return ""
            
        # Convert HTML to LaTeX using Pandoc
        latex_content = self._html_to_latex_pandoc(html_content)
        return latex_content
    
    def _process_markdown_editor(self, component: Dict[str, Any]) -> str:
        """Process MarkdownEditor components using Pandoc"""
        content = component.get("content", {})
        text = content.get("text", "")
        
        if not text:
            return ""
            
        # Convert markdown to LaTeX using Pandoc
        latex_content = self._markdown_to_latex_pandoc(text)
        return latex_content
    
    async def _process_drawio_widget_async(self, component: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Process DrawIOWidget components with enhanced image extraction (ASYNC VERSION)"""
        content = component.get("content", {})
        
        # Extract image path - try multiple possible locations
        image_path = None
        caption = content.get("caption", "")
        
        # Method 1: Check for editorImagePath in Educative JSON
        if "editorImagePath" in content:
            image_path = content["editorImagePath"]
            print(f"DEBUG: Found editorImagePath: {image_path}")
        
        # Method 2: Fallback to legacy path field
        elif "path" in content:
            image_path = content["path"]
            print(f"DEBUG: Using fallback path: {image_path}")
        
        # Method 3: Check nested content structures
        elif "diagram" in content and isinstance(content["diagram"], dict):
            diagram_data = content["diagram"]
            if "imagePath" in diagram_data:
                image_path = diagram_data["imagePath"]
                print(f"DEBUG: Found diagram imagePath: {image_path}")
        
        generated_images = []
        
        if image_path:
            # Download and save the image using async method
            try:
                image_relative_path = await self._download_image_async(image_path)
                
                if image_relative_path:
                    generated_images.append(image_relative_path)
                    
                    # Convert any image format to PNG for better LaTeX compatibility
                    converted_path = await self._convert_image_to_png(image_relative_path)
                    
                    if converted_path and converted_path != image_relative_path:
                        # Successfully converted to PNG
                        latex_content = f"""
\\begin{{figure}}[htbp]
    \\centering
    \\includegraphics[width=0.8\\textwidth]{{{converted_path}}}
    {f"\\caption{{{self._escape_latex(caption)}}}" if caption else ""}
\\end{{figure}}
"""
                        print(f"✅ Using converted PNG image: {converted_path}")
                        return latex_content.strip(), [converted_path]
                    else:
                        # Use original image (PNG/JPG or conversion failed)
                        file_ext = os.path.splitext(image_relative_path)[1].lower()
                        if file_ext in ['.png', '.jpg', '.jpeg']:
                            latex_content = f"""
\\begin{{figure}}[htbp]
    \\centering
    \\includegraphics[width=0.8\\textwidth]{{{image_relative_path}}}
    {f"\\caption{{{self._escape_latex(caption)}}}" if caption else ""}
\\end{{figure}}
"""
                        else:
                            # Unsupported format, show placeholder
                            latex_content = f"""
\\begin{{figure}}[htbp]
    \\centering
    % Unsupported image format: {file_ext}
    % Original file: {image_relative_path}
    \\textit{{[Image: {self._escape_latex(caption) if caption else 'Diagram'} - Format: {file_ext}]}}
    {f"\\caption{{{self._escape_latex(caption)}}}" if caption else ""}
\\end{{figure}}
"""
                            print(f"⚠️  Warning: Unsupported image format {file_ext} for LaTeX")
                    
                    return latex_content.strip(), generated_images
                    
            except Exception as e:
                print(f"Error processing DrawIOWidget image: {e}")
                return f"\\textit{{Error loading image: {str(e)}}}", []
        
        return "\\textit{Image content not available}", generated_images

    def _process_drawio_widget(self, component: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Process DrawIOWidget components with enhanced image extraction (SYNC VERSION - DEPRECATED)"""
        content = component.get("content", {})
        
        # Extract image path - try multiple possible locations
        image_path = None
        caption = content.get("caption", "")
        
        # Method 1: Check for editorImagePath in Educative JSON
        if "editorImagePath" in content:
            image_path = content["editorImagePath"]
            print(f"DEBUG: Found editorImagePath: {image_path}")
        
        # Method 2: Fallback to legacy path field
        elif "path" in content:
            image_path = content["path"]
            print(f"DEBUG: Using fallback path: {image_path}")
        
        # Method 3: Check nested content structures
        elif "diagram" in content and isinstance(content["diagram"], dict):
            diagram_data = content["diagram"]
            if "imagePath" in diagram_data:
                image_path = diagram_data["imagePath"]
                print(f"DEBUG: Found diagram imagePath: {image_path}")
        
        generated_images = []
        
        if image_path:
            # Download and save the image using new async method
            try:
                # Try to handle nested event loops if possible
                try:
                    import nest_asyncio
                    nest_asyncio.apply()
                except ImportError:
                    pass  # nest_asyncio not available, proceed without it
                except RuntimeError:
                    pass  # Already applied or not needed
                
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Event loop is running, we can't use run_until_complete
                        # Fall back to a simplified sync version
                        print("WARNING: Event loop already running, using simplified image handling")
                        return f"\\textit{{Image download skipped - async conflict with path: {image_path}}}", []
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                image_relative_path = loop.run_until_complete(self._download_image_async(image_path))
                
                if image_relative_path:
                    generated_images.append(image_relative_path)
                    
                    # Convert any image format to PNG for better LaTeX compatibility
                    try:
                        converted_path = loop.run_until_complete(self._convert_image_to_png(image_relative_path))
                    except Exception as e:
                        print(f"Image conversion failed: {e}")
                        converted_path = image_relative_path
                    
                    if converted_path and converted_path != image_relative_path:
                        # Successfully converted to PNG
                        latex_content = f"""
\\begin{{figure}}[htbp]
    \\centering
    \\includegraphics[width=0.8\\textwidth]{{{converted_path}}}
    {f"\\caption{{{self._escape_latex(caption)}}}" if caption else ""}
\\end{{figure}}
"""
                        print(f"✅ Using converted PNG image: {converted_path}")
                        return latex_content.strip(), [converted_path]
                    else:
                        # Use original image (PNG/JPG or conversion failed)
                        file_ext = os.path.splitext(image_relative_path)[1].lower()
                        if file_ext in ['.png', '.jpg', '.jpeg']:
                            latex_content = f"""
\\begin{{figure}}[htbp]
    \\centering
    \\includegraphics[width=0.8\\textwidth]{{{image_relative_path}}}
    {f"\\caption{{{self._escape_latex(caption)}}}" if caption else ""}
\\end{{figure}}
"""
                        else:
                            # Unsupported format, show placeholder
                            latex_content = f"""
\\begin{{figure}}[htbp]
    \\centering
    % Unsupported image format: {file_ext}
    % Original file: {image_relative_path}
    \\textit{{[Image: {self._escape_latex(caption) if caption else 'Diagram'} - Format: {file_ext}]}}
    {f"\\caption{{{self._escape_latex(caption)}}}" if caption else ""}
\\end{{figure}}
"""
                            print(f"⚠️  Warning: Unsupported image format {file_ext} for LaTeX")
                    
                    return latex_content.strip(), generated_images
                    
            except Exception as e:
                print(f"Error processing DrawIOWidget image: {e}")
                return f"\\textit{{Error loading image: {str(e)}}}", []
        
        return "\\textit{Image content not available}", generated_images
    
    def _process_structured_quiz(self, component: Dict[str, Any]) -> str:
        """Process StructuredQuiz components"""
        content = component.get("content", {})
        questions = content.get("questions", [])
        
        if not questions:
            return ""
            
        latex_parts = ["\\begin{quote}"]
        latex_parts.append("\\textbf{Quiz:}")
        
        for i, question in enumerate(questions, 1):
            question_text = question.get("questionText", "").strip()
            answer_text = question.get("answerText", "").strip()
            
            if question_text:
                # Check if pandoc is available and import if needed
                if _lazy_import_pypandoc():
                    try:
                        import pypandoc
                        q_latex = pypandoc.convert_text(question_text, 'latex', format='html')
                        latex_parts.append(f"\\textbf{{Question {i}:}} {q_latex.strip()}")
                    except:
                        latex_parts.append(f"\\textbf{{Question {i}:}} {self._escape_latex(question_text)}")
                else:
                    latex_parts.append(f"\\textbf{{Question {i}:}} {self._escape_latex(question_text)}")
                
            if answer_text:
                if _lazy_import_pypandoc():
                    try:
                        import pypandoc
                        a_latex = pypandoc.convert_text(answer_text, 'latex', format='html')
                        latex_parts.append(f"\\textbf{{Answer:}} {a_latex.strip()}")
                    except:
                        latex_parts.append(f"\\textbf{{Answer:}} {self._escape_latex(answer_text)}")
                else:
                    latex_parts.append(f"\\textbf{{Answer:}} {self._escape_latex(answer_text)}")
                
        latex_parts.append("\\end{quote}")
        
        return "\n".join(latex_parts)
    
    async def _process_columns_async(self, component: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Process Columns components (ASYNC VERSION) - renders as side-by-side columns in LaTeX"""
        content = component.get("content", {})
        comps = content.get("comps", [])
        
        if not comps:
            return "", []
        
        column_contents = []
        generated_images = []
        
        # Process each column component
        for comp in comps:
            comp_type = comp.get("type", "")
            
            if comp_type == "MarkdownEditor":
                text = comp.get("content", {}).get("text", "")
                if text:
                    column_contents.append(self._markdown_to_latex_pandoc(text))
                else:
                    column_contents.append("")
                    
            elif comp_type == "DrawIOWidget":
                latex_content, images = await self._process_drawio_widget_async({"content": comp.get("content", {})})
                column_contents.append(latex_content)
                generated_images.extend(images)
            
            elif comp_type == "SlateHTML":
                html_content = comp.get("content", {}).get("html", "")
                if html_content:
                    column_contents.append(self._html_to_latex_pandoc(html_content))
                else:
                    column_contents.append("")
            
            else:
                # Handle unknown component types in columns
                column_contents.append(f"\\textit{{Column component type '{comp_type}' not yet supported.}}")
        
        # Create LaTeX columns layout
        if len(column_contents) == 1:
            # Single column, no need for special layout
            return column_contents[0], generated_images
        
        elif len(column_contents) == 2:
            # Two columns - use minipage for better control (avoid nested figure environments)
            # Clean content to remove figure environments that would cause nesting issues
            clean_content_0 = self._clean_content_for_minipage(column_contents[0])
            clean_content_1 = self._clean_content_for_minipage(column_contents[1])
            
            latex_output = f"""
\\noindent
\\begin{{minipage}}[t]{{0.48\\textwidth}}
{clean_content_0}
\\end{{minipage}}
\\hfill
\\begin{{minipage}}[t]{{0.48\\textwidth}}
{clean_content_1}
\\end{{minipage}}
"""
        
        else:
            # Multiple columns (3 or more) - use minipage approach (avoid nested figure environments)
            num_cols = min(len(column_contents), 4)  # Limit to max 4 columns for readability
            
            # Calculate column width
            col_width = 0.9 / num_cols
            
            latex_parts = []
            for i, content in enumerate(column_contents[:num_cols]):
                clean_content = self._clean_content_for_minipage(content)
                if i > 0:
                    latex_parts.append("\\hfill")
                latex_parts.append(f"""\\begin{{minipage}}[t]{{{col_width:.2f}\\textwidth}}
{clean_content}
\\end{{minipage}}""")
            
            latex_output = f"""
\\noindent
{chr(10).join(latex_parts)}
"""
        
        return latex_output.strip(), generated_images

    def _process_columns(self, component: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Process Columns components (SYNC VERSION) - renders as side-by-side columns in LaTeX"""
        content = component.get("content", {})
        comps = content.get("comps", [])
        
        if not comps:
            return "", []
        
        column_contents = []
        generated_images = []
        
        # Process each column component
        for comp in comps:
            comp_type = comp.get("type", "")
            
            if comp_type == "MarkdownEditor":
                text = comp.get("content", {}).get("text", "")
                if text:
                    column_contents.append(self._markdown_to_latex_pandoc(text))
                else:
                    column_contents.append("")
                    
            elif comp_type == "DrawIOWidget":
                latex_content, images = self._process_drawio_widget({"content": comp.get("content", {})})
                column_contents.append(latex_content)
                generated_images.extend(images)
            
            elif comp_type == "SlateHTML":
                html_content = comp.get("content", {}).get("html", "")
                if html_content:
                    column_contents.append(self._html_to_latex_pandoc(html_content))
                else:
                    column_contents.append("")
            
            else:
                # Handle unknown component types in columns
                column_contents.append(f"\\textit{{Column component type '{comp_type}' not yet supported.}}")
        
        # Create LaTeX columns layout
        if len(column_contents) == 1:
            # Single column, no need for special layout
            return column_contents[0], generated_images
        
        elif len(column_contents) == 2:
            # Two columns - use minipage for better control (avoid nested figure environments)
            # Clean content to remove figure environments that would cause nesting issues
            clean_content_0 = self._clean_content_for_minipage(column_contents[0])
            clean_content_1 = self._clean_content_for_minipage(column_contents[1])
            
            latex_output = f"""
\\noindent
\\begin{{minipage}}[t]{{0.48\\textwidth}}
{clean_content_0}
\\end{{minipage}}
\\hfill
\\begin{{minipage}}[t]{{0.48\\textwidth}}
{clean_content_1}
\\end{{minipage}}
"""
        
        else:
            # Multiple columns (3 or more) - use minipage approach (avoid nested figure environments)
            num_cols = min(len(column_contents), 4)  # Limit to max 4 columns for readability
            
            # Calculate column width
            col_width = 0.9 / num_cols
            
            latex_parts = []
            for i, content in enumerate(column_contents[:num_cols]):
                clean_content = self._clean_content_for_minipage(content)
                if i > 0:
                    latex_parts.append("\\hfill")
                latex_parts.append(f"""\\begin{{minipage}}[t]{{{col_width:.2f}\\textwidth}}
{clean_content}
\\end{{minipage}}""")
            
            latex_output = f"""
\\noindent
{chr(10).join(latex_parts)}
"""
        
        return latex_output.strip(), generated_images
    
    def _clean_content_for_minipage(self, content: str) -> str:
        """Clean content to avoid nested figure environments in minipages"""
        if not content:
            return content
        
        # Remove figure environments but keep the content inside
        import re
        
        # Pattern to match figure environments and extract their content
        figure_pattern = r'\\begin\{figure\}.*?\n(.*?)\\end\{figure\}'
        
        def replace_figure(match):
            figure_content = match.group(1)
            # Remove centering and other figure-specific commands, keep includegraphics and caption
            lines = figure_content.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                # Skip centering and empty lines
                if line == '\\centering' or not line:
                    continue
                # Keep includegraphics and caption
                if '\\includegraphics' in line or '\\caption' in line:
                    cleaned_lines.append(line)
            
            if cleaned_lines:
                return '\n'.join(cleaned_lines)
            else:
                return ''
        
        # Apply the replacement
        cleaned_content = re.sub(figure_pattern, replace_figure, content, flags=re.DOTALL)
        
        return cleaned_content.strip()
    
    def _process_markmap(self, component: Dict[str, Any]) -> str:
        """Process MarkMap components - converts mind map text to LaTeX structured outline"""
        content = component.get("content", {})
        
        # Extract text content and caption
        text = content.get("text", "")
        caption = content.get("caption", "")
        
        if not text:
            return f"\\textit{{MarkMap: {self._escape_latex(caption) if caption else 'Mind Map'}}}"
        
        # Convert the markdown-style mind map text to LaTeX
        latex_content = self._markmap_text_to_latex(text)
        
        # Wrap in a figure-like environment with caption if provided
        if caption:
            result = f"""\\begin{{quote}}
\\textbf{{{self._escape_latex(caption)}}}

{latex_content}
\\end{{quote}}"""
        else:
            result = latex_content
        
        return result.strip()
    
    def _markmap_text_to_latex(self, text: str) -> str:
        """Convert MarkMap markdown text to LaTeX structured format"""
        if not text:
            return ""
        
        import re
        
        # Split into lines and process each line
        lines = text.strip().split('\n')
        latex_lines = []
        in_itemize = False
        
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue
            
            # Count the number of '#' characters to determine heading level
            if stripped_line.startswith('#'):
                # Close any open itemize environment before heading
                if in_itemize:
                    latex_lines.append("\\end{itemize}")
                    in_itemize = False
                
                # Extract heading level and text
                heading_match = re.match(r'^(#+)\s*(.+)$', stripped_line)
                if heading_match:
                    level = len(heading_match.group(1))
                    heading_text = heading_match.group(2).strip()
                    
                    # Convert to appropriate LaTeX heading
                    if level == 1:
                        latex_lines.append(f"\\subsection{{{self._escape_latex(heading_text)}}}")
                    elif level == 2:
                        latex_lines.append(f"\\subsubsection{{{self._escape_latex(heading_text)}}}")
                    elif level >= 3:
                        latex_lines.append(f"\\paragraph{{{self._escape_latex(heading_text)}}}")
                    
                    latex_lines.append("")  # Add spacing after headings
            
            # Handle list items (lines starting with -)
            elif stripped_line.startswith('-'):
                # Start itemize environment if not already started
                if not in_itemize:
                    latex_lines.append("\\begin{itemize}")
                    in_itemize = True
                
                # Extract the list item text
                item_text = stripped_line[1:].strip()
                latex_lines.append(f"\\item {self._escape_latex(item_text)}")
        
        # Close any open itemize environment at the end
        if in_itemize:
            latex_lines.append("\\end{itemize}")
        
        return '\n'.join(latex_lines)
    
    def _html_to_latex_pandoc(self, html: str) -> str:
        """Convert HTML to LaTeX using Pandoc"""
        if not html or not _lazy_import_pypandoc():
            return self._html_to_latex_fallback(html)
        
        try:
            import pypandoc
            # Clean up HTML before conversion
            cleaned_html = self._clean_html_for_pandoc(html)
            
            # Use pandoc to convert HTML to LaTeX
            latex = pypandoc.convert_text(
                cleaned_html, 
                'latex', 
                format='html',
                extra_args=[
                    '--wrap=none',  # Don't wrap lines
                    '--no-highlight',  # Disable syntax highlighting  
                    '--strip-comments'  # Remove HTML comments
                ]
            )
            
            print(f"DEBUG: Pandoc HTML raw output: {repr(latex[:100])}")
            
            # Post-process LaTeX output
            latex = self._clean_latex_output(latex)
            
            print(f"DEBUG: After cleaning: {repr(latex[:100])}")
            
            return latex.strip()
        except Exception as e:
            print(f"Pandoc HTML conversion failed: {e}, falling back to manual conversion")
            return self._html_to_latex_fallback(html)
    
    def _markdown_to_latex_pandoc(self, markdown: str) -> str:
        """Convert Markdown to LaTeX using Pandoc"""
        if not markdown or not _lazy_import_pypandoc():
            return self._markdown_to_latex_fallback(markdown)
        
        try:
            import pypandoc
            # Clean up markdown before conversion
            cleaned_markdown = self._clean_markdown_for_pandoc(markdown)
            
            # Use pandoc to convert Markdown to LaTeX
            latex = pypandoc.convert_text(
                cleaned_markdown, 
                'latex', 
                format='markdown',
                extra_args=[
                    '--wrap=none',  # Don't wrap lines
                    '--no-highlight',  # Disable syntax highlighting
                ]
            )
            
            # Post-process LaTeX output
            latex = self._clean_latex_output(latex)
            return latex.strip()
        except Exception as e:
            print(f"Pandoc Markdown conversion failed: {e}, falling back to manual conversion")
            return self._markdown_to_latex_fallback(markdown)
    
    def _html_to_latex_fallback(self, html: str) -> str:
        """Convert HTML to LaTeX using basic text processing (fallback)"""
        if not html:
            return ""
            
        # Remove HTML tags and convert basic formatting
        latex = html
        
        # Convert headers
        latex = re.sub(r'<h([1-6])[^>]*>(.*?)</h[1-6]>', self._convert_header, latex)
        
        # Convert paragraphs
        latex = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', latex)
        
        # Convert emphasis
        latex = re.sub(r'<strong[^>]*>(.*?)</strong>', r'\\textbf{\1}', latex)
        latex = re.sub(r'<em[^>]*>(.*?)</em>', r'\\textit{\1}', latex)
        
        # Convert links
        latex = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'\\href{\1}{\2}', latex)
        
        # Convert lists
        latex = re.sub(r'<ul[^>]*>(.*?)</ul>', self._convert_ul_list, latex, flags=re.DOTALL)
        latex = re.sub(r'<ol[^>]*>(.*?)</ol>', self._convert_ol_list, latex, flags=re.DOTALL)
        
        # Convert blockquotes
        latex = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'\\begin{quote}\1\\end{quote}', latex, flags=re.DOTALL)
        
        # Remove remaining HTML tags
        latex = re.sub(r'<[^>]+>', '', latex)
        
        # Clean up whitespace
        latex = re.sub(r'\n\s*\n', '\n\n', latex)
        
        # DO NOT escape LaTeX commands - this is already LaTeX content
        return latex.strip()
    
    def _convert_header(self, match) -> str:
        """Convert HTML header to LaTeX"""
        level = int(match.group(1))
        text = match.group(2)
        
        if level == 1:
            return f"\\section{{{text}}}"
        elif level == 2:
            return f"\\subsection{{{text}}}"
        elif level == 3:
            return f"\\subsubsection{{{text}}}"
        else:
            return f"\\textbf{{{text}}}"
    
    def _convert_ul_list(self, match) -> str:
        """Convert HTML unordered list to LaTeX"""
        content = match.group(1)
        items = re.findall(r'<li[^>]*>(.*?)</li>', content, re.DOTALL)
        
        latex_items = [f"\\item {item.strip()}" for item in items]
        return f"\\begin{{itemize}}\n{chr(10).join(latex_items)}\n\\end{{itemize}}"
    
    def _convert_ol_list(self, match) -> str:
        """Convert HTML ordered list to LaTeX"""
        content = match.group(1)
        items = re.findall(r'<li[^>]*>(.*?)</li>', content, re.DOTALL)
        
        latex_items = [f"\\item {item.strip()}" for item in items]
        return f"\\begin{{enumerate}}\n{chr(10).join(latex_items)}\n\\end{{enumerate}}"
    
    def _markdown_to_latex_fallback(self, markdown: str) -> str:
        """Convert Markdown to LaTeX (fallback method)"""
        if not markdown:
            return ""
            
        latex = markdown
        
        # Convert headers
        latex = re.sub(r'^### (.*$)', r'\\subsubsection{\1}', latex, flags=re.MULTILINE)
        latex = re.sub(r'^## (.*$)', r'\\subsection{\1}', latex, flags=re.MULTILINE)
        latex = re.sub(r'^# (.*$)', r'\\section{\1}', latex, flags=re.MULTILINE)
        
        # Convert emphasis
        latex = re.sub(r'\*\*([^*]+)\*\*', r'\\textbf{\1}', latex)
        latex = re.sub(r'\*([^*]+)\*', r'\\textit{\1}', latex)
        
        # Convert code
        latex = re.sub(r'`([^`]+)`', r'\\texttt{\1}', latex)
        
        # DO NOT escape LaTeX commands - this is already LaTeX content
        return latex.strip()
    
    async def _download_image_async(self, image_path: str) -> Optional[str]:
        """Download image from Educative using async aiohttp with proper authentication and MIME detection"""
        if not image_path or not self.images_dir:
            return None
            
        # Debug: Check if hierarchical context is set
        print(f"DEBUG: Async download context - Chapter: {self.current_chapter_number}, Section: {self.current_section_id}")
            
        try:
            # Construct full URL - always prepend https://www.educative.io
            if image_path.startswith('/'):
                url = f"https://www.educative.io{image_path}"
            elif image_path.startswith('http'):
                url = image_path
            else:
                url = f"https://www.educative.io/{image_path}"
                
            # Generate base filename without extension (we'll detect from MIME type)
            parsed_url = urlparse(url)
            base_filename = os.path.basename(parsed_url.path)
            if not base_filename:
                base_filename = f"image_{abs(hash(url))}"
            else:
                # Remove any existing extension to detect the real format from MIME
                base_filename = os.path.splitext(base_filename)[0]
                
            # Use the same headers as API requests for consistency + session cookies
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept": "image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Sec-Ch-Ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "image",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "same-origin",
                "Referer": "https://www.educative.io/",
            }
            
            # Add Educative session cookies for authentication
            cookie = os.getenv("EDUCATIVE_COOKIE")
            if cookie:
                headers["Cookie"] = cookie
            
            print(f"Downloading image: {url}")
            
            # Use aiohttp for async download
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    
                    # Detect file format from Content-Type header
                    content_type = response.headers.get('content-type', '').lower()
                    file_extension = self._get_extension_from_mime_type(content_type)
                    
                    print(f"Detected MIME type: {content_type} -> Extension: {file_extension}")
                    
                    # Create hierarchical directory structure: Images/chapter_X/section_Y/
                    if self.current_chapter_number and self.current_section_id:
                        chapter_dir = self.images_dir / f"chapter_{self.current_chapter_number}"
                        section_dir = chapter_dir / f"section_{self.current_section_id}"
                        section_dir.mkdir(parents=True, exist_ok=True)
                        target_dir = section_dir
                        # Relative path for LaTeX includes
                        filename = base_filename + file_extension
                        relative_image_path = f"Images/chapter_{self.current_chapter_number}/section_{self.current_section_id}/{filename}"
                        print(f"DEBUG: Using hierarchical image path: {relative_image_path}")
                    else:
                        # Fallback to old behavior if context not set
                        target_dir = self.images_dir
                        filename = base_filename + file_extension
                        relative_image_path = f"Images/{filename}"
                        print(f"DEBUG: Using flat image path (no context): {relative_image_path}")
                    
                    filepath = target_dir / filename
                    
                    # Skip if file already exists and is not empty
                    if filepath.exists() and filepath.stat().st_size > 0:
                        print(f"Image {filename} already exists, skipping download")
                        return relative_image_path
                    
                    # Download and save using aiofiles
                    content_data = await response.read()
                    
                    if not content_data:
                        print(f"Error: Image download returned empty content")
                        return None
                    
                    # Save the image asynchronously
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(content_data)
                    
                    # Verify the downloaded file
                    actual_size = filepath.stat().st_size
                    if actual_size == 0:
                        print(f"Error: Downloaded image file is empty")
                        filepath.unlink()  # Remove empty file
                        return None
                    
                    print(f"Successfully downloaded image: {filename} ({actual_size} bytes, MIME: {content_type})")
                    
                    # Additional validation for SVG files
                    if file_extension == ".svg":
                        try:
                            async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                                svg_content = await f.read()
                            if not svg_content.strip().startswith('<svg'):
                                print(f"Warning: SVG file doesn't start with <svg tag")
                        except Exception as e:
                            print(f"Warning: Could not validate SVG content: {e}")
                    
                    return relative_image_path
                    
        except aiohttp.ClientError as e:
            print(f"Network error downloading image {image_path}: {e}")
            return None
        except Exception as e:
            print(f"Failed to download image {image_path}: {e}")
            return None

    def _get_extension_from_mime_type(self, content_type: str) -> str:
        """Get file extension from MIME type"""
        mime_to_ext = {
            'image/png': '.png',
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/gif': '.gif',
            'image/svg+xml': '.svg',
            'image/webp': '.webp',
            'image/bmp': '.bmp',
            'image/tiff': '.tiff',
            'image/x-icon': '.ico',
            'application/pdf': '.pdf'
        }
        
        # Extract main MIME type (remove charset, etc.)
        main_type = content_type.split(';')[0].strip()
        
        extension = mime_to_ext.get(main_type, '.bin')
        print(f"MIME type '{main_type}' mapped to extension '{extension}'")
        
        return extension

    async def _convert_image_to_png(self, image_path: str) -> Optional[str]:
        """Convert any image format (SVG, WebP, GIF, etc.) to PNG for LaTeX compatibility"""
        if not image_path:
            return None
            
        file_ext = os.path.splitext(image_path)[1].lower()
        
        # If already PNG or JPG, no conversion needed (LaTeX handles these well)
        if file_ext in ['.png', '.jpg', '.jpeg']:
            print(f"INFO: Image {image_path} is already in LaTeX-compatible format")
            return image_path
            
        # Determine file paths
        if self.current_chapter_number and self.current_section_id:
            chapter_dir = self.images_dir / f"chapter_{self.current_chapter_number}"
            section_dir = chapter_dir / f"section_{self.current_section_id}"
            original_file_path = section_dir / os.path.basename(image_path)
            png_filename = os.path.splitext(os.path.basename(image_path))[0] + '.png'
            png_file_path = section_dir / png_filename
            png_relative_path = f"Images/chapter_{self.current_chapter_number}/section_{self.current_section_id}/{png_filename}"
        else:
            original_file_path = self.images_dir / os.path.basename(image_path)
            png_filename = os.path.splitext(os.path.basename(image_path))[0] + '.png'
            png_file_path = self.images_dir / png_filename
            png_relative_path = f"Images/{png_filename}"
        
        # Skip if PNG already exists
        if png_file_path.exists() and png_file_path.stat().st_size > 0:
            print(f"INFO: PNG version {png_filename} already exists, skipping conversion")
            return png_relative_path
            
        try:
            if file_ext == '.svg':
                # Try multiple SVG conversion methods in order of preference
                
                # Method 1: Try cairosvg (most reliable)
                if _lazy_import_cairosvg():
                    try:
                        import cairosvg
                        # Read SVG content and convert with cairosvg
                        async with aiofiles.open(original_file_path, 'r', encoding='utf-8') as f:
                            svg_content = await f.read()
                        
                        png_data = cairosvg.svg2png(
                            bytestring=svg_content.encode('utf-8'),
                            output_width=1200,  # Higher resolution for better quality
                            output_height=900
                        )
                        
                        async with aiofiles.open(png_file_path, 'wb') as f:
                            await f.write(png_data)
                        
                        print(f"✅ Successfully converted SVG to PNG using cairosvg: {png_filename}")
                        return png_relative_path
                    except Exception as e:
                        print(f"⚠️  cairosvg conversion failed: {e}, trying alternative methods...")
                
                # Method 2: Try Wand (ImageMagick) 
                if _lazy_import_wand():
                    try:
                        from wand.image import Image as WandImage
                        def convert_svg_with_wand():
                            with WandImage(filename=str(original_file_path)) as img:
                                img.format = 'png'
                                img.resize(1200, 900)  # High resolution for LaTeX
                                img.background_color = 'white'
                                img.alpha_channel = 'remove'
                                img.save(filename=str(png_file_path))
                        
                        # Run the conversion in a thread pool to avoid blocking
                        import asyncio
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(None, convert_svg_with_wand)
                        
                        if png_file_path.exists() and png_file_path.stat().st_size > 0:
                            print(f"✅ Successfully converted SVG to PNG using Wand: {png_filename}")
                            return png_relative_path
                        else:
                            print(f"⚠️ Wand conversion produced empty file, trying next method...")
                    except Exception as e:
                        print(f"⚠️ Wand conversion failed: {e}, trying fallback...")
                
                # Method 3: Try ImageMagick CLI
                try:
                    def convert_svg_with_imagemagick_cli():
                        import subprocess
                        result = subprocess.run([
                            'magick',
                            str(original_file_path),
                            '-resize', '1200x900',
                            '-background', 'white',
                            '-alpha', 'remove',
                            str(png_file_path)
                        ], capture_output=True, text=True, timeout=30)
                        
                        if result.returncode != 0:
                            raise Exception(f"ImageMagick CLI failed: {result.stderr}")
                    
                    # Run the conversion in a thread pool to avoid blocking
                    import asyncio
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, convert_svg_with_imagemagick_cli)
                    
                    if png_file_path.exists() and png_file_path.stat().st_size > 0:
                        print(f"✅ Successfully converted SVG to PNG using ImageMagick CLI: {png_filename}")
                        return png_relative_path
                    else:
                        print(f"⚠️ ImageMagick CLI conversion produced empty file, trying next method...")
                except Exception as e:
                    print(f"⚠️ ImageMagick CLI conversion failed: {e}, trying fallback...")
                
                # Method 4: Try Pillow with svg handling (limited but sometimes works)
                if _lazy_import_pil():
                    try:
                        from PIL import Image
                        def convert_svg_with_pillow():
                            # Try to open SVG with Pillow (requires pillow-simd or specific plugins)
                            with Image.open(original_file_path) as img:
                                # Convert to RGB if needed
                                if img.mode in ['RGBA', 'LA']:
                                    background = Image.new('RGB', img.size, (255, 255, 255))
                                    if img.mode == 'RGBA':
                                        background.paste(img, mask=img.split()[-1])
                                    else:
                                        background.paste(img, mask=img.split()[-1])
                                    img = background
                                elif img.mode not in ['RGB', 'L']:
                                    img = img.convert('RGB')
                                
                                img.save(png_file_path, 'PNG', optimize=True)
                        
                        import asyncio
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(None, convert_svg_with_pillow)
                        
                        print(f"✅ Successfully converted SVG to PNG using Pillow: {png_filename}")
                        return png_relative_path
                    except Exception as e:
                        print(f"⚠️  Pillow SVG conversion failed: {e}")
                
                # All conversion methods failed
                print("❌ All SVG conversion methods failed. SVG images will remain as SVG.")
                print("      Note: SVG files may not display properly in LaTeX PDFs.")
                return image_path
                
            elif file_ext in ['.webp', '.gif', '.bmp', '.tiff', '.ico']:
                # Handle other formats with Pillow
                if not _lazy_import_pil():
                    print(f"INFO: Pillow not available. {file_ext} images will remain in original format.")
                    print("      Note: Some image formats may not display properly in LaTeX PDFs.")
                    return image_path
                
                # Use Pillow to convert to PNG
                from PIL import Image
                def convert_to_png():
                    with Image.open(original_file_path) as img:
                        # Convert to RGB if necessary (for formats like GIF with transparency)
                        if img.mode in ['RGBA', 'LA']:
                            # Create white background for transparency
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'RGBA':
                                background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                            else:
                                background.paste(img, mask=img.split()[-1])
                            img = background
                        elif img.mode not in ['RGB', 'L']:
                            img = img.convert('RGB')
                        
                        # Save as PNG with high quality
                        img.save(png_file_path, 'PNG', optimize=True)
                
                # Run the conversion in a thread pool to avoid blocking
                import asyncio
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, convert_to_png)
                
                print(f"✅ Successfully converted {file_ext.upper()} to PNG: {png_filename}")
                return png_relative_path
            
            else:
                # Unknown format, return original
                print(f"INFO: Unknown image format {file_ext}, keeping original")
                return image_path
                
        except Exception as e:
            print(f"❌ Failed to convert {file_ext} to PNG: {e}")
            print(f"   Falling back to original image: {image_path}")
            return image_path

    def _download_image(self, image_path: str) -> Optional[str]:
        """Download image from Educative (LEGACY METHOD - Use _download_image_async instead)"""
        print("WARNING: Using legacy _download_image method. Consider using async version.")
        
        # For backward compatibility, run the async version
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._download_image_async(image_path))
        except Exception as e:
            print(f"Legacy image download failed: {e}")
            return None
    
    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters"""
        if not text:
            return ""
        
        # Escape backslash first to avoid double escaping
        text = text.replace('\\', r'\textbackslash{}')
        
        # LaTeX special characters that need escaping (excluding backslash)
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
        }
        
        for char, escaped in latex_special_chars.items():
            text = text.replace(char, escaped)
        
        return text
    
    def _clean_html_for_pandoc(self, html: str) -> str:
        """Clean HTML before pandoc conversion"""
        if not html:
            return ""
        
        # Remove empty tags that cause issues
        html = re.sub(r'<em>\s*</em>', '', html)
        html = re.sub(r'<strong>\s*</strong>', '', html)
        html = re.sub(r'<span[^>]*>\s*</span>', '', html)
        
        # Handle strikethrough properly
        html = re.sub(r'<del>(.*?)</del>', r'\\sout{\1}', html)
        html = re.sub(r'<s>(.*?)</s>', r'\\sout{\1}', html)
        
        return html
    
    def _clean_markdown_for_pandoc(self, markdown: str) -> str:
        """Clean Markdown before pandoc conversion"""
        if not markdown:
            return ""
        
        # Handle strikethrough
        markdown = re.sub(r'~~(.*?)~~', r'\\sout{\1}', markdown)
        
        # Clean up excessive newlines
        markdown = re.sub(r'\n\s*\n\s*\n+', '\n\n', markdown)
        
        return markdown
    
    def _clean_latex_output(self, latex: str) -> str:
        """Clean up LaTeX output from pandoc - DO NOT ESCAPE AGAIN"""
        if not latex:
            return ""
        
        # Remove empty emphasis tags and fix spacing
        latex = re.sub(r'\\emph\{\s*\}', ' ', latex)
        latex = re.sub(r'\\textbf\{\s*\}', ' ', latex)
        latex = re.sub(r'\\textit\{\s*\}', ' ', latex)
        
        # Handle strikethrough that pandoc might not process correctly
        latex = re.sub(r'~~([^~]+)~~', r'\\texttt{\1}', latex)
        
        # Fix missing spaces after periods followed by capital letters
        latex = re.sub(r'\.([A-Z])', r'. \1', latex)
        
        # Fix missing spaces after other punctuation
        latex = re.sub(r'([.!?])([A-Z])', r'\1 \2', latex)
        
        # Fix malformed texttt commands that contain other LaTeX commands
        latex = re.sub(r'\\texttt\{([^}]*\\[^}]*)\}', r'\1', latex)
        
        # Fix malformed href commands - comprehensive approach
        # Pattern 1: href with nested braces \\href{url{text}}
        latex = re.sub(r'\\href\{([^}]*)\{([^}]*)\}\}', r'\\href{\1}{\2}', latex)
        # Pattern 2: href missing text braces \\href{url}text (be more specific)
        latex = re.sub(r'\\href\{([^}]*)\}([a-zA-Z][^{\\}\s]*)', r'\\href{\1}{\2}', latex) 
        # Pattern 3: href with text but missing closing brace
        latex = re.sub(r'\\href\{([^}]*)\}\{([^}]*)}([^}])', r'\\href{\1}{\2}\3', latex)
        
        # Fix missing space issues specifically found in your content
        # "April 2008,I joined" -> "April 2008, I joined"
        latex = re.sub(r'(\d{4}),([A-Z])', r'\1, \2', latex)
        
        # "Azure. By the time" -> "Azure.\nBy the time" 
        latex = re.sub(r'(Azure\.)([A-Z])', r'\1 \2', latex)
        # Fix other missing spaces after punctuation
        latex = re.sub(r'([.!?,;:])([A-Z])', r'\1 \2', latex)
        
        # Fix specific problematic patterns from your content
        # "problem,---for example" -> "problem---for example"
        latex = re.sub(r',---', r'---', latex)
        
        # Fix "interview.Such" -> "interview. Such"
        latex = re.sub(r'\.([A-Z][a-z])', r'. \1', latex)
        
        # Clean up excessive whitespace and newlines
        latex = re.sub(r'\n\s*\n\s*\n+', '\n\n', latex)
        
        # Convert Windows-style line endings to Unix
        latex = latex.replace('\r\n', '\n')
        latex = latex.replace('\r', '')
        
        # Fix quote formatting
        latex = re.sub(r'\n\s*\n(?=\\begin\{quote\})', '\n', latex)
        latex = re.sub(r'(?<=\\end\{quote\})\n\s*\n', '\n', latex)
        
        # Fix spacing around sections
        latex = re.sub(r'\n\s*\n(?=\\subsection)', '\n\n', latex)
        latex = re.sub(r'\n\s*\n(?=\\subsubsection)', '\n\n', latex)
        
        # Ensure proper spacing after figures
        latex = re.sub(r'(\\end\{figure\})\s*\n\s*([A-Z])', r'\1\n\n\2', latex)
        
        # Break very long lines at natural sentence boundaries (more conservative approach)
        lines = latex.split('\n')
        processed_lines = []
        
        for line in lines:
            # Only process extremely long non-command lines (be more conservative)
            if (not line.strip().startswith('\\') and 
                len(line) > 150 and 
                not re.search(r'\\(sub)*section|\\begin|\\end|\\textbf|\\textit', line)):
                
                # Look for good breaking points: ". " followed by capital letter
                sentences = re.split(r'(\. [A-Z][a-z]+)', line)
                if len(sentences) > 2:
                    current_line = ""
                    for i, part in enumerate(sentences):
                        if i % 2 == 0:  # Main sentence content
                            if current_line and len(current_line + part) > 120:
                                # Break here if adding this part would make line too long
                                processed_lines.append(current_line.strip())
                                current_line = part
                            else:
                                current_line += part
                        else:  # Sentence boundary ". Word"
                            current_line += part
                    
                    if current_line.strip():
                        processed_lines.append(current_line.strip())
                else:
                    # No good breaking points found, keep as is
                    processed_lines.append(line)
            else:
                processed_lines.append(line)
        
        latex = '\n'.join(processed_lines)
        
        # Final cleanup: normalize multiple spaces to single spaces (but preserve line structure)
        latex = re.sub(r'[ \t]+', ' ', latex)  # Multiple spaces/tabs to single space
        latex = re.sub(r' +\n', '\n', latex)  # Remove trailing spaces
        latex = re.sub(r'\n +', '\n', latex)  # Remove leading spaces
        
        # IMPORTANT: Do NOT call _escape_latex here - pandoc output is already proper LaTeX
        return latex
