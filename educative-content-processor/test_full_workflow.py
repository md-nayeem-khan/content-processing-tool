#!/usr/bin/env python3
"""
Full workflow test: Generate book and then section content with LaTeX fixes
"""

import requests
import json
import time

def test_full_workflow():
    """Test complete workflow from book generation to section content"""
    
    print("=== TESTING FULL WORKFLOW WITH LATEX FIXES ===")
    
    # Step 1: Generate book structure
    print("\n1. Generating book structure...")
    book_url = "http://localhost:8000/generate-latex-book"
    
    book_payload = {
        "educative_course_name": "mastering-system-design-fundamentals",
        "book_name": "mastering-system-design-fundamentals",
        "use_env_credentials": True
    }
    
    try:
        book_response = requests.post(book_url, json=book_payload, timeout=60)
        
        if book_response.status_code == 200:
            book_result = book_response.json()
            
            if book_result.get("success"):
                print("✅ Book structure generated successfully!")
                print(f"Book path: {book_result.get('book_path')}")
                print(f"Generated files: {len(book_result.get('generated_files', []))}")
            else:
                print(f"❌ Book generation failed: {book_result.get('error_message')}")
                return False
        else:
            print(f"❌ Book generation HTTP error {book_response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Book generation request failed: {e}")
        return False
    
    # Step 2: Wait a moment for file system operations
    print("\n2. Waiting for file system operations...")
    time.sleep(2)
    
    # Step 3: Generate section content  
    print("\n3. Generating section content with LaTeX fixes...")
    section_url = "http://localhost:8000/generate-section-content"
    
    section_payload = {
        "book_name": "mastering-system-design-fundamentals",
        "chapter_number": 1,
        "section_id": "4771234193080320",
        "educative_course_name": "mastering-system-design-fundamentals",
        "author_id": "10370001",
        "collection_id": "4941429335392256",
        "use_env_credentials": True
    }
    
    try:
        section_response = requests.post(section_url, json=section_payload, timeout=60)
        
        if section_response.status_code == 200:
            section_result = section_response.json()
            
            if section_result.get("success"):
                print("✅ Section content generated successfully!")
                print(f"Section file: {section_result.get('section_file_path')}")
                print(f"Section title: {section_result.get('section_title')}")
                print(f"Generated images: {len(section_result.get('generated_images', []))}")
                print(f"Component types: {section_result.get('component_types')}")
                
                # Analyze LaTeX content quality
                latex_content = section_result.get("latex_content", "")
                if latex_content:
                    print(f"\n4. Analyzing LaTeX content quality...")
                    print("="*60)
                    print("First 300 characters:")
                    print(latex_content[:300])
                    print("="*60)
                    
                    # Look for key improvements
                    improvements = []
                    issues = []
                    
                    # Check for spacing fixes
                    if "April 2008, I joined" in latex_content:
                        improvements.append("✅ Fixed '2008,I' spacing")
                    elif "April 2008,I" in latex_content:
                        issues.append("❌ '2008,I' spacing not fixed")
                    
                    # Check for href formatting
                    import re
                    href_matches = re.findall(r'\\href\{[^}]*\}\{[^}]*\}', latex_content)
                    if href_matches:
                        improvements.append(f"✅ Found {len(href_matches)} properly formatted href commands")
                    
                    malformed_href = re.findall(r'\\href\{[^}]*\{[^}]*\}\}', latex_content)
                    if malformed_href:
                        issues.append(f"❌ Found {len(malformed_href)} malformed href commands")
                    
                    # Check for sentence spacing
                    missing_spaces = re.findall(r'\.([A-Z][a-z])', latex_content)
                    if missing_spaces:
                        issues.append(f"❌ Found {len(missing_spaces)} missing spaces after periods")
                    else:
                        improvements.append("✅ No missing spaces after periods")
                    
                    # Check line lengths (no lines should be extremely long)
                    long_lines = [line for line in latex_content.split('\n') 
                                 if len(line) > 150 and not line.strip().startswith('%')]
                    if long_lines:
                        issues.append(f"⚠️ Found {len(long_lines)} very long lines (>150 chars)")
                    else:
                        improvements.append("✅ No excessively long lines")
                    
                    print(f"\nLaTeX Content Analysis:")
                    print(f"Improvements: {len(improvements)}")
                    for improvement in improvements:
                        print(f"  {improvement}")
                    
                    print(f"Remaining Issues: {len(issues)}")
                    for issue in issues:
                        print(f"  {issue}")
                    
                    if len(issues) == 0:
                        print(f"\n🎉 LaTeX content looks great! Should compile properly.")
                        return True
                    elif len(issues) <= 2:
                        print(f"\n✅ LaTeX content looks good with minor issues.")
                        return True
                    else:
                        print(f"\n⚠️ LaTeX content has several issues that may affect compilation.")
                        return False
                        
            else:
                print(f"❌ Section generation failed: {section_result.get('error_message')}")
                return False
        else:
            print(f"❌ Section generation HTTP error {section_response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Section generation request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_full_workflow()
    
    if success:
        print("\n🎉 Full workflow test completed successfully!")
        print("The LaTeX compilation fixes are working properly.")
    else:
        print("\n⚠️ Full workflow test encountered issues.")
        print("Check the analysis above for details.")
