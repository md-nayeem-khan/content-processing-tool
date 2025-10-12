"""
Test MarkMap with more complex hierarchies
"""

from section_processor import SectionContentProcessor

def test_complex_hierarchy():
    """Test with deeper hierarchy levels"""
    
    test_component = {
        "type": "MarkMap",
        "content": {
            "caption": "Complex Mind Map",
            "text": """# Main Topic

## Subtopic 1
- Item A
- Item B

### Deep Topic 1.1
- Deep Item A
- Deep Item B

## Subtopic 2
- Item C
- Item D

### Deep Topic 2.1
- Deep Item C

#### Very Deep Topic
- Very deep item

## Subtopic 3
- Item E"""
        },
        "children": [{"text": ""}]
    }
    
    processor = SectionContentProcessor()
    latex_output = processor._process_markmap(test_component)
    
    print("Complex Hierarchy Test")
    print("=" * 60)
    print(latex_output)
    print("=" * 60)
    
    # Save to file
    with open("test_complex_markmap.tex", "w", encoding="utf-8") as f:
        f.write(latex_output)
    
    print("\nSaved to: test_complex_markmap.tex")
    print(f"Length: {len(latex_output)} characters")
    print(f"Contains '###': {'Deep Topic' in latex_output}")
    print(f"Contains '####': {'Very Deep Topic' in latex_output}")

if __name__ == "__main__":
    test_complex_hierarchy()
