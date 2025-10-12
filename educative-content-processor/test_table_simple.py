"""
Simple test for Table component processing
"""

import asyncio
from section_processor import SectionContentProcessor

# Sample table data
sample_table = {
    "type": "Table",
    "content": {
        "numberOfRows": 3,
        "numberOfColumns": 2,
        "data": [
            ["<p>Header 1</p>", "<p>Header 2</p>"],
            ["<p>Row 1 Col 1</p>", "<p>Row 1 Col 2</p>"],
            ["<p>Row 2 Col 1</p>", "<p>Row 2 Col 2</p>"]
        ],
        "template": 1,
        "title": "Test Table"
    }
}

async def main():
    processor = SectionContentProcessor()
    processor.set_book_context("test", 1, "1")
    
    section_data = {"components": [sample_table]}
    latex, images, types = await processor.process_section_components_async(section_data)
    
    print("Component types:", types)
    print("\nGenerated LaTeX:")
    print(latex)
    
    # Verify
    assert "\\begin{table}" in latex
    assert "\\begin{tabular}" in latex
    assert "Header 1" in latex
    assert "Header 2" in latex
    assert "Row 1 Col 1" in latex
    assert "&" in latex
    assert "\\\\" in latex
    assert "\\hline" in latex
    
    print("\n✅ All assertions passed!")

if __name__ == "__main__":
    asyncio.run(main())
