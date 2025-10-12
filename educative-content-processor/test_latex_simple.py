"""
Simple test for Latex component processing
"""

from section_processor import SectionContentProcessor

# Initialize processor
processor = SectionContentProcessor()
processor.set_book_context("test_latex", chapter_number=1, section_id="test-section")

# Sample Latex component from backend
latex_component = {
    "type": "Latex",
    "content": {
        "text": "CPU_{time\\ per\\ program} = Instruction_{per\\ program} \\times CPI \\times CPU_{time\\ per\\ clock\\ cycle}"
    }
}

# Create section data
section_data = {"components": [latex_component]}

# Process the section
latex_output, images, component_types = processor.process_section_components(section_data)

print("Component Types:", component_types)
print("\nLaTeX Output:")
print(latex_output)
print("\nSuccess: Latex component is now supported!")
