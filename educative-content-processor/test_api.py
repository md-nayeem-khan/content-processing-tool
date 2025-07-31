import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_api():
    """Test the FastAPI endpoints"""
    
    print("🚀 Testing Content Processing API")
    print("=" * 50)
    
    # Test health check
    print("\n1. Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test root endpoint
    print("\n2. Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test getting all items (should be empty initially)
    print("\n3. Testing get all items (empty)...")
    response = requests.get(f"{BASE_URL}/items")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test creating a new item
    print("\n4. Testing create item...")
    new_item = {
        "name": "Sample Content",
        "description": "A sample content item for processing",
        "price": 49.99,
        "is_active": True
    }
    response = requests.post(f"{BASE_URL}/items", json=new_item)
    print(f"Status: {response.status_code}")
    created_item = response.json()
    print(f"Response: {created_item}")
    item_id = created_item.get("id")
    
    # Test getting the created item
    print(f"\n5. Testing get item by ID ({item_id})...")
    response = requests.get(f"{BASE_URL}/items/{item_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test updating the item
    print(f"\n6. Testing update item ({item_id})...")
    updated_item = {
        "name": "Updated Content",
        "description": "Updated description for the content",
        "price": 59.99,
        "is_active": True
    }
    response = requests.put(f"{BASE_URL}/items/{item_id}", json=updated_item)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test getting all items (should have our item)
    print("\n7. Testing get all items (with data)...")
    response = requests.get(f"{BASE_URL}/items")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test creating another item
    print("\n8. Testing create another item...")
    another_item = {
        "name": "Another Item",
        "description": "Another test item",
        "price": 25.00,
        "is_active": False
    }
    response = requests.post(f"{BASE_URL}/items", json=another_item)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test deleting an item
    print(f"\n9. Testing delete item ({item_id})...")
    response = requests.delete(f"{BASE_URL}/items/{item_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test getting deleted item (should return 404)
    print(f"\n10. Testing get deleted item ({item_id}) - should return 404...")
    response = requests.get(f"{BASE_URL}/items/{item_id}")
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.json()}")
    
    # Final check - get all remaining items
    print("\n11. Final check - get all remaining items...")
    response = requests.get(f"{BASE_URL}/items")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test the new generate book content endpoint with environment credentials
    print("\n12. Testing generate book content (using environment credentials)...")
    book_request = {
        "educative_course_name": "grokking-the-system-design-interview",
        "use_env_credentials": True
    }
    response = requests.post(f"{BASE_URL}/generate-book-content", json=book_request)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Success: {result.get('success')}")
    print(f"Source: {result.get('source')}")
    if result.get('success'):
        print(f"Data keys: {list(result.get('data', {}).keys())}")
    else:
        print(f"Error: {result.get('error_message')}")
    
    # Test with custom credentials (optional)
    print("\n13. Testing generate book content (using custom credentials)...")
    book_request_custom = {
        "educative_course_name": "grokking-the-system-design-interview",
        "use_env_credentials": False,
        "token": "custom-token-here",  # Replace with actual token if needed
        "cookie": "custom-cookie-here"  # Replace with actual cookie if needed
    }
    response = requests.post(f"{BASE_URL}/generate-book-content", json=book_request_custom)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Success: {result.get('success')}")
    print(f"Source: {result.get('source')}")
    if result.get('success'):
        print(f"Data keys: {list(result.get('data', {}).keys())}")
    else:
        print(f"Error: {result.get('error_message')}")
    
    print("\n" + "=" * 50)
    print("✅ API testing completed!")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API.")
        print("Make sure the FastAPI server is running on http://localhost:8000")
        print("Run: uvicorn main:app --reload")
