"""
Test paragraph spacing fix for LaTeX output
"""

from section_processor import SectionContentProcessor

def test_paragraph_spacing():
    """Test that paragraph breaks are converted to \\\\ in LaTeX"""
    
    print("=" * 80)
    print("Testing Paragraph Spacing Fix")
    print("=" * 80)
    
    # Sample HTML with multiple paragraphs (similar to user's example)
    sample_html = """
    <p>Abstractions in distributed systems help engineers simplify their work and relieve them of the burden of dealing with the underlying complexity of the distributed systems.</p>
    
    <p>The abstraction of distributed systems has grown in popularity as many big companies like Amazon AWS, Google Cloud, and Microsoft Azure provide distributed services. Every service offers different levels of abstraction. The details behind implementing these distributed services are hidden from the users, thereby allowing the developers to focus on the application rather than going into the depth of the distributed systems that are often very complex.</p>
    
    <p>Today's applications can't remain responsive/functional if they're based on a single node because of an exponentially growing number of users. Abstractions in distributed systems help engineers shift to distributed systems quickly to scale their applications.</p>
    """
    
    processor = SectionContentProcessor()
    
    print("\n1. Converting HTML to LaTeX...")
    latex_output = processor._html_to_latex_pandoc(sample_html)
    
    print("\n2. Generated LaTeX output:")
    print("-" * 80)
    print(latex_output)
    print("-" * 80)
    
    # Check if \\ appears between paragraphs
    if '\\\\' in latex_output:
        print("\n✅ Paragraph breaks converted to \\\\ (line breaks)")
        print(f"   Found {latex_output.count('\\\\\\\\')} line breaks")
    else:
        print("\n⚠️  No \\\\ found - paragraphs may still have blank lines")
    
    # Check for excessive blank lines
    blank_line_count = latex_output.count('\n\n\n')
    if blank_line_count > 0:
        print(f"⚠️  Found {blank_line_count} excessive blank lines")
    else:
        print("✅ No excessive blank lines found")
    
    # Save output for inspection
    with open("test_paragraph_spacing_output.tex", "w", encoding="utf-8") as f:
        f.write("\\documentclass{article}\n")
        f.write("\\begin{document}\n\n")
        f.write("\\subsection{Abstractions in distributed systems}\\label{test}\n\n")
        f.write(latex_output)
        f.write("\n\n\\end{document}\n")
    
    print("\n✅ Output saved to: test_paragraph_spacing_output.tex")
    
    # Also test with section structure
    print("\n" + "=" * 80)
    print("Testing with subsection")
    print("=" * 80)
    
    sample_component = {
        "type": "SlateHTML",
        "content": {
            "html": sample_html
        }
    }
    
    latex_with_section = processor._process_slate_html(sample_component)
    print("\n3. LaTeX with section processing:")
    print("-" * 80)
    print(latex_with_section)
    print("-" * 80)
    
if __name__ == "__main__":
    test_paragraph_spacing()
