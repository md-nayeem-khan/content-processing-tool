#!/usr/bin/env python3
"""
Test section content generation with real Educative section data
"""

import requests
import json

def test_section_content_generation():
    """Test section content generation with actual section data"""
    
    print("🔧 Testing Section Content Generation")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test with the section that we have mock data for
    section_request = {
        "book_name": "test-system-design",
        "chapter_number": 1,
        "section_id": "4771234193080320",  # This matches our test data
        "educative_course_name": "system-design-interview",
        "author_id": "10370001",
        "collection_id": "4941429335392256",
        "use_env_credentials": True
    }
    
    print(f"📤 Sending request:")
    print(json.dumps(section_request, indent=2))
    
    try:
        response = requests.post(f"{base_url}/generate-section-content", json=section_request)
        result = response.json()
        
        print(f"\n📨 Response (Status {response.status_code}):")
        print(json.dumps(result, indent=2))
        
        if result.get("success"):
            print("\n✅ Section content generation successful!")
            print(f"📄 Section file: {result.get('section_file_path')}")
            print(f"🧩 Component types: {result.get('component_types')}")
            print(f"🖼️  Generated images: {result.get('generated_images')}")
            print(f"📝 Section title: {result.get('section_title')}")
            
            # Check if file was actually created
            section_file = f"generated_books/test-system-design/{result.get('section_file_path')}"
            try:
                with open(section_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"\n📜 Generated LaTeX content preview:")
                print(content[:500] + "..." if len(content) > 500 else content)
            except Exception as e:
                print(f"⚠️  Could not read generated file: {e}")
                
        else:
            print(f"\n❌ Section content generation failed:")
            print(f"Error: {result.get('error_message')}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_section_content_generation()
