"""
Test script for Latex component processing
"""

from section_processor import SectionContentProcessor

def test_latex_component():
    """Test processing of Latex component type"""
    
    # Initialize processor
    processor = SectionContentProcessor()
    processor.set_book_context("test_latex", chapter_number=1, section_id="test-section")
    
    # Sample Latex component from backend
    latex_component = {
        "type": "Latex",
        "mode": "edit",
        "content": {
            "version": "1.0",
            "text": "CPU_{time\\ per\\ program} = Instruction_{per\\ program} \\times CPI \\times CPU_{time\\ per\\ clock\\ cycle}",
            "mdhtml": "<span class=\"katex-display\">...</span>",
            "isEquationValid": True,
            "comp_id": "ZhxqdoQ7L8-J9KfNG_xGX"
        },
        "iteration": 0,
        "hash": 13,
        "status": "normal",
        "contentID": "zayKkgpQ99O_WydaEPr5A",
        "widgetCopyId": "6012425262465024",
        "children": [{"text": ""}]
    }
    
    # Create section data with the Latex component
    section_data = {
        "components": [latex_component]
    }
    
    # Process the section
    latex_output, images, component_types = processor.process_section_components(section_data)
    
    print("=" * 80)
    print("LATEX COMPONENT TEST")
    print("=" * 80)
    print("\nComponent Types Found:", component_types)
    print("\nGenerated LaTeX Output:")
    print("-" * 80)
    print(latex_output)
    print("-" * 80)
    print("\nImages Generated:", images)
    
    # Verify the output
    assert "Latex" in component_types, "Latex component type should be detected"
    assert "CPU_{time" in latex_output, "LaTeX equation should be present"
    assert "\\[" in latex_output or "$$" in latex_output or "$" in latex_output, "Should have math delimiters"
    
    print("\n✅ All tests passed!")
    
    # Test with already wrapped equation
    print("\n" + "=" * 80)
    print("TEST: Already wrapped equation")
    print("=" * 80)
    
    wrapped_component = {
        "type": "Latex",
        "content": {
            "text": "$$E = mc^2$$"
        }
    }
    
    section_data2 = {"components": [wrapped_component]}
    latex_output2, _, _ = processor.process_section_components(section_data2)
    
    print("\nGenerated LaTeX Output:")
    print("-" * 80)
    print(latex_output2)
    print("-" * 80)
    
    assert "$$E = mc^2$$" in latex_output2, "Already wrapped equation should be preserved"
    print("\n✅ Wrapped equation test passed!")
    
    # Test with inline math
    print("\n" + "=" * 80)
    print("TEST: Inline math equation")
    print("=" * 80)
    
    inline_component = {
        "type": "Latex",
        "content": {
            "text": "$x^2 + y^2 = z^2$"
        }
    }
    
    section_data3 = {"components": [inline_component]}
    latex_output3, _, _ = processor.process_section_components(section_data3)
    
    print("\nGenerated LaTeX Output:")
    print("-" * 80)
    print(latex_output3)
    print("-" * 80)
    
    assert "$x^2 + y^2 = z^2$" in latex_output3, "Inline math should be preserved"
    print("\n✅ Inline math test passed!")

if __name__ == "__main__":
    test_latex_component()
