"""
Test MarkMap processing with the actual Educative API format
"""

from section_processor import SectionContentProcessor

def test_real_markmap_format():
    """Test with the actual backend response format"""
    
    # This is the actual format from Educative API
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
        },
        "iteration": 0,
        "hash": 1,
        "status": "normal",
        "contentID": "WelTorBA0yKLCTRKjNDBT",
        "saveVersion": 8,
        "widgetCopyId": "5468314213810176",
        "children": [
            {
                "text": ""
            }
        ],
        "headingTag": "JZo0lymJOCsPOK0nG1m0c",
        "collapsed": True
    }
    
    # Create processor
    processor = SectionContentProcessor()
    
    # Test the MarkMap processing
    print("Testing MarkMap processing with real API format...")
    print("=" * 60)
    
    try:
        latex_output = processor._process_markmap(test_component)
        print("SUCCESS: MarkMap LaTeX generated")
        print("=" * 60)
        
        # Save to file for better viewing
        with open("test_markmap_output.tex", "w", encoding="utf-8") as f:
            f.write(latex_output)
        
        print("LaTeX Output saved to: test_markmap_output.tex")
        print("=" * 60)
        print("LaTeX Output:")
        print(latex_output)
        print("=" * 60)
        print(f"\nLength: {len(latex_output)} characters")
        print(f"Contains caption: {'Preparing for the System Design interview' in latex_output}")
        print(f"Contains subsection: {'\\subsection' in latex_output or '\\subsubsection' in latex_output}")
        print(f"Contains itemize: {'\\itemize' in latex_output}")
        
        # Check for specific content
        print(f"\nContent checks:")
        print(f"- Contains 'PACELC theorem': {'PACELC theorem' in latex_output}")
        print(f"- Contains 'WebSockets': {'WebSockets' in latex_output}")
        print(f"- Contains 'Durability': {'Durability' in latex_output}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_markmap_format()
