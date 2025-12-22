"""
Comprehensive test for EditorCode component with various edge cases
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from section_processor import SectionContentProcessor

def test_editor_code_edge_cases():
    """Test EditorCode with edge cases"""
    processor = SectionContentProcessor(output_dir="test_output")
    
    test_cases = [
        # Edge case 1: Empty content
        {
            "name": "Empty content",
            "component": {
                "type": "EditorCode",
                "content": {
                    "language": "python",
                    "content": "",
                    "version": "1.0"
                }
            },
            "expected": ""
        },
        # Edge case 2: Special characters in code
        {
            "name": "Special characters",
            "component": {
                "type": "EditorCode",
                "content": {
                    "language": "javascript",
                    "content": "const regex = /[a-z]{3,5}/gi;\nconst text = 'Hello & goodbye <tag>';",
                    "version": "1.0"
                }
            },
            "expected": "\\begin{lstlisting}[language=JavaScript]"
        },
        # Edge case 3: Language not in map
        {
            "name": "Unknown language",
            "component": {
                "type": "EditorCode",
                "content": {
                    "language": "foobar",
                    "content": "some code here",
                    "version": "1.0"
                }
            },
            "expected": "\\begin{lstlisting}[language=foobar]"
        },
        # Edge case 4: Missing language field
        {
            "name": "No language specified",
            "component": {
                "type": "EditorCode",
                "content": {
                    "content": "generic code",
                    "version": "1.0"
                }
            },
            "expected": "\\begin{lstlisting}"
        },
        # Edge case 5: TypeScript (maps to JavaScript)
        {
            "name": "TypeScript mapping",
            "component": {
                "type": "EditorCode",
                "content": {
                    "language": "typescript",
                    "content": "interface User { name: string; age: number; }",
                    "version": "1.0"
                }
            },
            "expected": "\\begin{lstlisting}[language=JavaScript]"
        },
        # Edge case 6: Multi-line with mixed indentation
        {
            "name": "Mixed indentation",
            "component": {
                "type": "EditorCode",
                "content": {
                    "language": "python",
                    "content": "def outer():\n    def inner():\n        pass\n    return inner",
                    "version": "1.0"
                }
            },
            "expected": "\\begin{lstlisting}[language=Python]"
        },
        # Edge case 7: Code with LaTeX special chars
        {
            "name": "LaTeX special chars",
            "component": {
                "type": "EditorCode",
                "content": {
                    "language": "bash",
                    "content": "echo $HOME\ncd ~/documents & ls -la",
                    "version": "1.0"
                }
            },
            "expected": "\\begin{lstlisting}[language=bash]"
        }
    ]
    
    print("Testing EditorCode Edge Cases")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        print(f"\n{test['name']}:")
        print(f"  Input: {test['component']['content'].get('content', 'N/A')[:40]}...")
        
        result = processor._process_editor_code(test['component'])
        
        if test['expected']:
            if test['expected'] in result:
                print(f"  ✅ PASS: Expected pattern found")
                passed += 1
            else:
                print(f"  ❌ FAIL: Expected pattern not found")
                print(f"  Expected: {test['expected']}")
                print(f"  Got: {result[:100]}")
                failed += 1
        else:
            if result == "":
                print(f"  ✅ PASS: Empty result as expected")
                passed += 1
            else:
                print(f"  ❌ FAIL: Expected empty result")
                print(f"  Got: {result}")
                failed += 1
    
    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    
    if failed == 0:
        print("✅ All edge case tests passed!")
    else:
        print(f"⚠️  {failed} test(s) failed")

if __name__ == "__main__":
    test_editor_code_edge_cases()
