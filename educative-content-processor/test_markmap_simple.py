#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from section_processor import SectionContentProcessor

def test_markmap_simple():
    """Simple test of MarkMap component processing"""
    
    # Create a simple test MarkMap component
    test_component = {
        "type": "MarkMap",
        "content": {
            "caption": "Test Mind Map",
            "text": "# Main Topic\n\n## Subtopic 1\n- Item A\n- Item B\n\n## Subtopic 2\n- Item C & D\n- Item E"
        }
    }
    
    # Create processor
    processor = SectionContentProcessor()
    
    try:
        # Test the MarkMap processing
        latex_output = processor._process_markmap(test_component)
        print("SUCCESS: MarkMap LaTeX generated")
        print("Length:", len(latex_output))
        print("Contains 'subsection':", '\\subsection' in latex_output)
        print("Contains 'itemize':", '\\itemize' in latex_output)
        print("Contains proper &:", '\\&' in latex_output and '\\textbackslash{}' not in latex_output)
        
        # Save to file for inspection
        with open('markmap_output.tex', 'w') as f:
            f.write(latex_output)
        print("Output saved to markmap_output.tex")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_markmap_simple()
