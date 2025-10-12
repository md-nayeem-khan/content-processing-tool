"""
Test script for SpoilerEditor component support
"""

import json
from section_processor import SectionContentProcessor

# Sample SpoilerEditor component from the backend response
sample_component = {
    "type": "SpoilerEditor",
    "mode": "edit",
    "content": {
        "version": "3.0",
        "text": "As designers, we'd have a harder job because we'd need to use a traditional database and do extra work to ameliorate the shortcomings or challenges. In this case, we'd have invented a new component.\n\nSuch interactions during interviews are also excellent opportunities to exhibit our design skills.",
        "mdHtml": "<p>As designers, we'd have a harder job because we'd need to use a traditional database and do extra work to ameliorate the shortcomings or challenges. In this case, we'd have invented a new component.</p>\n<p>Such interactions during interviews are also excellent opportunities to exhibit our design skills.</p>\n",
        "showHintText": "Show the solution",
        "hideHintText": "Hide the solution",
        "showIcon": True,
        "comp_id": "Rb3W-X8fKB8ztdCcZCSsw"
    },
    "iteration": 2,
    "hash": 15,
    "saveVersion": 4,
    "contentID": "s6cm_DfaW7P-ML8qQS8nU",
    "status": "normal",
    "children": [
        {
            "text": ""
        }
    ],
    "headingTag": "h_fy3Hnva4Wl_nVats7GY",
    "collapsed": True
}

# Create section data with the component
section_data = {
    "components": [sample_component]
}

# Initialize processor
processor = SectionContentProcessor()
processor.set_book_context("test_book", chapter_number=1, section_id="test_section")

# Process the section
print("Processing SpoilerEditor component...")
latex_content, generated_images, component_types = processor.process_section_components(section_data)

print("\n" + "="*80)
print("COMPONENT TYPES DETECTED:")
print("="*80)
print(component_types)

print("\n" + "="*80)
print("GENERATED LATEX:")
print("="*80)
print(latex_content)

print("\n" + "="*80)
print("GENERATED IMAGES:")
print("="*80)
print(generated_images)

print("\n✅ SpoilerEditor component processed successfully!")

# Write to file for better viewing
with open("test_spoiler_output.tex", "w", encoding="utf-8") as f:
    f.write(latex_content)
print("\n📄 LaTeX output saved to: test_spoiler_output.tex")
