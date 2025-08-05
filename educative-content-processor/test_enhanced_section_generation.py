#!/usr/bin/env python3
"""
Test script for the enhanced /generate-section-content endpoint
that generates all sections for a given chapter automatically
"""

import requests
import json
from pprint import pprint

def test_chapter_section_generation():
    """Test the enhanced chapter-based section generation"""
    
    print("🧪 Testing Enhanced Chapter-Based Section Generation")
    print("="*60)
    
    # API endpoint
    url = "http://localhost:8000/generate-section-content"
    
    # Test payload - only chapter_number needed now
    payload = {
        "book_name": "grokking-the-system-design-interview",
        "chapter_number": 1,
        "educative_course_name": "grokking-system-design-interview",
        "use_env_credentials": True
    }
    
    try:
        print("📋 Test Configuration:")
        print(f"   📚 Book Name: {payload['book_name']}")
        print(f"   📖 Chapter Number: {payload['chapter_number']}")
        print(f"   🎓 Course Name: {payload['educative_course_name']}")
        print(f"   🔐 Use Environment Credentials: {payload['use_env_credentials']}")
        print()
        
        print("🚀 Sending request to generate all sections for chapter...")
        print("-" * 40)
        
        # Make the request
        response = requests.post(url, json=payload, timeout=300)  # 5 minutes timeout for multiple sections
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ SUCCESS: Chapter sections generation completed!")
            print()
            
            # Debug: Print raw response for troubleshooting
            print("🔍 RAW RESPONSE DEBUG:")
            print(json.dumps(data, indent=2))
            print()
            
            # Display overall results
            print("📈 GENERATION SUMMARY:")
            print("="*40)
            print(f"   🎯 Overall Success: {data.get('success', False)}")
            print(f"   📊 Total Sections Generated: {data.get('total_sections_generated', 0)}")
            
            # Chapter information
            chapter_info = data.get('chapter_info', {})
            if chapter_info:
                print(f"   📋 Chapter Title: {chapter_info.get('chapter_title', 'N/A')}")
                print(f"   🔢 Chapter Number: {chapter_info.get('chapter_number', 'N/A')}")
                print(f"   📝 Chapter Slug: {chapter_info.get('chapter_slug', 'N/A')}")
                print(f"   📄 Total Sections in Chapter: {chapter_info.get('total_sections', 0)}")
                print(f"   ✅ Successful Sections: {chapter_info.get('successful_sections', 0)}")
                print(f"   ❌ Failed Sections: {chapter_info.get('failed_sections', 0)}")
            
            print()
            
            # Display successful generations
            generated_sections = data.get('generated_sections', [])
            if generated_sections:
                print("✅ SUCCESSFULLY GENERATED SECTIONS:")
                print("="*40)
                for i, section in enumerate(generated_sections, 1):
                    print(f"   📄 Section {i}:")
                    print(f"      📝 Title: {section.get('section_title', 'N/A')}")
                    print(f"      🆔 Section ID: {section.get('section_id', 'N/A')}")
                    print(f"      📁 File Path: {section.get('section_file_path', 'N/A')}")
                    print(f"      👤 Author ID: {section.get('author_id', 'N/A')}")
                    print(f"      📦 Collection ID: {section.get('collection_id', 'N/A')}")
                    print(f"      🖼️  Generated Images: {len(section.get('generated_images', []))}")
                    print(f"      🧩 Component Types: {', '.join(section.get('component_types', []))}")
                    print(f"      📊 LaTeX Content Length: {section.get('latex_content_length', 0)} chars")
                    print()
            
            # Display failed sections if any
            failed_sections = data.get('failed_sections', [])
            if failed_sections:
                print("❌ FAILED SECTIONS:")
                print("="*25)
                for i, failure in enumerate(failed_sections, 1):
                    print(f"   ❌ Failed Section {i}:")
                    print(f"      📝 Title: {failure.get('section_title', 'N/A')}")
                    print(f"      🆔 Section ID: {failure.get('section_id', 'N/A')}")
                    print(f"      📍 Section Index: {failure.get('section_index', 'N/A')}")
                    print(f"      ⚠️  Error: {failure.get('error', 'N/A')}")
                    print()
            
            # Success metrics
            total_sections = chapter_info.get('total_sections', 0)
            successful_sections = chapter_info.get('successful_sections', 0)
            
            if total_sections > 0:
                success_rate = (successful_sections / total_sections) * 100
                print(f"📊 SUCCESS RATE: {success_rate:.1f}% ({successful_sections}/{total_sections})")
            
            if data.get('success') and successful_sections > 0:
                print("🎉 CHAPTER GENERATION COMPLETED SUCCESSFULLY!")
            elif successful_sections > 0:
                print("⚠️  PARTIAL SUCCESS - Some sections generated")
            else:
                print("❌ CHAPTER GENERATION FAILED - No sections generated")
                
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error Details: {error_data.get('error_message', 'Unknown error')}")
                if 'chapter_info' in error_data:
                    print(f"Chapter Info: {error_data['chapter_info']}")
            except:
                print(f"Raw response: {response.text[:500]}")
        
    except requests.exceptions.Timeout:
        print("❌ FAILED: Request timeout (5 minutes)")
    except requests.exceptions.ConnectionError:
        print("❌ FAILED: Could not connect to server. Is it running on localhost:8000?")
    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {str(e)}")

def test_endpoint_documentation():
    """Test the endpoint documentation and payload structure"""
    
    print("\n" + "="*60)
    print("📚 ENHANCED ENDPOINT DOCUMENTATION")
    print("="*60)
    
    print("🔧 New Request Structure:")
    print("""
    {
        "book_name": "string",           // Required: Name of the generated book
        "chapter_number": int,           // Required: Chapter number to process
        "educative_course_name": "string", // Required: Course name for API calls
        "token": "string",               // Optional: Auth token
        "cookie": "string",              // Optional: Auth cookie  
        "use_env_credentials": bool      // Optional: Use environment credentials (default: true)
    }
    """)
    
    print("📤 New Response Structure:")
    print("""
    {
        "success": bool,
        "generated_sections": [          // List of successfully generated sections
            {
                "section_id": "string",
                "section_title": "string", 
                "section_file_path": "string",
                "author_id": "string",
                "collection_id": "string",
                "generated_images": ["string"],
                "component_types": ["string"],
                "latex_content_length": int
            }
        ],
        "total_sections_generated": int,
        "failed_sections": [             // List of failed sections (if any)
            {
                "section_id": "string",
                "section_title": "string",
                "section_index": int,
                "error": "string"
            }
        ],
        "chapter_info": {
            "chapter_number": int,
            "chapter_title": "string",
            "chapter_slug": "string", 
            "total_sections": int,
            "successful_sections": int,
            "failed_sections": int
        },
        "error_message": "string",
        "source": "string"
    }
    """)
    
    print("✨ Key Improvements:")
    print("   ✅ Automatic discovery of all sections in a chapter")
    print("   ✅ Automatic extraction of author_id, collection_id, section_id from book data")
    print("   ✅ Batch processing of all sections in the chapter")
    print("   ✅ Detailed success/failure reporting per section")
    print("   ✅ Robust error handling with partial success support")
    print("   ✅ Enhanced progress tracking and metrics")

if __name__ == "__main__":
    test_chapter_section_generation()
    test_endpoint_documentation()
