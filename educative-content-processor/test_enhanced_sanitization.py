#!/usr/bin/env python3
"""
Unit test to verify the enhanced sanitize_educative_response function
with mock data to ensure author_id and collection_id extraction works correctly.
"""

import sys
import os

# Add the current directory to the path to import from main.py
sys.path.append(os.path.dirname(__file__))

from main import sanitize_educative_response

def test_enhanced_sanitization():
    """Test the enhanced sanitization function with mock Educative API response"""
    
    # Mock Educative API response structure
    mock_response = {
        "instance": {
            "id": "4941429335392256",  # This should be the collection_id
            "details": {
                "title": "System Design Interview Handbook",
                "summary": "Complete guide to system design interviews",
                "brief_summary": "Learn system design fundamentals",
                "author": {
                    "id": "10370001",  # This should be the author_id
                    "user_id": "10370001"
                },
                "collection_id": "4941429335392256",  # Alternative location
                "toc": {
                    "categories": [
                        {
                            "type": "COLLECTION_CATEGORY",
                            "title": "Introduction to System Design",
                            "summary": "Fundamentals of system design",
                            "pages": [
                                {
                                    "title": "What is System Design?",
                                    "page_id": 1234567890,
                                    "slug": "what-is-system-design"
                                },
                                {
                                    "title": "Design Process Overview",
                                    "page_id": 2345678901,
                                    "slug": "design-process-overview"
                                }
                            ]
                        },
                        {
                            "type": "COLLECTION_CATEGORY", 
                            "title": "Core Concepts",
                            "summary": "Essential system design concepts",
                            "pages": [
                                {
                                    "title": "Scalability Fundamentals",
                                    "page_id": 3456789012,
                                    "slug": "scalability-fundamentals"
                                }
                            ]
                        },
                        {
                            "type": "OTHER_TYPE",  # This should be filtered out
                            "title": "Ignored Category",
                            "pages": [
                                {
                                    "title": "Should not appear",
                                    "page_id": 9999999999,
                                    "slug": "ignored-section"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
    
    print("🧪 Testing enhanced sanitize_educative_response function...")
    print("="*60)
    
    # Test the enhanced sanitization function
    result = sanitize_educative_response(mock_response, "test_source")
    
    print(f"✅ Sanitization successful: {result.success}")
    print(f"📚 Book Title: {result.book_title}")
    print(f"👤 Author ID: {result.author_id}")
    print(f"📦 Collection ID: {result.collection_id}")
    print(f"📖 Total Chapters: {result.total_chapters}")
    print(f"📄 Total Sections: {result.total_sections}")
    print(f"🎯 Source: {result.source}")
    
    if result.success:
        print("\n" + "="*60)
        print("🔍 VERIFYING ENHANCED SECTION DATA:")
        print("="*60)
        
        # Verify that sections have author_id and collection_id
        for chapter_idx, chapter in enumerate(result.chapters):
            print(f"\n📋 Chapter {chapter_idx + 1}: {chapter.title}")
            print(f"   📝 Summary: {chapter.summary}")
            
            for section_idx, section in enumerate(chapter.sections):
                print(f"  📄 Section {section_idx + 1}:")
                print(f"    📝 Title: {section.title}")
                print(f"    🆔 Section ID: {section.id}")
                print(f"    🔗 Slug: {section.slug}")
                print(f"    👤 Author ID: {section.author_id}")
                print(f"    📦 Collection ID: {section.collection_id}")
                
                # Verify the enhanced data
                if section.author_id == "10370001" and section.collection_id == "4941429335392256":
                    print(f"    ✅ Enhanced data correctly extracted")
                else:
                    print(f"    ❌ Enhanced data incorrect or missing")
        
        # Test edge cases
        print(f"\n🔍 TESTING EDGE CASES:")
        print("="*30)
        
        # Test with missing author data
        mock_response_no_author = {
            "instance": {"id": "test_collection"},
            "details": {
                "title": "Test Book",
                "toc": {"categories": []}
            }
        }
        
        result_no_author = sanitize_educative_response(mock_response_no_author, "test_no_author")
        print(f"📊 No author data - Author ID: {result_no_author.author_id} (should be None)")
        print(f"📊 No author data - Collection ID: {result_no_author.collection_id} (should be 'test_collection')")
        
        # Test with alternative author format (string instead of dict)
        mock_response_string_author = {
            "instance": {"id": "test_collection2"},
            "details": {
                "title": "Test Book 2",
                "author": "string_author_id",
                "toc": {"categories": []}
            }
        }
        
        result_string_author = sanitize_educative_response(mock_response_string_author, "test_string_author")
        print(f"📊 String author - Author ID: {result_string_author.author_id} (should be 'string_author_id')")
        
        # Test with numeric author ID
        mock_response_numeric_author = {
            "instance": {"id": "test_collection3"},
            "details": {
                "title": "Test Book 3",
                "author": 12345,
                "toc": {"categories": []}
            }
        }
        
        result_numeric_author = sanitize_educative_response(mock_response_numeric_author, "test_numeric_author")
        print(f"📊 Numeric author - Author ID: {result_numeric_author.author_id} (should be '12345')")
        
    else:
        print(f"❌ Sanitization failed: {result.error_message}")

if __name__ == "__main__":
    test_enhanced_sanitization()
