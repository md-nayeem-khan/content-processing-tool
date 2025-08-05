#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from section_processor import SectionContentProcessor

def test_markmap_processing():
    """Test the MarkMap component processing"""
    
    # Create a test MarkMap component
    test_component = {
        "type": "MarkMap",
        "mode": "edit",
        "content": {
            "version": "1.0",
            "caption": "Preparing for the System Design interview",
            "height": 350,
            "width": 900,
            "text": "# System Design interview\n\n## Fundamental concepts in System Design interview\n\n- PACELC theorem\n- Heartbeat\n- AJAX polling/HTTP short-polling\n- HTTP long-polling\n- WebSockets\n- Server-sent events (SSEs)\n\n## Fundamentals of distributed system\n- Durability\n- Replication\n- Partitioning\n- Consensus\n## The architecture of large-scale web applications\n- HTTP & REST\n- Caching\n- CDNs\n- N-Tier applications\n## Design of large-scale distributed systems",
            "comp_id": "Jgn4kQaeJYV_6fvD6XA1F"
        }
    }
    
    # Create processor
    processor = SectionContentProcessor()
    
    # Test the MarkMap processing
    print("Testing MarkMap processing...")
    print("=" * 50)
    
    try:
        # Test the _process_markmap method directly
        latex_output = processor._process_markmap(test_component)
        print("LaTeX Output:")
        print(latex_output)
        print("=" * 50)
        
        # Test the text conversion method directly
        text = test_component["content"]["text"]
        print("Input text:")
        print(repr(text))
        print("\nConverted LaTeX:")
        converted = processor._markmap_text_to_latex(text)
        print(converted)
        
    except Exception as e:
        print(f"Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_markmap_processing()
