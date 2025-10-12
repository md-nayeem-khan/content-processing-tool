"""
Test script for Code component processing
"""

import json
from section_processor import SectionContentProcessor

# Sample Code component data from backend
code_component = {
    "type": "Code",
    "mode": "edit",
    "content": {
        "version": "8.0",
        "caption": "HAProxy sample configuration for layer 7 load balancers",
        "language": "shell",
        "title": "",
        "theme": "default",
        "additionalContent": [],
        "selectedIndex": 0,
        "runnable": False,
        "judge": False,
        "staticEntryFileName": True,
        "judgeContent": None,
        "judgeHints": None,
        "allowDownload": False,
        "treatOutputAsHTML": False,
        "enableHiddenCode": False,
        "enableStdin": False,
        "evaluateWithoutExecution": False,
        "showSolution": False,
        "timeLimit": 30,
        "hiddenCodeContent": {
            "prependCode": "\n\n",
            "appendCode": "\n\n",
            "codeSelection": "prependCode"
        },
        "dockerJob": {},
        "selectedApiKeys": {},
        "selectedEnvVars": {},
        "specialInput": "no-input",
        "solutionContent": "\n\n\n",
        "judgeContentPrepend": "\n\n\n",
        "evaluateLanguage": "shell",
        "isCodeDrawing": False,
        "content": """mode HTTP                               //define which mode the LB will work on, TCP for tier-2 LBs
acl slidesApp path_end -i /presentation //define a category of applications if the path ends in /presentation
use_backend slidesServers if slidesApp  // use a set of backend servers if the request arrives for slidesApp
backend slidesServers                   // listing servers serving slidesApp
server slides1 192.168.12.1:80          //using slides1 server to serve slidesApp. """,
        "entryFileName": "haproxy",
        "staticEntryName": False,
        "readOnlyApiKeys": False,
        "transformOutput": False,
        "outputTransformCode": "function outputTransform(stdout, stderr) {\n  // Transform output or perform API key extraction.\n  const apiKeys = {};\n  return { apiKeys, stdout, stderr };\n}",
        "imageId": "",
        "outputImageHeight": 150,
        "comp_id": "UHXx0UAXFNduHHmCf8q7e"
    },
    "iteration": 0,
    "hash": 14,
    "saveVersion": 7,
    "status": "normal",
    "children": [
        {
            "text": ""
        }
    ],
    "headingTag": "qeWK1Ksmnfl3yOAWv6WTR",
    "collapsed": True
}

# Test section data with Code component
section_data = {
    "components": [code_component]
}

def test_code_processing():
    """Test Code component processing"""
    print("Testing Code component processing...")
    print("=" * 60)
    
    # Create processor
    processor = SectionContentProcessor()
    processor.set_book_context("test_code_book", chapter_number=1, section_id="test_section")
    
    # Process the section
    latex_content, images, component_types = processor.process_section_components(section_data)
    
    print("\n✅ Processing completed successfully!")
    print(f"\nComponent types found: {component_types}")
    print(f"Images generated: {len(images)}")
    
    print("\n" + "=" * 60)
    print("Generated LaTeX:")
    print("=" * 60)
    print(latex_content)
    print("=" * 60)
    
    # Verify the output contains expected elements
    assert "Code" in component_types, "Code component type not detected"
    assert "\\begin{lstlisting}" in latex_content, "lstlisting environment not found"
    assert "HAProxy sample configuration" in latex_content, "Caption not found"
    assert "mode HTTP" in latex_content, "Code content not found"
    
    print("\n✅ All assertions passed!")
    print("\n📝 Summary:")
    print(f"   - Code component successfully processed")
    print(f"   - LaTeX output contains {len(latex_content.split(chr(10)))} lines")
    print(f"   - lstlisting environment properly formatted")
    
    # Save output to file for inspection
    with open("test_code_output.tex", "w", encoding="utf-8") as f:
        f.write(latex_content)
    print(f"   - Output saved to test_code_output.tex")
    
    return latex_content

if __name__ == "__main__":
    try:
        result = test_code_processing()
        print("\n" + "=" * 60)
        print("✅ TEST PASSED - Code component support is working!")
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
