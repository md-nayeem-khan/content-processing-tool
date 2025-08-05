#!/usr/bin/env python3
"""
Debug the actual API flow
"""

import requests
import json

def debug_api_flow():
    """Debug the API response step by step"""
    
    print("🔧 Debugging API Flow")
    print("="*40)
    
    # Make the API call and inspect the response
    response = requests.post('http://localhost:8000/generate-section-content', json={
        'book_name': 'test-system-design',
        'chapter_number': 1,
        'section_id': '4771234193080320',
        'educative_course_name': 'system-design-interview',
        'author_id': '10370001',
        'collection_id': '4941429335392256',
        'use_env_credentials': True
    })
    
    if response.status_code != 200:
        print(f"❌ API call failed: {response.status_code}")
        return
    
    result = response.json()
    latex_content = result.get('latex_content', '')
    
    # Check specific parts of the content
    lines = latex_content.split('\n')
    
    print("📝 First few lines of generated content:")
    for i, line in enumerate(lines[:15]):
        print(f"{i+1:2}: {line}")
    
    # Look for the problematic line
    for i, line in enumerate(lines):
        if 'textbf' in line and 'textbackslash' in line:
            print(f"\n⚠️  Found problematic line {i+1}:")
            print(f"    {line}")
            
            # Show context
            start = max(0, i-2)
            end = min(len(lines), i+3)
            print("    Context:")
            for j in range(start, end):
                marker = " -> " if j == i else "    "
                print(f"{marker}{j+1:2}: {lines[j]}")
            break
    
    # Find the actual content part (after headers)
    content_start = -1
    for i, line in enumerate(lines):
        if line.strip() and not line.startswith('%') and not line.startswith(' '):
            content_start = i
            break
    
    if content_start >= 0:
        print(f"\n📍 Content starts at line {content_start + 1}")
        print(f"    First content line: {repr(lines[content_start])}")

if __name__ == "__main__":
    debug_api_flow()
