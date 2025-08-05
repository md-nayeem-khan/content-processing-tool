#!/usr/bin/env python3
"""
Simple test to directly verify the enhanced sanitization function after reloading
"""

import importlib
import sys

# Force reload the main module to get latest changes
if 'main' in sys.modules:
    importlib.reload(sys.modules['main'])

from main import sanitize_educative_response

def test_simple_cases():
    """Test simple cases for author extraction"""
    
    print("🧪 Testing enhanced sanitization with fresh module reload...")
    print("="*60)
    
    # Test string author
    mock_string_author = {
        "instance": {"id": "collection_123"},
        "details": {
            "title": "Test Book",
            "author": "author_abc",
            "toc": {"categories": [
                {
                    "type": "COLLECTION_CATEGORY",
                    "title": "Test Chapter", 
                    "pages": [
                        {
                            "title": "Test Section",
                            "page_id": 999,
                            "slug": "test-section"
                        }
                    ]
                }
            ]}
        }
    }
    
    result = sanitize_educative_response(mock_string_author, "test")
    print(f"📊 String Author Test:")
    print(f"   Mock data details keys: {list(mock_string_author['details'].keys())}")
    print(f"   Mock data author value: {mock_string_author['details'].get('author', 'NOT_FOUND')}")
    print(f"   Success: {result.success}")
    print(f"   Author ID: {result.author_id} (expected: 'author_abc')")
    print(f"   Collection ID: {result.collection_id} (expected: 'collection_123')")
    
    if result.chapters:
        first_section = result.chapters[0].sections[0]
        print(f"   Section Author ID: {first_section.author_id}")
        print(f"   Section Collection ID: {first_section.collection_id}")
    
    # Test numeric author
    mock_numeric_author = {
        "instance": {"id": "collection_456"},
        "details": {
            "title": "Test Book 2",
            "author": 789,
            "toc": {"categories": [
                {
                    "type": "COLLECTION_CATEGORY", 
                    "title": "Test Chapter 2",
                    "pages": [
                        {
                            "title": "Test Section 2",
                            "page_id": 888,
                            "slug": "test-section-2"
                        }
                    ]
                }
            ]}
        }
    }
    
    result2 = sanitize_educative_response(mock_numeric_author, "test")
    print(f"\n📊 Numeric Author Test:")
    print(f"   Success: {result2.success}")
    print(f"   Author ID: {result2.author_id} (expected: '789')")
    print(f"   Collection ID: {result2.collection_id} (expected: 'collection_456')")
    
    if result2.chapters:
        first_section = result2.chapters[0].sections[0]
        print(f"   Section Author ID: {first_section.author_id}")
        print(f"   Section Collection ID: {first_section.collection_id}")

if __name__ == "__main__":
    test_simple_cases()
