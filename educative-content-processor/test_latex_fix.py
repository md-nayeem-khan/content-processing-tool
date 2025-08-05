#!/usr/bin/env python3
"""
Test script to validate LaTeX generation fix
"""

from latex_generator import LaTeXBookGenerator
from main import SanitizedBookResponse, BookChapter, BookSection

# Create mock data to test LaTeX generation
def create_mock_book_data():
    """Create mock book data for testing"""
    
    sections = [
        BookSection(
            id="1",
            title="Introduction to HTML",
            slug="introduction-to-html",
            summary="Basic HTML concepts"
        ),
        BookSection(
            id="2", 
            title="HTML Document Structure",
            slug="html-document-structure",
            summary="Understanding HTML document structure"
        )
    ]
    
    chapters = [
        BookChapter(
            id="1",
            title="Getting Started with HTML",
            sections=sections,
            summary="Learn the basics of HTML"
        )
    ]
    
    return SanitizedBookResponse(
        success=True,
        book_title="Test HTML Course",
        book_summary="A comprehensive guide to HTML",
        book_brief_summary="Learn HTML basics",
        chapters=chapters,
        total_chapters=1,
        total_sections=2,
        course_url="https://example.com/test-course"
    )

def test_latex_generation():
    """Test LaTeX generation with mock data"""
    
    print("🧪 Testing LaTeX generation with mock data...")
    
    # Create mock data
    book_data = create_mock_book_data()
    
    # Initialize generator
    generator = LaTeXBookGenerator()
    
    try:
        # Generate LaTeX files
        generated_files = generator.generate_book(book_data, "test-book")
        
        print(f"✅ LaTeX generation successful!")
        print(f"📁 Generated {len(generated_files)} files:")
        
        for file_path in generated_files.keys():
            print(f"   - {file_path}")
        
        # Check specific files
        if 'main.tex' in generated_files:
            print(f"\n📄 Main.tex content preview:")
            preview = generated_files['main.tex'][:300] + "..." if len(generated_files['main.tex']) > 300 else generated_files['main.tex']
            print(preview)
        
        return True
        
    except Exception as e:
        print(f"❌ LaTeX generation failed: {e}")
        return False

if __name__ == "__main__":
    success = test_latex_generation()
    if success:
        print("\n🎉 LaTeX generation fix validation: PASSED")
    else:
        print("\n💥 LaTeX generation fix validation: FAILED")
