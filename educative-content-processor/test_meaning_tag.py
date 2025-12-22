"""
Test the <meaning> tag conversion in SlateHTML components
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from section_processor import SectionContentProcessor

def test_meaning_tag_conversion():
    """Test that <meaning> tags are converted to parentheses"""
    processor = SectionContentProcessor(output_dir="test_output")
    
    # Test case 1: Simple meaning tag
    test_component_1 = {
        "type": "SlateHTML",
        "content": {
            "html": "<p>This is a <meaning>definition</meaning> example.</p>"
        }
    }
    
    # Test case 2: Meaning tag with formatted content
    test_component_2 = {
        "type": "SlateHTML",
        "content": {
            "html": "<p>The term <strong>API</strong> <meaning>Application Programming Interface</meaning> is widely used.</p>"
        }
    }
    
    # Test case 3: Multiple meaning tags
    test_component_3 = {
        "type": "SlateHTML",
        "content": {
            "html": "<p>Both <meaning>RAM</meaning> and <meaning>ROM</meaning> are types of memory.</p>"
        }
    }
    
    # Test case 4: Meaning tag with nested formatting
    test_component_4 = {
        "type": "SlateHTML",
        "content": {
            "html": "<p>SQL <meaning><em>Structured Query Language</em></meaning> is essential.</p>"
        }
    }
    
    print("Testing <meaning> tag conversion in SlateHTML components\n")
    print("=" * 70)
    
    # Process each test case
    test_cases = [
        ("Simple meaning tag", test_component_1),
        ("Meaning with formatted text", test_component_2),
        ("Multiple meaning tags", test_component_3),
        ("Meaning with nested formatting", test_component_4)
    ]
    
    for name, component in test_cases:
        print(f"\n{name}:")
        print(f"Input HTML: {component['content']['html']}")
        
        result = processor._process_slate_html(component)
        
        print(f"Output LaTeX: {result}")
        
        # Check if parentheses are present
        if "(" in result and ")" in result:
            print("✅ SUCCESS: Meaning tag converted to parentheses")
        else:
            print("❌ FAILED: No parentheses found")
        
        print("-" * 70)

if __name__ == "__main__":
    test_meaning_tag_conversion()
