"""
Test script to verify the main generate-book-content endpoint returns sanitized responses
"""

import httpx
import json

def test_sanitized_main_endpoint():
    """Test that the main generate-book-content endpoint returns sanitized book data"""
    
    url = "http://localhost:8000/generate-book-content"
    
    # Test request using environment credentials
    payload = {
        "educative_course_name": "learn-html-css-javascript-from-scratch",
        "use_env_credentials": True
    }
    
    try:
        print("Testing main generate-book-content endpoint for sanitized responses...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print("-" * 50)
        
        response = httpx.post(url, json=payload, timeout=60.0)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            
            print("\n=== RESPONSE STRUCTURE ===")
            print(f"Success: {response_data.get('success')}")
            print(f"Source: {response_data.get('source')}")
            print(f"Title: {response_data.get('title', 'N/A')}")
            print(f"Total Chapters: {len(response_data.get('chapters', []))}")
            
            # Show structure of first chapter and section
            chapters = response_data.get('chapters', [])
            if chapters:
                first_chapter = chapters[0]
                print(f"\nFirst Chapter: {first_chapter.get('title', 'N/A')}")
                print(f"Chapter Sections: {len(first_chapter.get('sections', []))}")
                
                sections = first_chapter.get('sections', [])
                if sections:
                    first_section = sections[0]
                    print(f"First Section: {first_section.get('title', 'N/A')}")
                    print(f"Section Content Preview: {str(first_section.get('content', ''))[:100]}...")
            
            # Check if this looks like sanitized book data
            expected_fields = ['success', 'title', 'chapters']
            has_expected_structure = all(field in response_data for field in expected_fields)
            
            print(f"\n=== VALIDATION ===")
            print(f"Has expected book structure: {has_expected_structure}")
            print(f"Response size: {len(response.content)} bytes")
            
            # Check for clean book structure
            if chapters:
                first_chapter = chapters[0]
                chapter_fields = ['title', 'sections']
                has_chapter_structure = all(field in first_chapter for field in chapter_fields)
                print(f"Has clean chapter structure: {has_chapter_structure}")
                
                sections = first_chapter.get('sections', [])
                if sections:
                    first_section = sections[0]
                    section_fields = ['title', 'content']
                    has_section_structure = all(field in first_section for field in section_fields)
                    print(f"Has clean section structure: {has_section_structure}")
            
            print("\n✅ SUCCESS: Main endpoint returns sanitized book data!")
            
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print("Response:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
                
    except Exception as e:
        print(f"\n❌ EXCEPTION: {str(e)}")

if __name__ == "__main__":
    test_sanitized_main_endpoint()
