"""
Test script for Table component processing
"""

import asyncio
from section_processor import SectionContentProcessor

# Sample table data from the backend response
sample_table_component = {
    "type": "Table",
    "mode": "view",
    "content": {
        "version": "2.0",
        "comp_id": "VhwqOjpVpjhH18SkdRgje",
        "numberOfRows": 10,
        "numberOfColumns": 2,
        "columnWidths": [272, 517],
        "data": [
            [
                "<p class=\"ql-align-center\">Strengths</p>",
                "<p class=\"ql-align-center\">Advantage</p>"
            ],
            [
                "<p>Building blocks</p>",
                "<p>This is a modern approach to system design where we construct bigger artifacts using smaller building blocks.</p>"
            ],
            [
                "<p>Building blocks as design problems</p>",
                "<p>We'll treat each one of our building blocks as a stand-alone, mini design problem.</p>"
            ],
            [
                "<p>Incremental improvement to design</p>",
                "<p>Layer-by-layer design solution addresses added bottlenecks, designing simple and incremental solutions to complex systems.</p>"
            ],
            [
                "<p>Evaluating the design</p>",
                "<p>Accountability of the provided design solution shows the performance of our design.</p>"
            ],
            [
                "<p>Solving the traditional problems with updated designs</p>",
                "<p>This course is up to date with the latest industry demands.</p>"
            ],
            [
                "<p>New design problems added</p>",
                "<p>This course contains updates to decades-old system design courses.</p>"
            ],
            [
                "<p>Careful collection of design problems</p>",
                "<p>Each problem has its unique aspects in terms of problem-solving and designing.</p>"
            ],
            [
                "<p>Contributions by experts from FAANG</p>",
                "<p>Learn from the best.</p>"
            ],
            [
                "<p>AI-based quizzes and assessments</p>",
                "<p>These assessments and interviews evaluate learner's concepts of system design.</p>"
            ]
        ],
        "mergeInfo": {},
        "customStyles": [
            [{}, {}],
            [{}, {}],
            [{}, {}],
            [{}, {}],
            [{}, {}],
            [{}, {}],
            [{}, {}],
            [{}, {}],
            [{}, {}],
            [{}, {}]
        ],
        "template": 1,
        "title": "",
        "titleAlignment": "align-center",
        "isCopied": True
    },
    "saveVersion": 22,
    "iteration": 8,
    "hash": 3,
    "status": "normal",
    "contentID": "Je_i9slNM7qouRSc8Gz3i",
    "children": [{"text": ""}]
}

# Sample section data with the table component
sample_section_data = {
    "components": [sample_table_component]
}

async def test_table_processing():
    """Test the table processing functionality"""
    print("=" * 80)
    print("Testing Table Component Processing")
    print("=" * 80)
    
    # Initialize processor
    processor = SectionContentProcessor(output_dir="generated_books")
    processor.set_book_context("test_table_book", chapter_number=1, section_id="test_section")
    
    # Process the section with table component
    print("\n1. Processing table component...")
    latex_content, generated_images, component_types = await processor.process_section_components_async(sample_section_data)
    
    print(f"\n2. Component types detected: {component_types}")
    print(f"3. Generated images: {generated_images}")
    
    print("\n4. Generated LaTeX content:")
    print("-" * 80)
    print(latex_content)
    print("-" * 80)
    
    # Save to file for inspection
    output_file = "test_table_output.tex"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print(f"\n5. LaTeX output saved to: {output_file}")
    
    # Verify key features
    print("\n6. Verification:")
    checks = [
        ("Table environment present", "\\begin{table}" in latex_content),
        ("Tabular environment present", "\\begin{tabular}" in latex_content),
        ("Header row present", "Strengths" in latex_content and "Advantage" in latex_content),
        ("Data rows present", "Building blocks" in latex_content),
        ("Proper row separators", "\\\\" in latex_content),
        ("Horizontal lines present", "\\hline" in latex_content),
        ("Column separators present", "&" in latex_content),
    ]
    
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {check_name}")
    
    print("\n" + "=" * 80)
    print("Test completed successfully!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_table_processing())
