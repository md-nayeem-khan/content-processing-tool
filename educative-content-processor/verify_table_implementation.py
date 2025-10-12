"""
Final verification of Table implementation with actual backend response structure
"""

import asyncio
from section_processor import SectionContentProcessor

# Exact backend response structure from user's request
backend_table_response = {
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
            [{}, {}], [{}, {}], [{}, {}], [{}, {}], [{}, {}],
            [{}, {}], [{}, {}], [{}, {}], [{}, {}], [{}, {}]
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

async def verify_implementation():
    """Verify the implementation with actual backend data"""
    
    print("=" * 80)
    print("VERIFYING TABLE IMPLEMENTATION WITH ACTUAL BACKEND RESPONSE")
    print("=" * 80)
    
    # Initialize processor
    processor = SectionContentProcessor(output_dir="generated_books")
    processor.set_book_context("verification_test", chapter_number=1, section_id="table_test")
    
    # Create section data
    section_data = {"components": [backend_table_response]}
    
    # Process
    print("\n[1/5] Processing backend table response...")
    latex_content, generated_images, component_types = await processor.process_section_components_async(section_data)
    
    print(f"[2/5] Component types detected: {component_types}")
    assert "Table" in component_types, "❌ Table type not detected!"
    print("      ✅ Table type correctly detected")
    
    print(f"[3/5] Generated images: {len(generated_images)}")
    assert len(generated_images) == 0, "❌ Tables should not generate images!"
    print("      ✅ No images generated (correct)")
    
    # Verification checks
    print("\n[4/5] Running verification checks...")
    
    checks = {
        "Table environment": "\\begin{table}" in latex_content,
        "Tabular environment": "\\begin{tabular}{|l|l|}" in latex_content,
        "Header row (Strengths)": "Strengths" in latex_content,
        "Header row (Advantage)": "Advantage" in latex_content,
        "Data row 1": "Building blocks" in latex_content,
        "Data row 2": "Incremental improvement" in latex_content,
        "Data row 10": "AI-based quizzes" in latex_content,
        "Column separator": " & " in latex_content,
        "Row separator": " \\\\" in latex_content,
        "Horizontal lines": "\\hline" in latex_content,
        "Double line after header": latex_content.count("\\hline\\hline") >= 1,
        "Proper row count": latex_content.count("\\\\") == 10,  # 10 rows
        "Small font size": "\\small" in latex_content,
        "Centered table": "\\centering" in latex_content,
        "Table closing": "\\end{table}" in latex_content,
    }
    
    failed_checks = []
    for check_name, result in checks.items():
        if result:
            print(f"      ✅ {check_name}")
        else:
            print(f"      ❌ {check_name}")
            failed_checks.append(check_name)
    
    # Save output
    print("\n[5/5] Saving output...")
    output_file = "verification_table_output.tex"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    print(f"      ✅ Output saved to: {output_file}")
    
    # Final result
    print("\n" + "=" * 80)
    if not failed_checks:
        print("✅ ALL VERIFICATION CHECKS PASSED!")
        print("   The Table implementation is working correctly with backend data.")
    else:
        print(f"❌ {len(failed_checks)} CHECKS FAILED:")
        for check in failed_checks:
            print(f"   - {check}")
    print("=" * 80)
    
    # Show sample of output
    print("\nSample LaTeX Output (first 500 chars):")
    print("-" * 80)
    print(latex_content[:500])
    print("...")
    print("-" * 80)
    
    return len(failed_checks) == 0

if __name__ == "__main__":
    success = asyncio.run(verify_implementation())
    exit(0 if success else 1)
