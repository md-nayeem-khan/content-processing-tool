#!/usr/bin/env python3
"""
Debug script to examine the raw Educative API response structure
to better understand how to extract author_id and collection_id.
"""

import requests
import json
from pprint import pprint

def debug_raw_response():
    """Debug the raw response structure"""
    
    # API endpoint
    url = "http://localhost:8000/debug-educative-response"
    
    # Request payload
    payload = {
        "educative_course_name": "system-design-interview-handbook",
        "use_env_credentials": True
    }
    
    try:
        print("🔍 Debugging raw Educative API response structure...")
        print(f"📝 Request: {json.dumps(payload, indent=2)}")
        print("-" * 60)
        
        # Make the request
        response = requests.post(url, json=payload, timeout=60)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Raw response info:")
            pprint(data)
            
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Raw response: {response.text[:500]}")
        
    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {str(e)}")

def test_actual_api_call():
    """Test the actual generate-book-content call and examine its response"""
    
    # API endpoint  
    url = "http://localhost:8000/generate-book-content"
    
    # Request payload
    payload = {
        "educative_course_name": "system-design-interview-handbook", 
        "use_env_credentials": True
    }
    
    try:
        print("\n" + "="*60)
        print("🚀 Testing actual /generate-book-content endpoint...")
        print(f"📝 Request: {json.dumps(payload, indent=2)}")
        print("-" * 60)
        
        # Make the request
        response = requests.post(url, json=payload, timeout=60)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Book content response received!")
            
            # Print the entire response structure for debugging
            print("\n🔍 FULL RESPONSE STRUCTURE:")
            print("="*40)
            
            # Print top-level keys and their types
            for key, value in data.items():
                if isinstance(value, (str, int, bool)) or value is None:
                    print(f"{key}: {value}")
                elif isinstance(value, list):
                    print(f"{key}: [list with {len(value)} items]")
                    if value and key == 'chapters':
                        print(f"  First chapter keys: {list(value[0].keys()) if value[0] else 'Empty'}")
                        if value[0] and 'sections' in value[0]:
                            sections = value[0]['sections']
                            if sections:
                                print(f"  First section keys: {list(sections[0].keys())}")
                                print(f"  First section sample: {sections[0]}")
                elif isinstance(value, dict):
                    print(f"{key}: {dict} with keys: {list(value.keys())}")
                else:
                    print(f"{key}: {type(value)}")
            
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Raw response: {response.text[:500]}")
        
    except Exception as e:
        print(f"❌ FAILED: Unexpected error: {str(e)}")

if __name__ == "__main__":
    debug_raw_response()
    test_actual_api_call()
