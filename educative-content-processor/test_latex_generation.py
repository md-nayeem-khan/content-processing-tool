"""
Test script for LaTeX book generation with Jinja2 templates
"""

import asyncio
import json
from pathlib import Path

# Test the LaTeX generator
async def test_latex_generation():
    """Test the complete LaTeX book generation workflow"""
    
    print("🚀 Testing LaTeX Book Generation with Jinja2")
    print("=" * 60)
    
    try:
        # Import required modules
        from latex_generator import LaTeXBookGenerator
        from main import SanitizedBookResponse, BookChapter, BookSection
        
        # Create sample book data
        sample_book_data = SanitizedBookResponse(
            success=True,
            book_title="Learn HTML, CSS, and JavaScript from Scratch",
            book_summary="A comprehensive guide to web development fundamentals",
            book_brief_summary="Master the building blocks of modern web development",
            chapters=[
                BookChapter(
                    title="Semantic Web Page Layout with HTML",
                    summary="Learn how to use HTML for structuring semantic, accessible, and well-organized web pages effectively.",
                    sections=[
                        BookSection(title="What is HTML?", id="1", slug="what-is-html"),
                        BookSection(title="HTML Document Structure", id="2", slug="html-structure"),
                        BookSection(title="Semantic HTML Elements", id="3", slug="semantic-elements")
                    ]
                ),
                BookChapter(
                    title="Stylizing HTML Content using CSS",
                    summary="Get started with CSS fundamentals, selectors, box model, color, font styling, and text alignment.",
                    sections=[
                        BookSection(title="Introduction to CSS", id="4", slug="intro-css"),
                        BookSection(title="CSS Selectors", id="5", slug="css-selectors"),
                        BookSection(title="Box Model", id="6", slug="box-model")
                    ]
                )
            ],
            total_chapters=2,
            total_sections=6,
            source="test_data"
        )
        
        print("✅ Sample book data created")
        print(f"   Title: {sample_book_data.book_title}")
        print(f"   Chapters: {sample_book_data.total_chapters}")
        print(f"   Sections: {sample_book_data.total_sections}")
        print()
        
        # Initialize the LaTeX generator
        latex_generator = LaTeXBookGenerator()
        print("✅ LaTeX generator initialized")
        print(f"   Template directory: {latex_generator.template_dir}")
        print(f"   Output directory: {latex_generator.output_dir}")
        print()
        
        # Generate the book files
        book_name = "test_html_css_js_guide"
        print(f"📚 Generating LaTeX book: {book_name}")
        
        generated_files = latex_generator.generate_book(sample_book_data, book_name)
        print("✅ LaTeX files generated in memory")
        print(f"   Generated {len(generated_files)} files:")
        for file_path in generated_files.keys():
            print(f"     - {file_path}")
        print()
        
        # Save to disk
        book_path = latex_generator.save_book_to_disk(generated_files, book_name)
        print("✅ LaTeX book saved to disk")
        print(f"   Book path: {book_path}")
        print()
        
        # Verify files exist
        book_path_obj = Path(book_path)
        if book_path_obj.exists():
            print("📁 Generated files structure:")
            for file_path in sorted(book_path_obj.rglob('*')):
                if file_path.is_file():
                    relative_path = file_path.relative_to(book_path_obj)
                    file_size = file_path.stat().st_size
                    print(f"     {relative_path} ({file_size} bytes)")
            print()
        
        # Show sample content from main.tex
        main_tex_path = book_path_obj / "main.tex"
        if main_tex_path.exists():
            print("📄 Sample content from main.tex:")
            print("-" * 40)
            with open(main_tex_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                for i, line in enumerate(lines[:20]):  # Show first 20 lines
                    print(f"{i+1:2d}: {line}")
                if len(lines) > 20:
                    print(f"    ... ({len(lines) - 20} more lines)")
            print("-" * 40)
            print()
        
        print("🎉 LaTeX book generation test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Please install jinja2: pip install jinja2")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_latex_generation())
