"""
Test script to verify SpoilerEditor integration with other components
"""

import json
from section_processor import SectionContentProcessor

# Sample section with multiple component types including SpoilerEditor
section_data = {
    "components": [
        {
            "type": "MarkdownEditor",
            "content": {
                "text": "## Problem Statement\n\nDesign a distributed key-value store that can handle high throughput."
            }
        },
        {
            "type": "SpoilerEditor",
            "content": {
                "text": "**Solution Approach:**\n\nWe can use consistent hashing to distribute keys across multiple nodes. This ensures:\n\n- Scalability\n- Load balancing\n- Fault tolerance",
                "showHintText": "Show the solution",
                "hideHintText": "Hide the solution"
            }
        },
        {
            "type": "MarkdownEditor",
            "content": {
                "text": "This approach is used by systems like Amazon DynamoDB and Apache Cassandra."
            }
        }
    ]
}

# Initialize processor
processor = SectionContentProcessor()
processor.set_book_context("test_integration", chapter_number=1, section_id="test_section")

# Process the section
print("Processing section with multiple components including SpoilerEditor...")
latex_content, generated_images, component_types = processor.process_section_components(section_data)

print("\n" + "="*80)
print("COMPONENT TYPES DETECTED:")
print("="*80)
for i, ctype in enumerate(component_types, 1):
    print(f"{i}. {ctype}")

print("\n" + "="*80)
print("LATEX OUTPUT PREVIEW (first 500 chars):")
print("="*80)
print(latex_content[:500])
print("...")

# Write full output to file
with open("test_spoiler_integration_output.tex", "w", encoding="utf-8") as f:
    f.write(latex_content)

print("\n✅ Integration test completed successfully!")
print(f"📄 Full LaTeX output saved to: test_spoiler_integration_output.tex")
print(f"📊 Total component types: {len(set(component_types))}")
print(f"📝 Total components processed: {len(component_types)}")
