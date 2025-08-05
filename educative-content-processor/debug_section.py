#!/usr/bin/env python3
"""
Debug section content generation
"""

import json
from section_processor import SectionContentProcessor

def test_section_processor():
    """Test the section processor with mock data"""
    
    print("🔍 Testing Section Processor")
    
    # Mock section data based on your attachment
    mock_section_data = {
        "components": [
            {
                "type": "SlateHTML",
                "content": {
                    "html": "<h2>This course</h2><p>This course helps readers learn or brush up on their system design skills.</p>",
                    "comp_id": "test-html"
                },
                "hash": 2
            },
            {
                "type": "MarkdownEditor",
                "content": {
                    "text": "Substantial preparation is necessary to increase our odds of getting the job we apply for.",
                    "version": "2.0"
                },
                "hash": 1
            }
        ],
        "summary": {
            "title": "Resources to Prepare for a System Design Interview",
            "description": "Get familiar with resources and guidelines to prepare for the System Design interview."
        }
    }
    
    processor = SectionContentProcessor()
    processor.set_book_context("test-debug")
    
    try:
        latex_content, generated_images, component_types = processor.process_section_components(mock_section_data)
        
        print("✅ Section processing successful!")
        print(f"Component types: {component_types}")
        print(f"Generated images: {generated_images}")
        print(f"LaTeX content preview:")
        print(latex_content[:300] + "..." if len(latex_content) > 300 else latex_content)
        
    except Exception as e:
        print(f"❌ Section processing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_section_processor()
