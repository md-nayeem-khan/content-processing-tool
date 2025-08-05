#!/usr/bin/env python3
"""
Test the enhanced author extraction from page-level data
"""

import sys
import importlib

# Force reload the main module to get latest changes
if 'main' in sys.modules:
    importlib.reload(sys.modules['main'])

from main import sanitize_educative_response

def test_page_level_author_extraction():
    """Test author_id extraction from page-level data"""
    
    print("🧪 Testing page-level author_id extraction...")
    print("="*60)
    
    # Mock response with author_id at page level
    mock_response = {
        "instance": {
            "id": "collection_123",
            "details": {
                "title": "Test Course",
                "summary": "Test course summary",
                "toc": {
                    "categories": [
                        {
                            "type": "COLLECTION_CATEGORY",
                            "title": "Chapter 1",
                            "summary": "First chapter",
                            "pages": [
                                {
                                    "title": "Section 1.1",
                                    "page_id": 111,
                                    "slug": "section-1-1",
                                    "author_id": "author_from_page_111"
                                },
                                {
                                    "title": "Section 1.2", 
                                    "page_id": 112,
                                    "slug": "section-1-2",
                                    "author_id": "author_from_page_112"
                                }
                            ]
                        },
                        {
                            "type": "COLLECTION_CATEGORY",
                            "title": "Chapter 2",
                            "pages": [
                                {
                                    "title": "Section 2.1",
                                    "page_id": 221,
                                    "slug": "section-2-1",
                                    "author_id": "author_from_page_221"
                                }
                            ]
                        },
                        {
                            "type": "OTHER_TYPE",  # Should be ignored
                            "title": "Ignored Chapter",
                            "pages": [
                                {
                                    "title": "Ignored Section",
                                    "page_id": 999,
                                    "author_id": "ignored_author"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
    
    result = sanitize_educative_response(mock_response, "test_page_level")
    
    print(f"✅ Sanitization successful: {result.success}")
    print(f"📚 Book Title: {result.book_title}")
    print(f"👤 Book-level Author ID: {result.author_id} (should be 'author_from_page_111')")
    print(f"📦 Collection ID: {result.collection_id}")
    print(f"📖 Total Chapters: {result.total_chapters}")
    print(f"📄 Total Sections: {result.total_sections}")
    
    if result.success and result.chapters:
        print("\n" + "="*60)
        print("🔍 VERIFYING PAGE-LEVEL AUTHOR DATA:")
        print("="*60)
        
        for chapter_idx, chapter in enumerate(result.chapters):
            print(f"\n📋 Chapter {chapter_idx + 1}: {chapter.title}")
            
            for section_idx, section in enumerate(chapter.sections):
                print(f"  📄 Section {section_idx + 1}:")
                print(f"    📝 Title: {section.title}")
                print(f"    🆔 Section ID: {section.id}")
                print(f"    👤 Author ID: {section.author_id}")
                print(f"    📦 Collection ID: {section.collection_id}")
                
                # Check if author_id matches expected page-level value
                expected_author = f"author_from_page_{section.id}"
                if section.author_id == expected_author:
                    print(f"    ✅ Page-level author_id correctly extracted")
                else:
                    print(f"    ❌ Expected '{expected_author}', got '{section.author_id}'")
    
    # Test fallback behavior when pages don't have author_id
    print(f"\n🔍 TESTING FALLBACK BEHAVIOR:")
    print("="*30)
    
    mock_response_fallback = {
        "instance": {
            "id": "collection_456",
            "details": {
                "title": "Test Course 2",
                "author": {"id": "fallback_author_id"},
                "toc": {
                    "categories": [
                        {
                            "type": "COLLECTION_CATEGORY",
                            "title": "Chapter Without Page Authors",
                            "pages": [
                                {
                                    "title": "Section Without Author",
                                    "page_id": 333,
                                    "slug": "section-no-author"
                                    # No author_id here
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
    
    result_fallback = sanitize_educative_response(mock_response_fallback, "test_fallback")
    
    print(f"📊 Fallback Test Result:")
    print(f"   Book-level Author ID: {result_fallback.author_id} (should be 'fallback_author_id')")
    
    if result_fallback.chapters and result_fallback.chapters[0].sections:
        section = result_fallback.chapters[0].sections[0]
        print(f"   Section Author ID: {section.author_id} (should be 'fallback_author_id')")
        
        if section.author_id == "fallback_author_id":
            print(f"   ✅ Fallback author_id working correctly")
        else:
            print(f"   ❌ Fallback failed")

if __name__ == "__main__":
    test_page_level_author_extraction()
