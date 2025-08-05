#!/usr/bin/env python3
"""
Test section content generation with local mock data instead of API call
"""

import json
from pathlib import Path

def test_with_mock_data():
    """Test section generation with local mock data"""
    
    print("🧪 Testing section generation with mock data...")
    
    # Load the sample section data from the attachments
    sample_data = {
        "components": [
            {
                "type": "Columns",
                "mode": "edit",
                "content": {
                    "comps": [
                        {
                            "type": "MarkdownEditor",
                            "content": {
                                "version": "2.0",
                                "text": "Substantial preparation is necessary to increase our odds of getting the job we apply for.\\nDepending on a candidate's seniority and proficiency, different candidates need different times for interview preparation.\\nFor an average candidate, three to four months might be required to prepare for a System Design interview."
                            },
                            "hash": "1",
                            "width": "60"
                        }
                    ]
                }
            },
            {
                "type": "SlateHTML",
                "content": {
                    "html": "<h2>This course</h2><p>This course helps readers learn or brush up on their system design skills. We've carefully curated some traditional and fresh design problems to cover the substantial depth and breadth of the system design.</p>"
                }
            }
        ],
        "summary": {
            "description": "Get familiar with resources and guidelines to prepare for the System Design interview.",
            "title": "Resources to Prepare for a System Design Interview"
        }
    }
    
    # Test section processor directly
    from section_processor import SectionContentProcessor
    
    processor = SectionContentProcessor()
    processor.set_book_context("test-debug")
    
    try:
        latex_content, generated_images, component_types = processor.process_section_components(sample_data)
        
        print("✅ Section processing successful!")
        print(f"Component types: {component_types}")
        print(f"Generated LaTeX (first 500 chars):")
        print(latex_content[:500])
        
        # Test template generation
        from latex_generator import LaTeXBookGenerator
        from main import BookSection
        
        latex_generator = LaTeXBookGenerator()
        
        section_obj = BookSection(
            id="4771234193080320",
            title="Resources to Prepare for a System Design Interview",
            slug="resources-to-prepare-for-system-design-interview",
            summary="Test section"
        )
        
        final_latex = latex_generator.generate_section_content(
            chapter_slug="system_design_interview_preparation",
            section=section_obj,
            content=latex_content
        )
        
        print(f"\\n✅ Template generation successful!")
        print(f"Final LaTeX (first 500 chars):")
        print(final_latex[:500])
        
        # Save to file for testing
        output_dir = Path("generated_books/test-system-design/sections")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "test_section.tex"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_latex)
        
        print(f"\\n💾 Section saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_mock_data()
