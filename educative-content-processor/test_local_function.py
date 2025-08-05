#!/usr/bin/env python3
"""
Test the enhanced author extraction by directly copying the function code
"""

def sanitize_educative_response_local(raw_data: dict, source: str):
    """
    Local copy of the sanitize function to test the logic directly
    """
    try:
        # Extract basic book information
        instance = raw_data.get("instance", {})
        details = instance.get("details", {})
        
        book_title = details.get("title", "")
        book_summary = details.get("summary", "")
        book_brief_summary = details.get("brief_summary", "")
        
        # Extract author_id and collection_id from the response
        author_id = None
        collection_id = None
        
        print(f"DEBUG LOCAL: details keys: {list(details.keys())}")
        
        # Try to extract author_id from various possible locations
        if "author" in details:
            author_data = details.get("author", {})
            print(f"DEBUG LOCAL: Found author data: {author_data} (type: {type(author_data)})")
            if isinstance(author_data, dict):
                author_id = str(author_data.get("id", "")) or str(author_data.get("user_id", ""))
                # Only keep non-empty strings
                author_id = author_id if author_id and author_id != "None" and author_id != "" else None
                print(f"DEBUG LOCAL: Dict author processing result: {author_id}")
            elif isinstance(author_data, (str, int)):
                # Convert to string and check if it's meaningful
                str_author = str(author_data)
                author_id = str_author if str_author and str_author != "None" and str_author != "" else None
                print(f"DEBUG LOCAL: String/int author processing result: {author_id}")
        else:
            print("DEBUG LOCAL: No 'author' key found in details")
        
        # Try to extract collection_id from instance or details
        if "id" in instance and instance.get("id"):
            collection_id = str(instance.get("id", ""))
        elif "collection_id" in details and details.get("collection_id"):
            collection_id = str(details.get("collection_id", ""))
        elif "id" in details and details.get("id"):
            collection_id = str(details.get("id", ""))
        
        print(f"DEBUG LOCAL: Final author_id: {author_id}, collection_id: {collection_id}")
        
        return {
            "success": True,
            "author_id": author_id,
            "collection_id": collection_id,
            "source": source
        }
        
    except Exception as e:
        return {
            "success": False,
            "error_message": f"Failed to sanitize response: {str(e)}",
            "source": source
        }

def test_local_function():
    """Test the local copy of the function"""
    
    print("🧪 Testing local copy of sanitization function...")
    print("="*60)
    
    # Test string author
    mock_string_author = {
        "instance": {"id": "collection_123"},
        "details": {
            "title": "Test Book",
            "author": "author_abc",
            "toc": {"categories": []}
        }
    }
    
    result = sanitize_educative_response_local(mock_string_author, "test")
    print(f"📊 String Author Test Result: {result}")
    
    # Test numeric author
    mock_numeric_author = {
        "instance": {"id": "collection_456"},
        "details": {
            "title": "Test Book 2",
            "author": 789,
            "toc": {"categories": []}
        }
    }
    
    result2 = sanitize_educative_response_local(mock_numeric_author, "test")
    print(f"📊 Numeric Author Test Result: {result2}")

if __name__ == "__main__":
    test_local_function()
