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
        self.author_id = None  # For LazyLoadPlaceholder API calls
        self.collection_id = None  # For LazyLoadPlaceholder API calls
        self.token = None  # Authentication token
        self.cookie = None  # Authentication cookie
        
    def set_book_context(self, book_name: str, chapter_number: int = None, section_id: str = None,
                        author_id: str = None, collection_id: str = None, token: str = None, cookie: str = None):
        """Set the context for a specific book, chapter, and section"""
        book_path = self.output_dir / book_name
        self.images_dir = book_path / "Images"  # Capital I to match existing structure
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Set current chapter and section for hierarchical organization
        self.current_chapter_number = chapter_number
        self.current_section_id = section_id
        
        # Set course IDs and credentials for API calls (e.g., LazyLoadPlaceholder)
        self.author_id = author_id
        self.collection_id = collection_id
        self.token = token
        self.cookie = cookie
        
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
                    
                elif component_type == "Quiz":
                    latex_content = self._process_quiz(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "Columns":
                    latex_content, images = await self._process_columns_async(component)
                    latex_parts.append(latex_content)
                    generated_images.extend(images)
                    
                elif component_type == "MarkMap":
                    latex_content = self._process_markmap(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "SpoilerEditor":
                    latex_content = self._process_spoiler_editor(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "Notepad":
                    latex_content = self._process_notepad(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "Table":
                    latex_content = self._process_table(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "TableHTML":
                    latex_content = self._process_table_html(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "Chart":
                    latex_content = self._process_chart(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "Latex":
                    latex_content = self._process_latex(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "Code":
                    latex_content = self._process_code(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "EditorCode":
                    latex_content = self._process_editor_code(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "TabbedCode":
                    latex_content = self._process_tabbed_code(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "LazyLoadPlaceholder":
                    latex_content, images = await self._process_lazy_load_placeholder_async(component)
                    latex_parts.append(latex_content)
                    generated_images.extend(images)
                    
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
                    
                elif component_type == "Quiz":
                    latex_content = self._process_quiz(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "Columns":
                    latex_content, images = self._process_columns(component)
                    latex_parts.append(latex_content)
                    generated_images.extend(images)
                    
                elif component_type == "MarkMap":
                    latex_content = self._process_markmap(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "SpoilerEditor":
                    latex_content = self._process_spoiler_editor(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "Notepad":
                    latex_content = self._process_notepad(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "Table":
                    latex_content = self._process_table(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "TableHTML":
                    latex_content = self._process_table_html(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "Chart":
                    latex_content = self._process_chart(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "Latex":
                    latex_content = self._process_latex(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "Code":
                    latex_content = self._process_code(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "EditorCode":
                    latex_content = self._process_editor_code(component)
                    latex_parts.append(latex_content)
                    
                elif component_type == "TabbedCode":
                    latex_content = self._process_tabbed_code(component)
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
        
        # IMPORTANT: Protect code blocks from text-processing fixes
        # Extract all lstlisting blocks and replace with placeholders
        import re
        code_blocks = []
        placeholder_pattern = "<<<CODE_BLOCK_{}>>>"
        
        def extract_code_block(match):
            code_blocks.append(match.group(0))
            return placeholder_pattern.format(len(code_blocks) - 1)
        
        # Extract lstlisting blocks (both with and without language parameter)
        latex_content = re.sub(
            r'\\begin\{lstlisting\}.*?\\end\{lstlisting\}',
            extract_code_block,
            latex_content,
            flags=re.DOTALL
        )
            
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
        
        # Restore code blocks with their original formatting intact
        for i, code_block in enumerate(code_blocks):
            placeholder = placeholder_pattern.format(i)
            latex_content = latex_content.replace(placeholder, code_block)
        
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
        
        # Check if this is a slides-enabled DrawIOWidget
        # Both slidesEnabled and isSlides must be true for slides mode
        slides_enabled = content.get("slidesEnabled", False)
        is_slides = content.get("isSlides", False)
        
        if slides_enabled and is_slides:
            # Handle as slider component
            return await self._process_drawio_slides_async(content)
        
        # Regular DrawIOWidget processing (non-slides)
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
    \\includegraphics[width=0.5\\textwidth]{{{converted_path}}}
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
    \\includegraphics[width=0.5\\textwidth]{{{image_relative_path}}}
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
    \\includegraphics[width=0.5\\textwidth]{{{converted_path}}}
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
    \\includegraphics[width=0.5\\textwidth]{{{image_relative_path}}}
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
    
    async def _process_drawio_slides_async(self, content: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Process DrawIOWidget with slides (multi-image slider)"""
        slides_id = content.get("slidesId")
        slides_captions = content.get("slidesCaption", [])
        editor_image_path = content.get("editorImagePath", "")
        
        if not slides_id:
            print(f"ERROR: Missing slidesId for DrawIOWidget slides")
            return "\\textit{DrawIOWidget slides missing slidesId}", []
        
        # Check if we have the required course IDs for constructing image URLs
        if not self.author_id or not self.collection_id:
            print(f"ERROR: author_id and collection_id not set in processor context")
            return "\\textit{DrawIOWidget slides requires course context}", []
        
        try:
            # Fetch slide data from Educative API
            slides_url = f"https://www.educative.io/api/slides/data?slides_id={slides_id}"
            
            print(f"DEBUG: Fetching DrawIOWidget slides from: {slides_url}")
            
            # Prepare headers with authentication
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
                "Referer": "https://www.educative.io/"
            }
            
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            if self.cookie:
                headers["Cookie"] = self.cookie
            
            # Fetch the slides data
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(slides_url, headers=headers)
                response.raise_for_status()
                slides_data = response.json()
            
            # Extract image IDs from the response
            image_ids = slides_data.get("image_ids", [])
            
            if not image_ids:
                print(f"WARNING: No image_ids found in slides response")
                return "\\textit{DrawIOWidget slides has no images}", []
            
            print(f"DEBUG: Found {len(image_ids)} slide images")
            
            # Extract page_id from editorImagePath if available
            # Format: /api/collection/{author}/{collection}/page/{page_id}/image/{image_id}?page_type=collection_lesson
            page_id = None
            if editor_image_path:
                import re
                match = re.search(r'/page/(\d+)/', editor_image_path)
                if match:
                    page_id = match.group(1)
                    print(f"DEBUG: Extracted page_id: {page_id} from editorImagePath")
            
            if not page_id:
                print(f"ERROR: Could not extract page_id from editorImagePath")
                return "\\textit{DrawIOWidget slides missing page_id}", []
            
            # Download and process all slide images
            generated_images = []
            processed_images = []
            
            for idx, image_id in enumerate(image_ids):
                try:
                    # Construct image URL
                    image_url = f"/api/collection/{self.author_id}/{self.collection_id}/page/{page_id}/image/{image_id}?page_type=collection_lesson"
                    
                    print(f"DEBUG: Downloading slide image {idx + 1}/{len(image_ids)}: {image_url}")
                    image_relative_path = await self._download_image_async(image_url)
                    
                    if image_relative_path:
                        generated_images.append(image_relative_path)
                        
                        # Convert to PNG if needed
                        converted_path = await self._convert_image_to_png(image_relative_path)
                        
                        if converted_path:
                            processed_images.append(converted_path)
                            print(f"✅ Slide image {idx + 1} processed: {converted_path}")
                        else:
                            processed_images.append(image_relative_path)
                            print(f"✅ Slide image {idx + 1} using original: {image_relative_path}")
                    else:
                        print(f"⚠️  Failed to download slide image {idx + 1}")
                        
                except Exception as e:
                    print(f"Error processing slide image {idx + 1}: {e}")
                    continue
            
            if not processed_images:
                return "\\textit{Failed to process DrawIOWidget slide images}", []
            
            # Generate LaTeX with subfigures (2 images per row)
            latex_parts = []
            
            for i in range(0, len(processed_images), 2):
                latex_parts.append("\\begin{figure}[htbp]")
                latex_parts.append("    \\centering")
                
                # First image in the row
                img1 = processed_images[i]
                caption1 = slides_captions[i] if i < len(slides_captions) else ""
                
                latex_parts.append("    \\begin{subfigure}[b]{0.48\\textwidth}")
                latex_parts.append("        \\centering")
                latex_parts.append(f"        \\includegraphics[width=\\textwidth]{{{img1}}}")
                if caption1:
                    latex_parts.append(f"        \\caption{{{self._escape_latex(caption1)}}}")
                latex_parts.append("    \\end{subfigure}")
                
                # Second image in the row (if exists)
                if i + 1 < len(processed_images):
                    latex_parts.append("    \\hfill")
                    img2 = processed_images[i + 1]
                    caption2 = slides_captions[i + 1] if i + 1 < len(slides_captions) else ""
                    
                    latex_parts.append("    \\begin{subfigure}[b]{0.48\\textwidth}")
                    latex_parts.append("        \\centering")
                    latex_parts.append(f"        \\includegraphics[width=\\textwidth]{{{img2}}}")
                    if caption2:
                        latex_parts.append(f"        \\caption{{{self._escape_latex(caption2)}}}")
                    latex_parts.append("    \\end{subfigure}")
                
                latex_parts.append("\\end{figure}")
                latex_parts.append("")  # Empty line between figures
            
            latex_content = "\n".join(latex_parts)
            
            print(f"✅ Generated LaTeX for DrawIOWidget slides with {len(processed_images)} images")
            return latex_content.strip(), processed_images
            
        except httpx.HTTPError as e:
            print(f"HTTP error fetching DrawIOWidget slides: {e}")
            return f"\\textit{{Error fetching DrawIOWidget slides: {str(e)}}}", []
        except Exception as e:
            print(f"Error processing DrawIOWidget slides: {e}")
            import traceback
            traceback.print_exc()
            return f"\\textit{{Error processing DrawIOWidget slides: {str(e)}}}", []
    
    async def _process_lazy_load_placeholder_async(self, component: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Process LazyLoadPlaceholder components (e.g., MxGraphWidget, CanvasAnimation)"""
        content = component.get("content", {})
        actual_type = content.get("actualType", "")
        
        print(f"DEBUG: Processing LazyLoadPlaceholder with actualType: {actual_type}")
        
        # Route to appropriate handler based on actualType
        if actual_type == "MxGraphWidget":
            return await self._process_mx_graph_widget_async(content)
        elif actual_type == "CanvasAnimation":
            return await self._process_canvas_animation_async(content)
        else:
            print(f"INFO: LazyLoadPlaceholder actualType '{actual_type}' not yet supported")
            return f"\\textit{{LazyLoadPlaceholder type '{actual_type}' not yet supported}}", []
    
    async def _process_mx_graph_widget_async(self, content: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Process MxGraphWidget from LazyLoadPlaceholder"""
        # Extract required parameters for API call
        page_id = content.get("pageId")
        content_revision = content.get("contentRevision")
        widget_index = content.get("widgetIndex")
        
        if not all([page_id, content_revision, widget_index]):
            print(f"ERROR: Missing required parameters for LazyLoadPlaceholder")
            return "\\textit{LazyLoadPlaceholder missing required parameters}", []
        
        # Check if we have the required course IDs and credentials
        if not self.author_id or not self.collection_id:
            print(f"ERROR: author_id and collection_id not set in processor context")
            return "\\textit{LazyLoadPlaceholder requires course context}", []
        
        try:
            # Construct API URL for fetching MxGraphWidget data
            # Format: /api/collection/{author_id}/{collection_id}/page/{page_id}/{content_revision}/{widget_index}?work_type=collection
            url = f"https://www.educative.io/api/collection/{self.author_id}/{self.collection_id}/page/{page_id}/{content_revision}/{widget_index}?work_type=collection"
            
            print(f"DEBUG: Fetching MxGraphWidget from: {url}")
            
            # Prepare headers with authentication
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
                "Referer": "https://www.educative.io/"
            }
            
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            if self.cookie:
                headers["Cookie"] = self.cookie
            
            # Fetch the MxGraphWidget data
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                widget_data = response.json()
            
            print(f"DEBUG: Successfully fetched MxGraphWidget data")
            
            # Extract the MxGraphWidget component from the response
            components = widget_data.get("components", [])
            if not components:
                print(f"WARNING: No components found in MxGraphWidget response")
                return "\\textit{MxGraphWidget data not available}", []
            
            # Get the first component (should be MxGraphWidget)
            mx_graph_component = components[0]
            mx_graph_type = mx_graph_component.get("type", "")
            
            if mx_graph_type != "MxGraphWidget":
                print(f"WARNING: Expected MxGraphWidget but got {mx_graph_type}")
                return f"\\textit{{Unexpected widget type: {mx_graph_type}}}", []
            
            # Extract image path and caption from MxGraphWidget content
            mx_content = mx_graph_component.get("content", {})
            image_path = mx_content.get("path", "")
            caption = mx_content.get("caption", "")
            
            if not image_path:
                print(f"WARNING: No image path found in MxGraphWidget")
                return "\\textit{MxGraphWidget image path not found}", []
            
            print(f"DEBUG: Found MxGraphWidget image path: {image_path}")
            
            # Download and process the image using existing infrastructure
            generated_images = []
            
            try:
                image_relative_path = await self._download_image_async(image_path)
                
                if image_relative_path:
                    generated_images.append(image_relative_path)
                    
                    # Convert to PNG if needed
                    converted_path = await self._convert_image_to_png(image_relative_path)
                    
                    if converted_path and converted_path != image_relative_path:
                        # Successfully converted to PNG
                        latex_content = f"""
\\begin{{figure}}[htbp]
    \\centering
    \\includegraphics[width=0.5\\textwidth]{{{converted_path}}}
    {f"\\caption{{{self._escape_latex(caption)}}}" if caption else ""}
\\end{{figure}}
"""
                        print(f"✅ Using converted PNG image for MxGraphWidget: {converted_path}")
                        return latex_content.strip(), [converted_path]
                    else:
                        # Use original image (PNG/JPG or conversion failed)
                        file_ext = os.path.splitext(image_relative_path)[1].lower()
                        if file_ext in ['.png', '.jpg', '.jpeg']:
                            latex_content = f"""
\\begin{{figure}}[htbp]
    \\centering
    \\includegraphics[width=0.5\\textwidth]{{{image_relative_path}}}
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
    \\textit{{[MxGraphWidget: {self._escape_latex(caption) if caption else 'Diagram'} - Format: {file_ext}]}}
    {f"\\caption{{{self._escape_latex(caption)}}}" if caption else ""}
\\end{{figure}}
"""
                            print(f"⚠️  Warning: Unsupported image format {file_ext} for LaTeX")
                        
                        return latex_content.strip(), generated_images
                        
            except Exception as e:
                print(f"Error processing MxGraphWidget image: {e}")
                return f"\\textit{{Error loading MxGraphWidget image: {str(e)}}}", []
        
        except httpx.HTTPError as e:
            print(f"HTTP error fetching MxGraphWidget: {e}")
            return f"\\textit{{Error fetching MxGraphWidget: {str(e)}}}", []
        except Exception as e:
            print(f"Error processing LazyLoadPlaceholder: {e}")
            return f"\\textit{{Error processing LazyLoadPlaceholder: {str(e)}}}", []
        
        return "\\textit{MxGraphWidget content not available}", []
    
    async def _process_canvas_animation_async(self, content: Dict[str, Any]) -> Tuple[str, List[str]]:
        """Process CanvasAnimation from LazyLoadPlaceholder (multi-image slider)"""
        # Extract required parameters for API call
        page_id = content.get("pageId")
        content_revision = content.get("contentRevision")
        widget_index = content.get("widgetIndex")
        slides_count = content.get("slidesCount", 0)
        
        if not all([page_id, content_revision, widget_index]):
            print(f"ERROR: Missing required parameters for CanvasAnimation")
            return "\\textit{CanvasAnimation missing required parameters}", []
        
        # Check if we have the required course IDs and credentials
        if not self.author_id or not self.collection_id:
            print(f"ERROR: author_id and collection_id not set in processor context")
            return "\\textit{CanvasAnimation requires course context}", []
        
        try:
            # Construct API URL for fetching CanvasAnimation data
            url = f"https://www.educative.io/api/collection/{self.author_id}/{self.collection_id}/page/{page_id}/{content_revision}/{widget_index}?work_type=collection"
            
            print(f"DEBUG: Fetching CanvasAnimation from: {url}")
            print(f"DEBUG: Expected slides count: {slides_count}")
            
            # Prepare headers with authentication
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
                "Referer": "https://www.educative.io/"
            }
            
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            if self.cookie:
                headers["Cookie"] = self.cookie
            
            # Fetch the CanvasAnimation data
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                widget_data = response.json()
            
            print(f"DEBUG: Successfully fetched CanvasAnimation data")
            
            # Extract the CanvasAnimation component from the response
            components = widget_data.get("components", [])
            if not components:
                print(f"WARNING: No components found in CanvasAnimation response")
                return "\\textit{CanvasAnimation data not available}", []
            
            # Get the first component (should be CanvasAnimation)
            canvas_component = components[0]
            canvas_type = canvas_component.get("type", "")
            
            if canvas_type != "CanvasAnimation":
                print(f"WARNING: Expected CanvasAnimation but got {canvas_type}")
                return f"\\textit{{Unexpected widget type: {canvas_type}}}", []
            
            # Extract canvas objects from CanvasAnimation content
            canvas_content = canvas_component.get("content", {})
            canvas_objects = canvas_content.get("canvasObjects", [])
            
            if not canvas_objects:
                print(f"WARNING: No canvas objects found in CanvasAnimation")
                return "\\textit{CanvasAnimation has no canvas objects}", []
            
            print(f"DEBUG: Found {len(canvas_objects)} canvas objects")
            
            # Extract image paths from all canvas objects
            image_paths = []
            captions = []
            
            for idx, canvas_obj in enumerate(canvas_objects):
                objects_dict = canvas_obj.get("objectsDict", {})
                caption = canvas_obj.get("caption", "")
                
                # Look for the educativeObjContent with MxGraph or DrawIO type
                for key, obj_data in objects_dict.items():
                    educative_content = obj_data.get("educativeObjContent", {})
                    content_type = educative_content.get("type", "")
                    
                    # Handle both MxGraph and DrawIO types (structure is the same)
                    if content_type in ["MxGraph", "DrawIO"]:
                        content_data = educative_content.get("content", {})
                        image_path = content_data.get("path", "")
                        
                        if image_path:
                            image_paths.append(image_path)
                            captions.append(caption)
                            print(f"DEBUG: Canvas object {idx + 1} ({content_type}): Found image path: {image_path}")
                            break
            
            if not image_paths:
                print(f"WARNING: No image paths found in CanvasAnimation canvas objects")
                return "\\textit{CanvasAnimation has no extractable images}", []
            
            print(f"DEBUG: Extracted {len(image_paths)} image paths from CanvasAnimation")
            
            # Download and process all images
            generated_images = []
            processed_images = []
            
            for idx, image_path in enumerate(image_paths):
                try:
                    print(f"DEBUG: Downloading canvas image {idx + 1}/{len(image_paths)}: {image_path}")
                    image_relative_path = await self._download_image_async(image_path)
                    
                    if image_relative_path:
                        generated_images.append(image_relative_path)
                        
                        # Convert to PNG if needed
                        converted_path = await self._convert_image_to_png(image_relative_path)
                        
                        if converted_path:
                            processed_images.append(converted_path)
                            print(f"✅ Canvas image {idx + 1} processed: {converted_path}")
                        else:
                            processed_images.append(image_relative_path)
                            print(f"✅ Canvas image {idx + 1} using original: {image_relative_path}")
                    else:
                        print(f"⚠️  Failed to download canvas image {idx + 1}")
                        
                except Exception as e:
                    print(f"Error processing canvas image {idx + 1}: {e}")
                    continue
            
            if not processed_images:
                return "\\textit{Failed to process CanvasAnimation images}", []
            
            # Generate LaTeX with subfigures (2 images per row)
            latex_parts = []
            
            for i in range(0, len(processed_images), 2):
                latex_parts.append("\\begin{figure}[htbp]")
                latex_parts.append("    \\centering")
                
                # First image in the row
                img1 = processed_images[i]
                caption1 = captions[i] if i < len(captions) else ""
                
                latex_parts.append("    \\begin{subfigure}[b]{0.48\\textwidth}")
                latex_parts.append("        \\centering")
                latex_parts.append(f"        \\includegraphics[width=\\textwidth]{{{img1}}}")
                if caption1:
                    latex_parts.append(f"        \\caption{{{self._escape_latex(caption1)}}}")
                latex_parts.append("    \\end{subfigure}")
                
                # Second image in the row (if exists)
                if i + 1 < len(processed_images):
                    latex_parts.append("    \\hfill")
                    img2 = processed_images[i + 1]
                    caption2 = captions[i + 1] if i + 1 < len(captions) else ""
                    
                    latex_parts.append("    \\begin{subfigure}[b]{0.48\\textwidth}")
                    latex_parts.append("        \\centering")
                    latex_parts.append(f"        \\includegraphics[width=\\textwidth]{{{img2}}}")
                    if caption2:
                        latex_parts.append(f"        \\caption{{{self._escape_latex(caption2)}}}")
                    latex_parts.append("    \\end{subfigure}")
                
                latex_parts.append("\\end{figure}")
                latex_parts.append("")  # Empty line between figures
            
            latex_content = "\n".join(latex_parts)
            
            print(f"✅ Generated LaTeX for CanvasAnimation with {len(processed_images)} images")
            return latex_content.strip(), processed_images
            
        except httpx.HTTPError as e:
            print(f"HTTP error fetching CanvasAnimation: {e}")
            return f"\\textit{{Error fetching CanvasAnimation: {str(e)}}}", []
        except Exception as e:
            print(f"Error processing CanvasAnimation: {e}")
            import traceback
            traceback.print_exc()
            return f"\\textit{{Error processing CanvasAnimation: {str(e)}}}", []
    
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
    
    def _process_quiz(self, component: Dict[str, Any]) -> str:
        """Process Quiz components with multiple-choice questions"""
        content = component.get("content", {})
        questions = content.get("questions", [])
        title = content.get("title", "").strip()
        
        if not questions:
            return ""
        
        latex_parts = []
        
        # Add quiz title if present
        if title:
            latex_parts.append(f"\\subsection*{{{self._escape_latex(title)}}}")
        else:
            latex_parts.append("\\subsection*{Quiz}")
        
        # Process each question
        for q_idx, question in enumerate(questions, 1):
            question_text_html = question.get("questionTextHtml", "").strip()
            question_text = question.get("questionText", "").strip()
            question_options = question.get("questionOptions", [])
            multiple_answers = question.get("multipleAnswers", False)
            
            if not question_text_html and not question_text:
                continue
            
            # Start question block
            latex_parts.append("\\vspace{0.3cm}")
            latex_parts.append("\\noindent")
            
            # Convert question text from HTML to LaTeX
            if question_text_html:
                q_latex = self._html_to_latex_pandoc(question_text_html)
                latex_parts.append(f"\\textbf{{Question {q_idx}:}} {q_latex.strip()}")
            else:
                latex_parts.append(f"\\textbf{{Question {q_idx}:}} {self._escape_latex(question_text)}")
            
            # Add hint for multiple answers
            if multiple_answers:
                latex_parts.append("\\\\")
                latex_parts.append("\\textit{(Select all that apply.)}")
            
            # Process answer options
            if question_options:
                latex_parts.append("\\\\[0.2cm]")
                latex_parts.append("\\begin{itemize}")
                
                for opt_idx, option in enumerate(question_options):
                    option_text_html = option.get("mdHtml", "").strip()
                    option_text = option.get("text", "").strip()
                    is_correct = option.get("correct", False)
                    explanation = option.get("explanation", {})
                    explanation_html = explanation.get("mdHtml", "").strip() if isinstance(explanation, dict) else ""
                    explanation_text = explanation.get("mdText", "").strip() if isinstance(explanation, dict) else ""
                    
                    # Convert option text from HTML to LaTeX
                    if option_text_html:
                        opt_latex = self._html_to_latex_pandoc(option_text_html)
                    else:
                        opt_latex = self._escape_latex(option_text)
                    
                    # Mark correct answers
                    if is_correct:
                        latex_parts.append(f"    \\item \\textbf{{[CORRECT]}} {opt_latex.strip()}")
                    else:
                        latex_parts.append(f"    \\item {opt_latex.strip()}")
                    
                    # Add explanation if present
                    if explanation_html or explanation_text:
                        latex_parts.append("\\\\[0.1cm]")
                        latex_parts.append("\\textit{Explanation:} ")
                        if explanation_html:
                            exp_latex = self._html_to_latex_pandoc(explanation_html)
                            latex_parts.append(exp_latex.strip())
                        else:
                            latex_parts.append(self._escape_latex(explanation_text))
                
                latex_parts.append("\\end{itemize}")
        
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
% \\vspace{{-1.0\\baselineskip}}
\\noindent
\\begin{{minipage}}[t]{{0.48\\textwidth}}\\vspace{{0pt}}
{clean_content_0}
\\end{{minipage}}
\\hfill
\\begin{{minipage}}[t]{{0.48\\textwidth}}\\vspace{{0pt}}
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
                latex_parts.append(f"""\\begin{{minipage}}[t]{{{col_width:.2f}\\textwidth}}\\vspace{{0pt}}
{clean_content}
\\end{{minipage}}""")
            
            latex_output = f"""
% \\vspace{{-1.0\\baselineskip}}
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
% \\vspace{{-1.0\\baselineskip}}
\\noindent
\\begin{{minipage}}[t]{{0.48\\textwidth}}\\vspace{{0pt}}
{clean_content_0}
\\end{{minipage}}
\\hfill
\\begin{{minipage}}[t]{{0.48\\textwidth}}\\vspace{{0pt}}
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
                latex_parts.append(f"""\\begin{{minipage}}[t]{{{col_width:.2f}\\textwidth}}\\vspace{{0pt}}
{clean_content}
\\end{{minipage}}""")
            
            latex_output = f"""
\\noindent
{chr(10).join(latex_parts)}
"""
        
        return latex_output.strip(), generated_images
    
    def _clean_content_for_minipage(self, content: str) -> str:
        """Clean content to avoid nested figure environments in minipages and ensure top alignment"""
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
            has_includegraphics = False
            
            for line in lines:
                line = line.strip()
                # Skip centering and empty lines
                if line == '\\centering' or not line:
                    continue
                # Keep includegraphics and caption
                if '\\includegraphics' in line:
                    cleaned_lines.append(line)
                    has_includegraphics = True
                elif '\\caption' in line:
                    cleaned_lines.append(line)
            
            if cleaned_lines:
                # If there's an includegraphics, center it
                # (vspace is now handled at minipage level)
                if has_includegraphics:
                    return '\\centering\n' + '\n'.join(cleaned_lines)
                else:
                    return '\n'.join(cleaned_lines)
            else:
                return ''
        
        # Apply the replacement
        cleaned_content = re.sub(figure_pattern, replace_figure, content, flags=re.DOTALL)
        
        # Additional check: if content starts with \includegraphics (no figure wrapper)
        # add centering command
        cleaned_content = cleaned_content.strip()
        if cleaned_content.startswith('\\includegraphics'):
            cleaned_content = '\\centering\n' + cleaned_content
        
        return cleaned_content
    
    def _process_markmap(self, component: Dict[str, Any]) -> str:
        """
        Process MarkMap components - creates a placeholder with content summary
        
        MarkMaps are interactive JavaScript-based visualizations that cannot be directly
        converted to static LaTeX/PDF. This method creates a placeholder box followed by
        a structured text representation of the mind map content.
        """
        content = component.get("content", {})
        
        # Extract text content and caption
        text = content.get("text", "")
        caption = content.get("caption", "")
        
        result = []
        
        # Create a framed box placeholder for the mind map
        result.append("\\begin{center}")
        result.append("\\fbox{\\begin{minipage}{0.9\\textwidth}")
        result.append("\\centering")
        result.append("\\vspace{0.2cm}")
        
        if caption:
            result.append(f"\\textbf{{\\large {self._escape_latex(caption)}}}")
            result.append("\\\\[0.2cm]")
        
        result.append("\\textit{[Interactive Mind Map - See online version for interactive visualization]}")
        result.append("\\vspace{0.2cm}")
        result.append("\\end{minipage}}")
        result.append("\\end{center}")
        result.append("")
        
        # If there's text content, add a structured representation below the placeholder
        if text and text.strip():
            result.append("\\vspace{0.3cm}")
            content_latex = self._markmap_text_to_latex(text)
            result.append(content_latex)
        
        return '\n'.join(result)
    
    def _process_spoiler_editor(self, component: Dict[str, Any]) -> str:
        """
        Process SpoilerEditor components - renders as a simple text block
        
        SpoilerEditor is used for collapsible content (like solutions or hints).
        In LaTeX, we simply render the text content directly without special formatting.
        """
        content = component.get("content", {})
        text = content.get("text", "")
        
        if not text or not text.strip():
            return ""
        
        # Convert the text to LaTeX using Pandoc
        latex_content = self._markdown_to_latex_pandoc(text)
        
        return latex_content
    
    def _process_notepad(self, component: Dict[str, Any]) -> str:
        """
        Process Notepad components - extracts question from title and answer from systemPrompt
        
        Notepad is used for AI-assisted learning exercises where:
        - title contains the question/prompt
        - systemPrompt contains the REFERENCE ANSWER section
        """
        content = component.get("content", {})
        title = content.get("title", "")
        system_prompt = content.get("systemPrompt", "")
        
        result = []
        
        # Extract and format the question from title
        if title and title.strip():
            result.append("\\textbf{Question:}")
            result.append("")
            # Convert title to LaTeX (escape special characters)
            result.append(self._escape_latex(title))
            result.append("")
        
        # Extract REFERENCE ANSWER from systemPrompt
        if system_prompt:
            # Look for the REFERENCE ANSWER section
            answer_match = re.search(r'#\s*REFERENCE\s+ANSWER\s*\n(.+?)(?=\n#|$)', 
                                    system_prompt, 
                                    re.DOTALL | re.IGNORECASE)
            
            if answer_match:
                answer_text = answer_match.group(1).strip()
                
                if answer_text:
                    result.append("\\textbf{Reference Answer:}")
                    result.append("")
                    
                    # Fix markdown formatting: ensure blank line before numbered/bulleted lists
                    # This is required for Pandoc to recognize them as proper lists
                    # Only add blank line before the FIRST item (1. or * or -)
                    answer_text = re.sub(r'([^\n])\n(1\.\s)', r'\1\n\n\2', answer_text)
                    answer_text = re.sub(r'([^\n])\n([*-]\s[^\n])', r'\1\n\n\2', answer_text, count=1)
                    
                    # Convert markdown answer to LaTeX using Pandoc
                    # Pandoc will properly format numbered lists as enumerate environments
                    latex_answer = self._markdown_to_latex_pandoc(answer_text)
                    
                    # Ensure proper spacing around list environments
                    # Add blank line before enumerate/itemize if not present
                    latex_answer = re.sub(r'([^\n])\n(\\begin\{enumerate\}|\\begin\{itemize\})', 
                                         r'\1\n\n\2', latex_answer)
                    # Add blank line after enumerate/itemize if not present
                    latex_answer = re.sub(r'(\\end\{enumerate\}|\\end\{itemize\})\n([^\n])', 
                                         r'\1\n\n\2', latex_answer)
                    
                    result.append(latex_answer)
        
        # If no content was extracted, return empty
        if not result:
            return ""
        
        return '\n'.join(result)
    
    def _process_table(self, component: Dict[str, Any]) -> str:
        """
        Process Table components - converts Educative table data to LaTeX tabular format
        
        Table structure from backend:
        - numberOfRows, numberOfColumns: dimensions
        - columnWidths: array of column widths (for reference)
        - data: 2D array where each cell contains HTML content
        - template: table style template (1 = header row style)
        - title: optional table title
        """
        content = component.get("content", {})
        
        # Extract table metadata
        num_rows = content.get("numberOfRows", 0)
        num_cols = content.get("numberOfColumns", 0)
        data = content.get("data", [])
        title = content.get("title", "")
        template = content.get("template", 0)
        column_widths = content.get("columnWidths", [])
        
        if not data or num_rows == 0 or num_cols == 0:
            return "\\textit{Empty table}"
        
        result = []
        
        # Add title if present
        if title and title.strip():
            result.append(f"\\textbf{{{self._escape_latex(title)}}}")
            result.append("")
        
        # Calculate column widths as proportions of text width
        # Use columnWidths from backend if available, otherwise distribute equally
        if column_widths and len(column_widths) == num_cols:
            total_width = sum(column_widths)
            # Convert to proportions of \textwidth (leave some margin)
            col_proportions = [w / total_width * 0.95 for w in column_widths]
        else:
            # Equal distribution
            col_proportions = [0.95 / num_cols] * num_cols
        
        # Use p{width} columns for automatic text wrapping
        # This prevents tables from exceeding page width
        col_spec = "|" + "|".join([f"p{{{prop:.3f}\\textwidth}}" for prop in col_proportions]) + "|"
        
        # Start table environment with adjustbox for additional safety
        result.append("\\begin{table}[htbp]")
        result.append("\\centering")
        result.append("\\small")  # Use smaller font for better fit
        # Use adjustbox to scale down if still too wide
        result.append("\\adjustbox{max width=\\textwidth}{")
        result.append(f"\\begin{{tabular}}{{{col_spec}}}")
        result.append("\\hline")
        
        # Process each row
        for row_idx, row in enumerate(data):
            if row_idx >= num_rows:
                break
            
            # Process each cell in the row
            processed_cells = []
            for col_idx, cell_html in enumerate(row):
                if col_idx >= num_cols:
                    break
                
                # Convert HTML cell content to LaTeX
                cell_latex = self._process_table_cell(cell_html)
                processed_cells.append(cell_latex)
            
            # Join cells with & separator
            row_latex = " & ".join(processed_cells)
            result.append(row_latex + " \\\\")
            
            # Add horizontal line after each row
            # For template=1, add thicker line after first row (header)
            if row_idx == 0 and template == 1:
                result.append("\\hline")
                result.append("\\hline")  # Double line after header
            else:
                result.append("\\hline")
        
        # End table environment
        result.append("\\end{tabular}")
        result.append("}")  # Close adjustbox
        
        # Add caption if title exists
        if title and title.strip():
            result.append(f"\\caption{{{self._escape_latex(title)}}}")
        
        result.append("\\end{table}")
        
        return '\n'.join(result)
    
    def _process_table_html(self, component: Dict[str, Any]) -> str:
        """
        Process TableHTML components - converts HTML table to LaTeX format
        
        TableHTML structure from backend:
        - content.type: "TableV2"
        - content.html: HTML representation of the table
        - content.children: Structured data representation (not used here)
        
        We use the HTML representation and convert it to LaTeX using pandoc.
        """
        content = component.get("content", {})
        
        # Extract HTML content
        html_content = content.get("html", "")
        
        if not html_content or not html_content.strip():
            return "\\textit{Empty table}"
        
        # Convert HTML to LaTeX using pandoc
        try:
            latex_content = self._html_to_latex_pandoc(html_content)
            
            # Post-process the LaTeX to ensure it fits properly
            # Remove any excessive whitespace
            latex_content = latex_content.strip()
            
            # If the table doesn't have proper formatting, wrap it
            if latex_content and not latex_content.startswith("\\begin{"):
                latex_content = f"\\begin{{center}}\n{latex_content}\n\\end{{center}}"
            
            return latex_content
            
        except Exception as e:
            print(f"Error converting TableHTML to LaTeX: {e}")
            return f"\\textit{{Error processing table: {str(e)}}}"
    
    def _process_chart(self, component: Dict[str, Any]) -> str:
        """
        Process Chart components - converts chart data to LaTeX table format
        
        Since LaTeX PDFs don't easily support interactive charts without complex plotting libraries,
        we convert the chart data into a table representation that shows the data clearly.
        
        Chart structure from backend:
        - content.config: JSON string containing chart.js configuration
        - content.type: Chart type (e.g., 'line', 'bar', 'area')
        - content.caption: Chart caption/description
        
        The config contains:
        - type: Chart type (line, bar, pie, etc.)
        - data.labels: X-axis labels
        - data.datasets: Array of datasets with label, data, and styling
        - options.title.text: Chart title
        - options.scales: Axis configuration
        """
        content = component.get("content", {})
        config_str = content.get("config", "{}")
        caption = content.get("caption", "")
        chart_type = content.get("type", "")
        
        # Parse the chart configuration JSON
        try:
            config = json.loads(config_str)
        except json.JSONDecodeError as e:
            return f"\\textit{{Error parsing chart configuration: {str(e)}}}"
        
        # Extract chart data
        chart_data = config.get("data", {})
        labels = chart_data.get("labels", [])
        datasets = chart_data.get("datasets", [])
        
        # Extract chart options
        options = config.get("options", {})
        title_config = options.get("title", {})
        chart_title = title_config.get("text", "")
        
        # Extract axis labels
        scales = options.get("scales", {})
        x_axes = scales.get("xAxes", [{}])
        y_axes = scales.get("yAxes", [{}])
        x_label = x_axes[0].get("scaleLabel", {}).get("labelString", "") if x_axes else ""
        y_label = y_axes[0].get("scaleLabel", {}).get("labelString", "") if y_axes else ""
        
        if not labels or not datasets:
            return "\\textit{Chart data not available}"
        
        result = []
        
        # Add chart title if present
        if chart_title and chart_title.strip():
            result.append(f"\\textbf{{{self._escape_latex(chart_title)}}}")
            result.append("")
        
        # Add note about chart conversion
        result.append("\\textit{\\small [Chart data presented in table format]}")
        result.append("")
        
        # Calculate number of columns: 1 for labels + 1 per dataset
        num_cols = 1 + len(datasets)
        num_rows = len(labels)
        
        # Calculate column widths
        col_proportions = [0.95 / num_cols] * num_cols
        col_spec = "|" + "|".join([f"p{{{prop:.3f}\\textwidth}}" for prop in col_proportions]) + "|"
        
        # Start table environment
        result.append("\\begin{table}[htbp]")
        result.append("\\centering")
        result.append("\\small")
        result.append("\\adjustbox{max width=\\textwidth}{")
        result.append(f"\\begin{{tabular}}{{{col_spec}}}")
        result.append("\\hline")
        
        # Create header row
        header_cells = []
        
        # First column header (X-axis label or generic label)
        if x_label:
            header_cells.append(f"\\textbf{{{self._escape_latex(x_label)}}}")
        else:
            header_cells.append("\\textbf{Label}")
        
        # Add dataset labels as column headers
        for dataset in datasets:
            dataset_label = dataset.get("label", "Data")
            header_cells.append(f"\\textbf{{{self._escape_latex(dataset_label)}}}")
        
        result.append(" & ".join(header_cells) + " \\\\")
        result.append("\\hline")
        result.append("\\hline")  # Double line after header
        
        # Create data rows
        for i, label in enumerate(labels):
            row_cells = [self._escape_latex(str(label))]
            
            # Add data from each dataset
            for dataset in datasets:
                dataset_data = dataset.get("data", [])
                if i < len(dataset_data):
                    value = dataset_data[i]
                    row_cells.append(self._escape_latex(str(value)))
                else:
                    row_cells.append("-")
            
            result.append(" & ".join(row_cells) + " \\\\")
            result.append("\\hline")
        
        # End table environment
        result.append("\\end{tabular}")
        result.append("}")  # Close adjustbox
        
        # Add caption
        if caption and caption.strip():
            result.append(f"\\caption{{{self._escape_latex(caption)}}}")
        elif chart_title and chart_title.strip():
            result.append(f"\\caption{{{self._escape_latex(chart_title)}}}")
        
        # Add Y-axis label as a note if present
        if y_label:
            result.append(f"\\label{{tab:chart}}")
            result.append("")
            result.append(f"\\textit{{\\small Note: Values are in {self._escape_latex(y_label)}}}")
        
        result.append("\\end{table}")
        
        return '\n'.join(result)
    
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
        content = component.get("content", {})
        latex_text = content.get("text", "").strip()
        mode = content.get("mode", "edit")
        
        if not latex_text:
            return ""
        
        # Check if the equation is already wrapped in math delimiters
        has_display_math = latex_text.startswith("$$") or latex_text.startswith("\\[")
        has_inline_math = latex_text.startswith("$") and not has_display_math
        
        # If already wrapped, return as-is
        if has_display_math or has_inline_math:
            return latex_text
        
        # Otherwise, wrap in display math environment (equation block)
        # Use \[ \] for unnumbered display equations
        return f"\\[\n{latex_text}\n\\]"
    
    def _process_editor_code(self, component: Dict[str, Any]) -> str:
        """
        Process EditorCode components - renders inline code snippets
        
        The backend provides:
        - content.language: Programming language (e.g., 'python', 'javascript')
        - content.content: The actual code content
        - content.version: Version information
        - mode: 'edit' or 'view' mode
        
        Returns:
            LaTeX code listing with proper formatting
        """
        content = component.get("content", {})
        code_text = content.get("content", "")
        language = content.get("language", "").lower()
        
        if not code_text:
            return ""
        
        # Decode escape sequences if the string contains literal \n, \t, etc.
        # This handles cases where JSON escape sequences aren't properly interpreted
        if '\\n' in code_text or '\\t' in code_text:
            try:
                # Use encode().decode('unicode_escape') to interpret escape sequences
                code_text = code_text.encode().decode('unicode_escape')
            except:
                # If decoding fails, use the original text
                pass
        
        # Strip only after decoding to preserve internal whitespace
        code_text = code_text.strip()
        
        # Map Educative language names to listings package language names
        language_map = {
            'javascript': 'JavaScript',
            'python': 'Python',
            'python3': 'Python',
            'python2': 'Python',
            'java': 'Java',
            'cpp': 'C++',
            'c++': 'C++',
            'c': 'C',
            'csharp': 'C',
            'c#': 'C',
            'ruby': 'Ruby',
            'go': 'Go',
            'rust': 'Rust',
            'php': 'PHP',
            'swift': 'Swift',
            'kotlin': 'Kotlin',
            'typescript': 'JavaScript',
            'shell': 'bash',
            'bash': 'bash',
            'sql': 'SQL',
            'html': 'HTML',
            'css': 'CSS',
            'xml': 'XML',
            'json': 'JavaScript',
            'yaml': 'Python',
            'dockerfile': 'bash',
            'markdown': 'TeX',
        }
        
        # Get the listings language name
        listings_language = language_map.get(language, language)
        
        result = []
        
        # Create the code listing
        # Use lstlisting environment from listings package
        if listings_language:
            result.append(f"\\begin{{lstlisting}}[language={listings_language}]")
        else:
            result.append("\\begin{lstlisting}")
        
        result.append(code_text)
        result.append("\\end{lstlisting}")
        
        return '\n'.join(result)
    
    def _process_tabbed_code(self, component: Dict[str, Any]) -> str:
        """
        Process TabbedCode components - renders multi-language code snippets
        For now, only extract and display Java code, ignoring other languages.
        
        The backend provides:
        - content.codeContents: Array of code content objects for different languages
          Each object has:
          - title: Language name (e.g., 'Java', 'Python', 'C++')
          - language: Language identifier (e.g., 'java', 'python3', 'c++')
          - content: The actual code content
          - caption: Description/title of the code
        
        Returns:
            LaTeX code listing with Java code only
        """
        content = component.get("content", {})
        code_contents = content.get("codeContents", [])
        
        if not code_contents:
            return "\\textit{No code content available}"
        
        # Find Java code (look for title="Java" or language="java")
        java_code_obj = None
        for code_obj in code_contents:
            title = code_obj.get("title", "").lower()
            language = code_obj.get("language", "").lower()
            if title == "java" or language == "java":
                java_code_obj = code_obj
                break
        
        if not java_code_obj:
            # Fallback: use first available code if Java not found
            java_code_obj = code_contents[0]
        
        code_text = java_code_obj.get("content", "")
        caption = java_code_obj.get("caption", "")
        language = java_code_obj.get("language", "java").lower()
        
        if not code_text:
            return ""
        
        # Decode escape sequences if the string contains literal \n, \t, etc.
        # This handles cases where JSON escape sequences aren't properly interpreted
        if '\\n' in code_text or '\\t' in code_text:
            try:
                # Use encode().decode('unicode_escape') to interpret escape sequences
                code_text = code_text.encode().decode('unicode_escape')
            except:
                # If decoding fails, use the original text
                pass
        
        # Strip only after decoding to preserve internal whitespace
        code_text = code_text.strip()
        
        # Map language to listings package name
        language_map = {
            'java': 'Java',
            'python': 'Python',
            'python3': 'Python',
            'c++': 'C++',
            'cpp': 'C++',
            'c#': 'C',
            'csharp': 'C',
            'javascript': 'JavaScript',
            'javascript-es2024': 'JavaScript',
        }
        
        listings_language = language_map.get(language, 'Java')
        
        result = []
        
        # Add caption if available
        if caption:
            result.append(f"\\textbf{{{caption}}}\n")
        
        # Create the code listing
        result.append(f"\\begin{{lstlisting}}[language={listings_language}]")
        result.append(code_text)
        result.append("\\end{lstlisting}")
        
        return '\n'.join(result)
    
    def _process_code(self, component: Dict[str, Any]) -> str:
        """
        Process Code components - renders code blocks with syntax highlighting
        
        The backend provides:
        - content.caption: Description/title of the code
        - content.language: Programming language (e.g., 'python', 'javascript', 'shell')
        - content.content: The actual code content
        - content.mode: 'edit' or 'view' mode
        - content.runnable: Whether code is executable
        - content.showSolution: Whether to show solution
        
        Returns:
            LaTeX code listing with proper formatting
        """
        content = component.get("content", {})
        code_text = content.get("content", "")
        language = content.get("language", "").lower()
        caption = content.get("caption", "").strip()
        title = content.get("title", "").strip()
        
        if not code_text:
            return ""
        
        # Decode escape sequences if the string contains literal \n, \t, etc.
        # This handles cases where JSON escape sequences aren't properly interpreted
        if '\\n' in code_text or '\\t' in code_text:
            try:
                # Use encode().decode('unicode_escape') to interpret escape sequences
                code_text = code_text.encode().decode('unicode_escape')
            except:
                # If decoding fails, use the original text
                pass
        
        # Strip only after decoding to preserve internal whitespace
        code_text = code_text.strip()
        
        # Map Educative language names to listings package language names
        language_map = {
            'javascript': 'JavaScript',
            'python': 'Python',
            'python3': 'Python',  # Python 3 uses same highlighting as Python
            'python2': 'Python',  # Python 2 uses same highlighting as Python
            'java': 'Java',
            'cpp': 'C++',
            'c++': 'C++',
            'c': 'C',
            'csharp': 'C',  # listings doesn't have C# directly, use C
            'c#': 'C',
            'ruby': 'Ruby',
            'go': 'Go',
            'rust': 'Rust',
            'php': 'PHP',
            'swift': 'Swift',
            'kotlin': 'Kotlin',
            'typescript': 'JavaScript',  # Use JavaScript for TypeScript
            'shell': 'bash',
            'bash': 'bash',
            'sql': 'SQL',
            'html': 'HTML',
            'css': 'CSS',
            'xml': 'XML',
            'json': 'JavaScript',  # Use JavaScript for JSON
            'yaml': 'Python',  # Use Python for YAML
            'dockerfile': 'bash',
            'markdown': 'TeX',
        }
        
        # Get the listings language name
        listings_language = language_map.get(language, language)
        
        # Build the caption text
        caption_text = ""
        if caption:
            caption_text = caption
        elif title:
            caption_text = title
        
        # Escape special LaTeX characters in the code
        # For listings, we need to be careful with backslashes and braces
        # Use lstlisting with escapechar to handle special cases
        
        result = []
        
        # Add caption as a separate line if present
        if caption_text:
            result.append(f"\\textbf{{{self._escape_latex(caption_text)}}}")
            result.append("")
        
        # Create the code listing
        # Use lstlisting environment from listings package
        if listings_language:
            result.append(f"\\begin{{lstlisting}}[language={listings_language}]")
        else:
            result.append("\\begin{lstlisting}")
        
        result.append(code_text)
        result.append("\\end{lstlisting}")
        
        return '\n'.join(result)
    
    def _process_table_cell(self, cell_html: str) -> str:
        """
        Process individual table cell HTML content to LaTeX
        
        Handles:
        - HTML paragraph tags with alignment classes
        - Basic text formatting (bold, italic)
        - Nested HTML structures
        """
        if not cell_html or not cell_html.strip():
            return ""
        
        # Use pandoc to convert HTML to LaTeX if available
        if _lazy_import_pypandoc():
            try:
                import pypandoc
                # Convert HTML to LaTeX
                latex = pypandoc.convert_text(
                    cell_html,
                    'latex',
                    format='html',
                    extra_args=['--wrap=none']
                )
                
                # Clean up the output
                latex = latex.strip()
                
                # Remove paragraph breaks within cells (tables don't support \n\n)
                latex = latex.replace('\n\n', ' ')
                latex = latex.replace('\n', ' ')
                
                # Remove any stray paragraph commands
                latex = re.sub(r'\\par\s*', ' ', latex)
                
                # Clean up excessive spaces
                latex = re.sub(r'\s+', ' ', latex)
                
                return latex.strip()
                
            except Exception as e:
                print(f"Warning: Pandoc table cell conversion failed: {e}, using fallback")
        
        # Fallback: manual HTML processing
        cell_text = cell_html
        
        # Remove paragraph tags and extract text
        cell_text = re.sub(r'<p[^>]*class="ql-align-center"[^>]*>(.*?)</p>', r'\\centering \1', cell_text, flags=re.DOTALL)
        cell_text = re.sub(r'<p[^>]*class="ql-align-right"[^>]*>(.*?)</p>', r'\\raggedleft \1', cell_text, flags=re.DOTALL)
        cell_text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1', cell_text, flags=re.DOTALL)
        
        # Convert basic formatting
        cell_text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'\\textbf{\1}', cell_text, flags=re.DOTALL)
        cell_text = re.sub(r'<b[^>]*>(.*?)</b>', r'\\textbf{\1}', cell_text, flags=re.DOTALL)
        cell_text = re.sub(r'<em[^>]*>(.*?)</em>', r'\\textit{\1}', cell_text, flags=re.DOTALL)
        cell_text = re.sub(r'<i[^>]*>(.*?)</i>', r'\\textit{\1}', cell_text, flags=re.DOTALL)
        cell_text = re.sub(r'<code[^>]*>(.*?)</code>', r'\\texttt{\1}', cell_text, flags=re.DOTALL)
        
        # Remove remaining HTML tags
        cell_text = re.sub(r'<[^>]+>', '', cell_text)
        
        # Clean up whitespace
        cell_text = re.sub(r'\s+', ' ', cell_text)
        cell_text = cell_text.strip()
        
        # Escape LaTeX special characters (but preserve LaTeX commands we just added)
        # This is tricky - we need to escape user content but not our LaTeX commands
        # Simple approach: only escape if not part of a LaTeX command
        cell_text = self._escape_latex_in_text(cell_text)
        
        return cell_text
    
    def _escape_latex_in_text(self, text: str) -> str:
        """
        Escape LaTeX special characters in text while preserving LaTeX commands
        This is a smart escape that doesn't break existing LaTeX commands
        """
        if not text:
            return ""
        
        # Split by LaTeX commands to preserve them
        parts = re.split(r'(\\[a-zA-Z]+\{[^}]*\}|\\[a-zA-Z]+)', text)
        
        escaped_parts = []
        for i, part in enumerate(parts):
            # If this is a LaTeX command (odd indices after split), keep it as-is
            if i % 2 == 1 or part.startswith('\\'):
                escaped_parts.append(part)
            else:
                # This is regular text, escape it
                escaped_part = part
                # Only escape characters that aren't already escaped
                escaped_part = escaped_part.replace('&', r'\&')
                escaped_part = escaped_part.replace('%', r'\%')
                escaped_part = escaped_part.replace('$', r'\$')
                escaped_part = escaped_part.replace('#', r'\#')
                escaped_part = escaped_part.replace('_', r'\_')
                # Note: We don't escape { } here as they might be part of LaTeX commands
                escaped_parts.append(escaped_part)
        
        return ''.join(escaped_parts)
    
    def _markmap_to_simple_tree(self, text: str, caption: str = "") -> str:
        """
        Convert MarkMap markdown to a simple indented tree structure
        This provides a text-based representation of the mind map hierarchy
        """
        lines = text.strip().split('\n')
        result = []
        
        # Add caption if provided
        if caption:
            result.append(f"\\textbf{{{self._escape_latex(caption)}}}")
            result.append("")
        
        result.append("\\begin{quote}")
        result.append("\\textit{[Interactive Mind Map - Text Representation]}")
        result.append("")
        
        current_indent = 0
        in_list = False
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Handle headings
            if stripped.startswith('#'):
                if in_list:
                    result.append("\\end{itemize}")
                    in_list = False
                
                # Count heading level
                level = 0
                while level < len(stripped) and stripped[level] == '#':
                    level += 1
                
                heading_text = stripped[level:].strip()
                
                # Add appropriate spacing and formatting based on level
                if level == 1:
                    result.append("")
                    result.append(f"\\textbf{{{self._escape_latex(heading_text)}}}")
                elif level == 2:
                    result.append("")
                    result.append(f"\\quad \\textbullet\\ \\textit{{{self._escape_latex(heading_text)}}}")
                else:
                    result.append(f"\\quad\\quad \\textendash\\ {self._escape_latex(heading_text)}")
                
                current_indent = level
            
            # Handle list items
            elif stripped.startswith('-'):
                if not in_list:
                    result.append("\\begin{itemize}")
                    in_list = True
                
                item_text = stripped[1:].strip()
                # Add extra indentation for nested items
                indent = "\\quad" * (current_indent - 1) if current_indent > 1 else ""
                result.append(f"{indent}\\item {self._escape_latex(item_text)}")
        
        if in_list:
            result.append("\\end{itemize}")
        
        result.append("\\end{quote}")
        result.append("")
        result.append("\\textit{\\small Note: This is a text representation of an interactive mind map visualization.}")
        
        return '\n'.join(result)
    
    def _process_markmap_children(self, children: List[Dict[str, Any]], root_text: str = "") -> str:
        """Process hierarchical MarkMap children nodes into LaTeX structure"""
        if not children:
            return ""
        
        latex_lines = []
        
        # If there's root text from the main content, use it as a subsection
        if root_text and root_text.strip():
            # Parse the root text to extract the main title
            root_lines = root_text.strip().split('\n')
            if root_lines:
                first_line = root_lines[0].strip()
                # Remove markdown heading markers if present
                if first_line.startswith('#'):
                    first_line = first_line.lstrip('#').strip()
                if first_line:
                    latex_lines.append(f"\\subsection{{{self._escape_latex(first_line)}}}")
                    latex_lines.append("")
        
        # Process each child node
        for child in children:
            if not isinstance(child, dict):
                continue
            
            child_text = child.get("text", "").strip()
            child_children = child.get("children", [])
            
            if not child_text:
                continue
            
            # Determine the heading level based on whether it has children
            if child_children and isinstance(child_children, list) and len(child_children) > 0:
                # This is a parent node - use subsubsection
                latex_lines.append(f"\\subsubsection{{{self._escape_latex(child_text)}}}")
                latex_lines.append("")
                
                # Process children as list items
                has_valid_children = any(
                    isinstance(gc, dict) and gc.get("text", "").strip() 
                    for gc in child_children
                )
                
                if has_valid_children:
                    latex_lines.append("\\begin{itemize}")
                    for grandchild in child_children:
                        if isinstance(grandchild, dict):
                            gc_text = grandchild.get("text", "").strip()
                            if gc_text:
                                latex_lines.append(f"\\item {self._escape_latex(gc_text)}")
                    latex_lines.append("\\end{itemize}")
                    latex_lines.append("")
            else:
                # This is a leaf node - add as a paragraph or list item
                # For now, treat top-level leaf nodes as subsubsections
                latex_lines.append(f"\\paragraph{{{self._escape_latex(child_text)}}}")
                latex_lines.append("")
        
        return '\n'.join(latex_lines)
    
    def _markmap_text_to_latex(self, text: str) -> str:
        """
        Convert MarkMap markdown text to nested itemize lists
        Automatically determines hierarchy levels and creates proper nesting
        """
        if not text:
            return ""
        
        import re
        
        # Parse the markdown structure into a hierarchy
        lines = text.strip().split('\n')
        items = []
        
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue
            
            # Check if it's a heading (starts with #)
            if stripped_line.startswith('#'):
                heading_match = re.match(r'^(#+)\s*(.+)$', stripped_line)
                if heading_match:
                    level = len(heading_match.group(1))
                    text_content = heading_match.group(2).strip()
                    items.append({
                        'type': 'heading',
                        'level': level,
                        'text': text_content
                    })
            # Check if it's a list item (starts with -)
            elif stripped_line.startswith('-'):
                text_content = stripped_line[1:].strip()
                # List items are children of the last heading, so we use a marker level
                items.append({
                    'type': 'list_item',
                    'level': None,  # Will be determined by parent heading
                    'text': text_content
                })
        
        # Build the nested LaTeX structure
        latex_lines = []
        level_stack = []  # Track open itemize environments by level
        last_heading_level = 0
        
        for i, item in enumerate(items):
            if item['type'] == 'heading':
                current_level = item['level']
                
                # Close deeper levels
                while level_stack and level_stack[-1] >= current_level:
                    latex_lines.append("\\end{itemize}")
                    level_stack.pop()
                
                # Open new level if needed
                if not level_stack or level_stack[-1] < current_level:
                    latex_lines.append("\\begin{itemize}")
                    level_stack.append(current_level)
                
                # Add the heading as a bold item
                latex_lines.append(f"\\item \\textbf{{{self._escape_latex(item['text'])}}}")
                last_heading_level = current_level
                
            elif item['type'] == 'list_item':
                # List items are nested under their parent heading
                # Check if we need to open a nested itemize for list items
                list_level = last_heading_level + 1
                
                # If the last item was a heading, we need to open a nested list
                if i > 0 and items[i-1]['type'] == 'heading':
                    latex_lines.append("\\begin{itemize}")
                    level_stack.append(list_level)
                # If the previous item was also a list item, we're already in the list
                
                # Add the list item
                latex_lines.append(f"\\item {self._escape_latex(item['text'])}")
                
                # Check if next item is not a list item - close the list
                if i + 1 >= len(items) or items[i + 1]['type'] != 'list_item':
                    if level_stack and level_stack[-1] == list_level:
                        latex_lines.append("\\end{itemize}")
                        level_stack.pop()
        
        # Close all remaining open itemize environments
        while level_stack:
            latex_lines.append("\\end{itemize}")
            level_stack.pop()
        
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
        
        # Convert <meaning> tags to parentheses
        latex = re.sub(r'<meaning>(.*?)</meaning>', r'(\1)', latex)
        
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
                
                # Method 1: Try cairosvg (most reliable, but requires Cairo library)
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
                    except OSError as e:
                        if 'cairo' in str(e).lower() or 'library' in str(e).lower():
                            print(f"⚠️  cairosvg requires Cairo library (not installed): Install GTK+ runtime")
                        else:
                            print(f"⚠️  cairosvg conversion failed: {e}")
                        print(f"    Trying Wand/ImageMagick...")
                    except Exception as e:
                        print(f"⚠️  cairosvg conversion failed: {e}, trying Wand/ImageMagick...")
                else:
                    print(f"⚠️  cairosvg not available, trying Wand/ImageMagick...")
                
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
                        import shutil
                        
                        # Try to find magick or convert command
                        magick_cmd = shutil.which('magick')
                        if not magick_cmd:
                            magick_cmd = shutil.which('convert')  # Older ImageMagick versions
                        
                        if not magick_cmd:
                            raise FileNotFoundError("ImageMagick not found")
                        
                        result = subprocess.run([
                            magick_cmd,
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
                        print(f"⚠️ ImageMagick CLI conversion produced empty file, trying Inkscape...")
                except FileNotFoundError:
                    print(f"⚠️ ImageMagick not found (install from imagemagick.org), trying Inkscape...")
                except Exception as e:
                    print(f"⚠️ ImageMagick CLI conversion failed: {e}, trying Inkscape...")
                
                # Method 4: Try Inkscape CLI (excellent for SVG, often pre-installed)
                try:
                    def convert_svg_with_inkscape():
                        import subprocess
                        import shutil
                        
                        # Try to find inkscape
                        inkscape_cmd = shutil.which('inkscape')
                        if not inkscape_cmd:
                            # Try common Windows installation paths
                            possible_paths = [
                                r'C:\Program Files\Inkscape\bin\inkscape.exe',
                                r'C:\Program Files (x86)\Inkscape\bin\inkscape.exe',
                                r'C:\Program Files\Inkscape\inkscape.exe',
                                r'C:\Program Files (x86)\Inkscape\inkscape.exe',
                            ]
                            for path in possible_paths:
                                if os.path.exists(path):
                                    inkscape_cmd = path
                                    break
                        
                        if not inkscape_cmd:
                            raise FileNotFoundError("Inkscape not found")
                        
                        result = subprocess.run([
                            inkscape_cmd,
                            str(original_file_path),
                            '--export-type=png',
                            f'--export-filename={str(png_file_path)}',
                            '--export-width=1200',
                            '--export-background=white',
                        ], capture_output=True, text=True, timeout=30)
                        
                        if result.returncode != 0 and not png_file_path.exists():
                            raise Exception(f"Inkscape conversion failed: {result.stderr}")
                    
                    # Run the conversion in a thread pool to avoid blocking
                    import asyncio
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, convert_svg_with_inkscape)
                    
                    if png_file_path.exists() and png_file_path.stat().st_size > 0:
                        print(f"✅ Successfully converted SVG to PNG using Inkscape: {png_filename}")
                        return png_relative_path
                    else:
                        print(f"⚠️ Inkscape conversion produced empty file, trying Pillow...")
                except FileNotFoundError:
                    print(f"⚠️ Inkscape not found (install from inkscape.org), trying Pillow...")
                except Exception as e:
                    print(f"⚠️ Inkscape conversion failed: {e}, trying Pillow...")
                
                # Method 5: Try Pillow with svg handling (very limited, rarely works)
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
                print("")
                print("❌ All SVG conversion methods failed. SVG images will remain as SVG.")
                print("   LaTeX may not render SVG images properly in PDFs.")
                print("")
                print("   💡 SOLUTIONS:")
                print("   1. Install Inkscape: https://inkscape.org/release/ (RECOMMENDED)")
                print("   2. Install ImageMagick: https://imagemagick.org/script/download.php")
                print("   3. Install GTK+ runtime for Cairo: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer")
                print("   After installing, restart the server to enable SVG conversion.")
                print("")
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
        
        # Handle <meaning> tags - wrap content in parentheses
        html = re.sub(r'<meaning>(.*?)</meaning>', r'(\1)', html)
        
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
        
        # Clean up excessive whitespace and newlines (more than 2 newlines)
        latex = re.sub(r'\n\s*\n\s*\n+', '\n\n', latex)
        
        # Convert double newlines (paragraph breaks) to LaTeX line breaks (\\)
        # but preserve section breaks and environment boundaries
        lines = latex.split('\n')
        result_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            result_lines.append(line)
            
            # Check if we have a blank line (paragraph break)
            if i + 1 < len(lines) and lines[i + 1].strip() == '':
                # Check what comes after the blank line
                if i + 2 < len(lines):
                    next_content = lines[i + 2].strip()
                    # Don't add \\ before LaTeX environments or commands
                    if (next_content and 
                        not next_content.startswith('\\begin{') and
                        not next_content.startswith('\\end{') and
                        not next_content.startswith('\\section') and
                        not next_content.startswith('\\subsection') and
                        not next_content.startswith('\\subsubsection') and
                        not next_content.startswith('\\chapter') and
                        not next_content.startswith('\\part') and
                        not next_content.startswith('\\item')):
                        # This is a paragraph break in flowing text, add \\
                        result_lines.append('\\\\')
                        i += 1  # Skip the blank line
                    else:
                        # Keep the blank line for structural elements
                        i += 1
                        result_lines.append(lines[i])
                else:
                    i += 1
                    result_lines.append(lines[i])
            i += 1
        
        latex = '\n'.join(result_lines)
        
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
