#!/usr/bin/env python3
"""
Test script to verify the enhanced /generate-book-content endpoint 
with author_id and collection_id in section data.
"""

import requests
import json
from pprint import pprint

def test_enhanced_book_content():
    """Test the enhanced book content generation with author_id and collection_id"""
    
    # API endpoint
    url = "http://localhost:8000/generate-book-content"
    
    # Request payload
    payload = {
        "educative_course_name": "system-design-interview-handbook",
        "use_env_credentials": True
    }
    
    try:
        print("🚀 Testing enhanced /generate-book-content endpoint...")
        print(f"📝 Request: {json.dumps(payload, indent=2)}")
        print("-" * 60)
        
        # Make the request
        response = requests.post(url, json=payload, timeout=60)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ SUCCESS: Enhanced book content generated!")
            print(f"📚 Book Title: {data.get('book_title', 'N/A')}")
            print(f"👤 Author ID: {data.get('author_id', 'N/A')}")
            print(f"📦 Collection ID: {data.get('collection_id', 'N/A')}")
            print(f"📖 Total Chapters: {data.get('total_chapters', 0)}")
            print(f"📄 Total Sections: {data.get('total_sections', 0)}")
            
            print("\n" + "="*60)
            print("🔍 VERIFYING SECTION DATA WITH AUTHOR_ID & COLLECTION_ID:")
            print("="*60)
            
            chapters = data.get('chapters', [])
            if chapters:
                # Check first few sections for enhanced data
                sample_count = 0
                for chapter_idx, chapter in enumerate(chapters[:2]):  # Check first 2 chapters
                    print(f"\n📋 Chapter {chapter_idx + 1}: {chapter.get('title', 'Untitled')}")
                    
                    sections = chapter.get('sections', [])
                    for section_idx, section in enumerate(sections[:3]):  # Check first 3 sections per chapter
                        sample_count += 1
                        print(f"  📄 Section {section_idx + 1}:")
                        print(f"    📝 Title: {section.get('title', 'N/A')}")
                        print(f"    🆔 Section ID: {section.get('id', 'N/A')}")
                        print(f"    🔗 Slug: {section.get('slug', 'N/A')}")
                        print(f"    👤 Author ID: {section.get('author_id', 'N/A')}")
                        print(f"    📦 Collection ID: {section.get('collection_id', 'N/A')}")
                        
                        # Verify that author_id and collection_id are present
                        if section.get('author_id') and section.get('collection_id'):
                            print(f"    ✅ Enhanced data present")
                        else:
                            print(f"    ❌ Enhanced data missing")
                        
                        if sample_count >= 5:  # Limit sample to 5 sections
                            break
                    
                    if sample_count >= 5:
                        break
                
                print(f"\n📊 Sample verified for {sample_count} sections")
                
                # Check if author_id and collection_id are consistent across sections
                all_author_ids = set()
                all_collection_ids = set()
                
                for chapter in chapters:
                    for section in chapter.get('sections', []):
                        if section.get('author_id'):
                            all_author_ids.add(section.get('author_id'))
                        if section.get('collection_id'):
                            all_collection_ids.add(section.get('collection_id'))
                
                print(f"\n🔍 Data Consistency Check:")
                print(f"   Unique Author IDs found: {list(all_author_ids)}")
                print(f"   Unique Collection IDs found: {list(all_collection_ids)}")
                
                if len(all_author_ids) <= 1 and len(all_collection_ids) <= 1:
                    print("   ✅ IDs are consistent across sections")
                else:
                    print("   ⚠️  Multiple different IDs found")
            
            else:
                print("❌ No chapters found in response")
            
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('error_message', 'Unknown error')}")
            except:
                print(f"Raw response: {response.text[:500]}")
        
    except requests.exceptions.Timeout:
        print("❌ FAILED: Request timeout (60s)")
    except requests.exceptions.ConnectionError:
        print("❌ FAILED: Could not connect to server. Is it running on localhost:8000?")
    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_enhanced_book_content()
