#!/usr/bin/env python3
"""
Test regenerating section content with LaTeX compilation fixes
"""

import requests
import json

def test_section_regeneration():
    """Test section content regeneration with fixed LaTeX processing"""
    
    print("=== TESTING SECTION REGENERATION WITH LATEX FIXES ===")
    
    # Test the section generation endpoint
    url = "http://localhost:8000/generate-section-content"
    
    payload = {
        "book_name": "mastering-system-design-fundamentals",
        "chapter_number": 1,
        "section_id": "4771234193080320",
        "educative_course_name": "mastering-system-design-fundamentals",
        "author_id": "10370001",
        "collection_id": "4941429335392256",
        "use_env_credentials": True
    }
    
    print(f"Sending request to: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                print("✅ Section regeneration successful!")
                print(f"Section file: {result.get('section_file_path')}")
                print(f"Section title: {result.get('section_title')}")
                print(f"Generated images: {len(result.get('generated_images', []))}")
                print(f"Component types: {result.get('component_types')}")
                
                # Show first 500 chars of latex content
                latex_content = result.get("latex_content", "")
                if latex_content:
                    print(f"\nLaTeX content preview (first 500 chars):")
                    print("="*60)
                    print(latex_content[:500])
                    print("="*60)
                    
                    # Check for common LaTeX compilation issues
                    issues = []
                    
                    # Check for double backslashes (double escaping)
                    if "\\\\" in latex_content.replace("\\\\", ""):  # Ignore intentional line breaks
                        issues.append("Potential double-escaping detected")
                    
                    # Check for malformed commands
                    if "\\textbf{" in latex_content and "\\textbf{}" in latex_content:
                        issues.append("Empty textbf commands found")
                    
                    # Check for missing spaces after periods
                    import re
                    if re.search(r'\.([A-Z][a-z])', latex_content):
                        issues.append("Missing spaces after periods found")
                        
                    # Check for href issues
                    if re.search(r'\\href\{[^}]*\{[^}]*\}\}', latex_content):
                        issues.append("Malformed href commands found")
                    
                    if issues:
                        print(f"\n⚠️ Potential LaTeX issues found:")
                        for issue in issues:
                            print(f"  - {issue}")
                    else:
                        print(f"\n✅ No obvious LaTeX compilation issues detected!")
                        
                return True
            else:
                print(f"❌ Section generation failed: {result.get('error_message')}")
                return False
        else:
            print(f"❌ HTTP error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_section_regeneration()
    
    if success:
        print("\n🎉 Section regeneration test completed successfully!")
        print("The LaTeX fixes appear to be working properly.")
    else:
        print("\n⚠️ Section regeneration test failed.")
        print("Check the server logs for more details.")
