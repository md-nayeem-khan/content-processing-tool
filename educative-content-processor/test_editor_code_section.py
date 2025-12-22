"""
Test EditorCode component in full section processing
"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(__file__))

from section_processor import SectionContentProcessor

async def test_editor_code_in_section():
    """Test EditorCode component processing in a full section"""
    processor = SectionContentProcessor(output_dir="test_output")
    
    # Create a mock section with EditorCode component
    section_data = {
        "id": "test_section",
        "title": "Test Section with EditorCode",
        "components": [
            {
                "type": "SlateHTML",
                "content": {
                    "html": "<p>Here's a JavaScript function:</p>"
                }
            },
            {
                "type": "EditorCode",
                "mode": "edit",
                "content": {
                    "language": "javascript",
                    "content": "function greet(name) {\n    console.log(`Hello, ${name}!`);\n}",
                    "version": "1.0"
                }
            },
            {
                "type": "SlateHTML",
                "content": {
                    "html": "<p>And here's a Python example:</p>"
                }
            },
            {
                "type": "EditorCode",
                "mode": "view",
                "content": {
                    "language": "python",
                    "content": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
                    "version": "1.0"
                }
            }
        ]
    }
    
    print("Testing EditorCode in full section processing")
    print("=" * 70)
    
    # Process the section
    latex_content, images, component_types = await processor.process_section_components_async(section_data)
    
    print("\nComponent types found:")
    print(component_types)
    
    print("\n\nGenerated LaTeX:")
    print("-" * 70)
    print(latex_content)
    print("-" * 70)
    
    # Verify EditorCode was processed
    if "EditorCode" in component_types:
        print("\n✅ EditorCode component type detected")
    else:
        print("\n❌ EditorCode component type NOT detected")
    
    if "\\begin{lstlisting}" in latex_content:
        print("✅ Code listings generated")
    else:
        print("❌ Code listings NOT found")
    
    if "function greet" in latex_content and "def fibonacci" in latex_content:
        print("✅ Both code samples present in output")
    else:
        print("❌ Code samples missing from output")

if __name__ == "__main__":
    asyncio.run(test_editor_code_in_section())
