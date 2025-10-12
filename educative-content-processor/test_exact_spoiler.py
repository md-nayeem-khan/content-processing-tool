"""
Test with the exact SpoilerEditor structure from the user's backend response
"""

import json
from section_processor import SectionContentProcessor

# Exact component structure from user's request
exact_component = {
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

section_data = {
    "components": [exact_component]
}

# Initialize processor
processor = SectionContentProcessor()
processor.set_book_context("exact_test", chapter_number=1, section_id="test")

# Process
print("Testing exact backend response structure...")
latex_content, generated_images, component_types = processor.process_section_components(section_data)

# Verify results
print("\n✅ Component Type Detected:", component_types[0])
print("✅ LaTeX Generated:", "Yes" if latex_content else "No")
print("✅ Images Generated:", len(generated_images))

print("\n" + "="*80)
print("LATEX OUTPUT:")
print("="*80)
print(latex_content)
print("="*80)

# Save to file
with open("test_exact_spoiler_output.tex", "w", encoding="utf-8") as f:
    f.write(latex_content)

print("\n✅ Test completed successfully!")
print("📄 Output saved to: test_exact_spoiler_output.tex")
