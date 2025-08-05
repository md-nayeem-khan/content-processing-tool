#!/usr/bin/env python3
"""
Debug section processor content
"""

import requests
import json
from section_processor import SectionContentProcessor

async def debug_section_processing():
    """Debug the section processing step by step"""
    
    # Initialize processor
    processor = SectionContentProcessor()
    processor.set_book_context('test-debug')
    
    # Test with mock data that has HTML content
    mock_section_data = {
        "components": [
            {
                "type": "SlateHTML",
                "content": {
                    "html": "<p>This is a <strong>test</strong> paragraph.</p>"
                }
            }
        ]
    }
    
    print("🧪 Testing section processing step by step...")
    print("="*50)
    
    # Test HTML to LaTeX conversion directly
    html_content = "<p>This is a <strong>test</strong> paragraph.</p>"
    print(f"Input HTML: {html_content}")
    
    latex_result = processor._html_to_latex_pandoc(html_content)
    print(f"Pandoc Result: {repr(latex_result)}")
    
    # Test the full component processing
    latex_content, images, types = processor.process_section_components(mock_section_data)
    print(f"Full Processing Result: {repr(latex_content)}")
    
    return latex_content

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(debug_section_processing())
