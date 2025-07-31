#!/usr/bin/env python3
"""
Example showing the difference between raw and sanitized book data responses
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def compare_responses():
    print("📚 Educative API Response Comparison")
    print("=" * 60)
    
    course_data = {
        "educative_course_name": "grokking-the-system-design-interview",
        "use_env_credentials": True
    }
    
    print("\n🔍 Testing Raw Response (generate-book-content):")
    raw_response = requests.post(f"{BASE_URL}/generate-book-content", json=course_data, timeout=30)
    if raw_response.status_code == 200:
        raw_data = raw_response.json()
        print(f"   ✅ Success: {raw_data.get('success')}")
        print(f"   📊 Raw response size: {len(json.dumps(raw_data))} characters")
        print(f"   🗂️  Top-level keys: {list(raw_data.keys())}")
        if 'data' in raw_data and 'instance' in raw_data['data']:
            instance_keys = list(raw_data['data']['instance'].keys())
            print(f"   📁 Instance keys: {instance_keys}")
    
    print("\n✨ Testing Sanitized Response (get-book-data):")
    sanitized_response = requests.post(f"{BASE_URL}/get-book-data", json=course_data, timeout=30)
    if sanitized_response.status_code == 200:
        sanitized_data = sanitized_response.json()
        print(f"   ✅ Success: {sanitized_data.get('success')}")
        print(f"   📖 Book Title: {sanitized_data.get('book_title')}")
        print(f"   📊 Response size: {len(json.dumps(sanitized_data))} characters")
        print(f"   📚 Total Chapters: {sanitized_data.get('total_chapters')}")
        print(f"   📄 Total Sections: {sanitized_data.get('total_sections')}")
        print(f"   🗂️  Clean keys: {list(sanitized_data.keys())}")
        
        # Show sample chapter structure
        if sanitized_data.get('chapters') and len(sanitized_data['chapters']) > 0:
            first_chapter = sanitized_data['chapters'][0]
            print(f"\n   📖 Sample Chapter: '{first_chapter['title']}'")
            print(f"   📄 Sections in first chapter: {len(first_chapter['sections'])}")
            if first_chapter['sections']:
                first_section = first_chapter['sections'][0]
                print(f"   📝 First section: '{first_section['title']}'")
                print(f"   🆔 Section ID: {first_section['id']}")
                print(f"   🔗 Section Slug: {first_section['slug']}")
    
    print("\n" + "=" * 60)
    print("✨ The sanitized response provides a clean, book-focused structure")
    print("📚 Perfect for book generation, content organization, and UI display")

if __name__ == "__main__":
    compare_responses()
