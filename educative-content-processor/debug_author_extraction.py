#!/usr/bin/env python3
"""
Debug script to understand why string/numeric author extraction is failing
"""

def debug_author_extraction():
    """Debug the author extraction logic step by step"""
    
    print("🔍 Debugging author extraction logic...")
    print("="*50)
    
    # Test cases
    test_cases = [
        {"author": {"id": "dict_id", "user_id": "dict_user_id"}},
        {"author": "string_author_id"}, 
        {"author": 12345},
        {"author": ""},
        {"author": 0},
        {"author": None}
    ]
    
    for i, details in enumerate(test_cases):
        print(f"\n📊 Test case {i+1}: {details}")
        
        author_id = None
        
        if "author" in details:
            author_data = details.get("author", {})
            print(f"   Raw author_data: {author_data} (type: {type(author_data)})")
            
            if isinstance(author_data, dict):
                print("   → Processing as dict")
                extracted_id = str(author_data.get("id", "")) or str(author_data.get("user_id", ""))
                print(f"   → Extracted: '{extracted_id}'")
                author_id = extracted_id if extracted_id and extracted_id != "None" and extracted_id != "" else None
                
            elif isinstance(author_data, (str, int)):
                print("   → Processing as string/int")
                str_author = str(author_data)
                print(f"   → Converted to string: '{str_author}'")
                print(f"   → Non-empty check: {str_author and str_author != 'None' and str_author != ''}")
                author_id = str_author if str_author and str_author != "None" and str_author != "" else None
            
            else:
                print(f"   → Unknown type: {type(author_data)}")
        
        print(f"   ✅ Final author_id: {author_id}")

if __name__ == "__main__":
    debug_author_extraction()
