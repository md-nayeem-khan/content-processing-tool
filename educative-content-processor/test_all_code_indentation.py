"""
Test Code and EditorCode components with proper indentation handling
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from section_processor import SectionContentProcessor

def test_code_component_indentation():
    """Test that Code component properly handles escaped newlines and indentation"""
    
    # Sample Code component with Python code containing \n escape sequences
    code_component = {
        "type": "Code",
        "content": {
            "caption": "Python Class Example",
            "language": "python",
            "content": "class Calculator:\n    def __init__(self):\n        self.result = 0\n\n    def add(self, value):\n        self.result += value\n        return self.result\n\n    def subtract(self, value):\n        self.result -= value\n        return self.result"
        }
    }
    
    processor = SectionContentProcessor(output_dir="test_output")
    processor.set_book_context("test_code", chapter_number=1, section_id="test")
    
    print("Testing Code component with proper indentation...")
    print("=" * 70)
    
    # Process the component
    latex_output = processor._process_code(code_component)
    
    print("\nGenerated LaTeX Output:")
    print("-" * 70)
    print(latex_output)
    print("-" * 70)
    
    # Verify the output
    print("\n✅ Code Component Verification:")
    
    if latex_output.count('\n') > 5:
        print("✅ Code contains multiple lines")
    else:
        print("❌ Code appears to be on a single line")
    
    if '    def __init__(self):' in latex_output:
        print("✅ Code contains proper indentation")
    else:
        print("❌ Code missing proper indentation")
    
    return latex_output

def test_editor_code_indentation():
    """Test that EditorCode component properly handles escaped newlines and indentation"""
    
    # Sample EditorCode component with JavaScript code containing \n escape sequences
    editor_code_component = {
        "type": "EditorCode",
        "mode": "edit",
        "content": {
            "language": "javascript",
            "content": "function processData(items) {\n    return items\n        .filter(item => item.active)\n        .map(item => ({\n            id: item.id,\n            name: item.name.toUpperCase()\n        }))\n        .sort((a, b) => a.name.localeCompare(b.name));\n}",
            "version": "1.0"
        }
    }
    
    processor = SectionContentProcessor(output_dir="test_output")
    processor.set_book_context("test_editor_code", chapter_number=1, section_id="test")
    
    print("\n\nTesting EditorCode component with proper indentation...")
    print("=" * 70)
    
    # Process the component
    latex_output = processor._process_editor_code(editor_code_component)
    
    print("\nGenerated LaTeX Output:")
    print("-" * 70)
    print(latex_output)
    print("-" * 70)
    
    # Verify the output
    print("\n✅ EditorCode Component Verification:")
    
    if latex_output.count('\n') > 5:
        print("✅ Code contains multiple lines")
    else:
        print("❌ Code appears to be on a single line")
    
    if '        .filter(item => item.active)' in latex_output:
        print("✅ Code contains proper indentation")
    else:
        print("❌ Code missing proper indentation")
    
    return latex_output

if __name__ == "__main__":
    try:
        print("=" * 70)
        print("Testing All Code Component Types for Proper Indentation")
        print("=" * 70)
        
        code_output = test_code_component_indentation()
        editor_code_output = test_editor_code_indentation()
        
        # Save combined output
        with open("test_all_code_indentation_output.tex", 'w', encoding='utf-8') as f:
            f.write("\\documentclass{article}\n")
            f.write("\\usepackage{listings}\n")
            f.write("\\lstset{\n")
            f.write("  basicstyle=\\ttfamily,\n")
            f.write("  columns=fullflexible,\n")
            f.write("  breaklines=true,\n")
            f.write("  numbers=left\n")
            f.write("}\n")
            f.write("\\begin{document}\n\n")
            f.write("\\section{Code Component Test}\n")
            f.write(code_output)
            f.write("\n\n\\section{EditorCode Component Test}\n")
            f.write(editor_code_output)
            f.write("\n\n\\end{document}\n")
        
        print("\n" + "=" * 70)
        print("✅ All tests completed successfully!")
        print("✅ Test output saved to: test_all_code_indentation_output.tex")
        print("=" * 70)
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ Test failed with error: {str(e)}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
