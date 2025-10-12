"""
Test Python syntax highlighting colors
"""

from section_processor import SectionContentProcessor

# Test with python3 language
code_component = {
    "type": "Code",
    "content": {
        "caption": "Distributed Logging",
        "language": "python3",
        "content": """import logging as log # set the logging level to DEBUG
log.basicConfig(level=log.DEBUG) for i in range(6):
    if i == 0:
        log.debug('Debug level') elif i == 1:
        log.info('Info level') elif i == 2:
        log.warning('Warning level') elif i == 3:
        log.error('Error level') elif i == 4:
        log.critical('Critical level') elif i == 5:
        print('Uncomment the following to view a system generated error:') #print(3/0)"""
    }
}

section_data = {"components": [code_component]}

processor = SectionContentProcessor()
processor.set_book_context("test_python_colors", chapter_number=1, section_id="test")

latex, images, types = processor.process_section_components(section_data)

print("Generated LaTeX:")
print("=" * 70)
print(latex)
print("=" * 70)

# Save to file
with open("test_python_colors_output.tex", "w", encoding="utf-8") as f:
    f.write(latex)

print("\n✅ Output saved to test_python_colors_output.tex")
print(f"Language detected: {code_component['content']['language']}")
print(f"Should map to: Python")
