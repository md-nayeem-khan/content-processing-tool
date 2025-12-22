"""
Test the EditorCode component conversion
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from section_processor import SectionContentProcessor

def test_editor_code_conversion():
    """Test that EditorCode components are converted to LaTeX code listings"""
    processor = SectionContentProcessor(output_dir="test_output")
    
    # Test case 1: Sample from user request
    test_component_1 = {
        "type": "EditorCode",
        "mode": "edit",
        "content": {
            "language": "javascript",
            "content": "deliverContent(origin_id, server_list, content_type, content_version, description)",
            "version": "1.0",
            "comp_id": "vWL41yBruScOCv_RqiKcL"
        },
        "iteration": 1,
        "children": [
            {
                "text": ""
            }
        ],
        "status": "normal",
        "contentID": "mEwlqb9BvPGYY1TG6ea5r",
        "hash": 9,
        "headingTag": "DqH_d0DXA4RM1-nxf1Siz",
        "collapsed": True
    }
    
    # Test case 2: Python code
    test_component_2 = {
        "type": "EditorCode",
        "mode": "view",
        "content": {
            "language": "python",
            "content": "def calculate_sum(a, b):\n    return a + b",
            "version": "1.0"
        }
    }
    
    # Test case 3: Multi-line code
    test_component_3 = {
        "type": "EditorCode",
        "mode": "edit",
        "content": {
            "language": "java",
            "content": "public class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, World!\");\n    }\n}",
            "version": "1.0"
        }
    }
    
    # Test case 4: Code without language specified
    test_component_4 = {
        "type": "EditorCode",
        "mode": "edit",
        "content": {
            "content": "SELECT * FROM users WHERE active = true;",
            "version": "1.0"
        }
    }
    
    print("Testing EditorCode component conversion\n")
    print("=" * 70)
    
    # Process each test case
    test_cases = [
        ("JavaScript function call", test_component_1),
        ("Python function", test_component_2),
        ("Java class (multi-line)", test_component_3),
        ("Code without language", test_component_4)
    ]
    
    for name, component in test_cases:
        print(f"\n{name}:")
        code_content = component.get("content", {}).get("content", "")
        language = component.get("content", {}).get("language", "none")
        print(f"Language: {language}")
        print(f"Code: {code_content[:50]}{'...' if len(code_content) > 50 else ''}")
        
        result = processor._process_editor_code(component)
        
        print(f"\nOutput LaTeX:")
        print(result)
        
        # Check if lstlisting is present
        if "\\begin{lstlisting}" in result and "\\end{lstlisting}" in result:
            print("✅ SUCCESS: Code block generated correctly")
        else:
            print("❌ FAILED: LaTeX code block not found")
        
        # Check if code content is present
        if code_content[:30] in result:
            print("✅ SUCCESS: Code content preserved")
        else:
            print("⚠️  WARNING: Code content may be modified")
        
        print("-" * 70)

if __name__ == "__main__":
    test_editor_code_conversion()
