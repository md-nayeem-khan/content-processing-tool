#!/usr/bin/env python3
"""
Test script to verify all API endpoints are working correctly
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🧪 Testing {method} {endpoint} - {description}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}{'...' if len(response.text) > 200 else ''}")
        
        if response.status_code < 400:
            print("   ✅ SUCCESS")
        else:
            print("   ❌ FAILED")
            
        return response.status_code < 400
        
    except requests.exceptions.Timeout:
        print("   ⏰ TIMEOUT")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

def main():
    print("🚀 FastAPI Content Processing API - Endpoint Tests")
    print("=" * 60)
    
    # Test basic endpoints
    tests = [
        ("GET", "/", None, "Welcome endpoint"),
        ("GET", "/health", None, "Health check"),
        ("GET", "/items", None, "Get all items (empty list)"),
    ]
    
    # Test creating an item
    item_data = {
        "name": "Test Item",
        "description": "A test item for API testing",
        "price": 29.99,
        "is_active": True
    }
    tests.append(("POST", "/items", item_data, "Create test item"))
    
    # Test getting the created item
    tests.append(("GET", "/items/1", None, "Get created item"))
    
    # Test updating the item
    updated_item = {
        "name": "Updated Test Item",
        "description": "Updated description",
        "price": 39.99,
        "is_active": True
    }
    tests.append(("PUT", "/items/1", updated_item, "Update item"))
    
    # Test the main Educative API endpoint
    educative_data = {
        "educative_course_name": "grokking-the-system-design-interview",
        "use_env_credentials": True
    }
    tests.append(("POST", "/generate-book-content", educative_data, "Educative API integration"))
    
    # Test the new sanitized book endpoint
    tests.append(("POST", "/get-book-data", educative_data, "Sanitized book data endpoint"))
    
    # Test the alternative sanitized endpoint
    tests.append(("POST", "/generate-book", educative_data, "Alternative sanitized book endpoint"))
    
    # Test debug endpoint
    tests.append(("POST", "/debug-educative-response", educative_data, "Debug Educative response"))
    
    # Test deleting the item
    tests.append(("DELETE", "/items/1", None, "Delete test item"))
    
    # Run all tests
    passed = 0
    total = len(tests)
    
    for method, endpoint, data, description in tests:
        if test_endpoint(method, endpoint, data, description):
            passed += 1
        time.sleep(0.5)  # Small delay between tests
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print(f"⚠️  {total - passed} tests failed. Check the output above.")
    
    print(f"\n🌐 API Documentation: {BASE_URL}/docs")
    print(f"🔍 Alternative Docs: {BASE_URL}/redoc")

if __name__ == "__main__":
    main()
