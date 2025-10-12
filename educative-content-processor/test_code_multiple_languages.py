"""
Test Code component with multiple programming languages
"""

from section_processor import SectionContentProcessor

def create_code_component(language, caption, code):
    """Helper to create a Code component"""
    return {
        "type": "Code",
        "content": {
            "caption": caption,
            "language": language,
            "content": code
        }
    }

# Test cases for different languages
test_cases = [
    {
        "language": "python",
        "caption": "Python Hello World",
        "code": "def hello():\n    print('Hello, World!')\n\nhello()"
    },
    {
        "language": "javascript",
        "caption": "JavaScript Function",
        "code": "function greet(name) {\n    return `Hello, ${name}!`;\n}\n\nconsole.log(greet('World'));"
    },
    {
        "language": "java",
        "caption": "Java Main Method",
        "code": "public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, World!\");\n    }\n}"
    },
    {
        "language": "shell",
        "caption": "Bash Script",
        "code": "#!/bin/bash\necho 'Hello, World!'\nls -la"
    },
    {
        "language": "sql",
        "caption": "SQL Query",
        "code": "SELECT * FROM users\nWHERE age > 18\nORDER BY name;"
    },
    {
        "language": "cpp",
        "caption": "C++ Program",
        "code": "#include <iostream>\n\nint main() {\n    std::cout << \"Hello, World!\" << std::endl;\n    return 0;\n}"
    }
]

def test_multiple_languages():
    """Test Code component with multiple languages"""
    print("Testing Code component with multiple languages...")
    print("=" * 70)
    
    processor = SectionContentProcessor()
    processor.set_book_context("test_multi_lang", chapter_number=1, section_id="test")
    
    all_latex = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {test_case['language'].upper()}...")
        
        # Create component
        component = create_code_component(
            test_case['language'],
            test_case['caption'],
            test_case['code']
        )
        
        # Process
        section_data = {"components": [component]}
        latex, images, types = processor.process_section_components(section_data)
        
        # Verify
        assert "Code" in types, f"Code type not detected for {test_case['language']}"
        assert "\\begin{lstlisting}" in latex, f"lstlisting not found for {test_case['language']}"
        assert test_case['caption'] in latex, f"Caption not found for {test_case['language']}"
        
        print(f"   ✅ {test_case['language']} processed successfully")
        
        all_latex.append(f"% {test_case['language'].upper()} Example\n{latex}\n")
    
    # Save combined output
    combined = "\n\\vspace{1em}\n\n".join(all_latex)
    with open("test_code_multiple_output.tex", "w", encoding="utf-8") as f:
        f.write(combined)
    
    print("\n" + "=" * 70)
    print("✅ All language tests passed!")
    print(f"   - Tested {len(test_cases)} different languages")
    print(f"   - Output saved to test_code_multiple_output.tex")
    print("=" * 70)
    
    return combined

if __name__ == "__main__":
    try:
        test_multiple_languages()
        print("\n✅ MULTI-LANGUAGE TEST PASSED!")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
