"""
Test script to verify chapter summaries are being extracted
"""

import httpx
import json

def test_chapter_summaries():
    """Test that chapter summaries are included in the response"""
    
    url = "http://localhost:8000/generate-book-content"
    
    payload = {
        "educative_course_name": "learn-html-css-javascript-from-scratch",
        "use_env_credentials": True
    }
    
    try:
        print("Testing chapter summary extraction...")
        print("-" * 50)
        
        response = httpx.post(url, json=payload, timeout=60.0)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"Status: {data.get('success')}")
            print(f"Book Title: {data.get('book_title', 'N/A')}")
            
            chapters = data.get('chapters', [])
            print(f"\nTotal Chapters: {len(chapters)}")
            print("\n=== CHAPTER SUMMARIES ===")
            
            for i, chapter in enumerate(chapters[:5]):  # Show first 5 chapters
                title = chapter.get('title', 'N/A')
                summary = chapter.get('summary', None)
                sections_count = len(chapter.get('sections', []))
                
                print(f"\nChapter {i+1}: {title}")
                print(f"  Sections: {sections_count}")
                print(f"  Summary: {summary if summary else 'No summary available'}")
                
                if summary:
                    print(f"  Summary Length: {len(summary)} characters")
            
            # Count chapters with summaries
            chapters_with_summaries = sum(1 for ch in chapters if ch.get('summary'))
            print(f"\n=== SUMMARY STATISTICS ===")
            print(f"Chapters with summaries: {chapters_with_summaries}/{len(chapters)}")
            print(f"Percentage with summaries: {(chapters_with_summaries/len(chapters)*100):.1f}%" if chapters else "0%")
            
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Exception: {str(e)}")

if __name__ == "__main__":
    test_chapter_summaries()
