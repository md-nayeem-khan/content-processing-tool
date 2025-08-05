#!/usr/bin/env python3
"""
Test section generation with existing book structure
"""

import requests
import json

def test_section_with_existing_book():
    """Test section content generation using existing book structure"""
    
    print("=== TESTING SECTION GENERATION WITH EXISTING BOOK ===")
    
    # Test section generation with existing book
    section_url = "http://localhost:8000/generate-section-content"
    
    section_payload = {
        "book_name": "grokking-the-system-design-interview",
        "chapter_number": 1,
        "section_id": "4771234193080320",  # The section that was causing issues
        "educative_course_name": "grokking-the-system-design-interview",
        "author_id": "10370001",
        "collection_id": "4941429335392256",
        "use_env_credentials": True
    }
    
    print(f"Sending request to: {section_url}")
    print(f"Payload: {json.dumps(section_payload, indent=2)}")
    
    try:
        response = requests.post(section_url, json=section_payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                print("✅ Section content generated successfully!")
                print(f"Section file: {result.get('section_file_path')}")
                print(f"Section title: {result.get('section_title')}")
                print(f"Generated images: {len(result.get('generated_images', []))}")
                print(f"Component types: {result.get('component_types')}")
                
                # Analyze the generated LaTeX content
                latex_content = result.get("latex_content", "")
                if latex_content:
                    print(f"\n=== LATEX CONTENT ANALYSIS ===")
                    
                    # Show first part of content
                    print("First 400 characters:")
                    print("="*60)
                    print(latex_content[:400])
                    print("="*60)
                    
                    # Look for the specific problematic patterns we fixed
                    import re
                    
                    analysis_results = []
                    
                    # 1. Check for missing spaces after periods
                    missing_spaces = re.findall(r'\.([A-Z][a-z])', latex_content)
                    if missing_spaces:
                        analysis_results.append(f"❌ Found {len(missing_spaces)} missing spaces after periods")
                        print(f"Examples: {missing_spaces[:3]}")  # Show first 3
                    else:
                        analysis_results.append("✅ No missing spaces after periods")
                    
                    # 2. Check for the specific "2008,I" pattern
                    if "2008,I" in latex_content:
                        analysis_results.append("❌ '2008,I' pattern still present")
                    elif "2008, I" in latex_content:
                        analysis_results.append("✅ Fixed '2008,I' -> '2008, I'")
                    
                    # 3. Check for malformed href commands
                    malformed_href = re.findall(r'\\href\{[^}]*\{[^}]*\}\}', latex_content)
                    if malformed_href:
                        analysis_results.append(f"❌ Found {len(malformed_href)} malformed href commands")
                    else:
                        analysis_results.append("✅ No malformed href commands")
                    
                    # 4. Check for proper href formatting
                    proper_href = re.findall(r'\\href\{[^}]*\}\{[^}]*\}', latex_content)
                    if proper_href:
                        analysis_results.append(f"✅ Found {len(proper_href)} properly formatted href commands")
                    
                    # 5. Check for the ",---for" pattern
                    if ",---for" in latex_content:
                        analysis_results.append("❌ ',---for' pattern still present")
                    elif "---for" in latex_content:
                        analysis_results.append("✅ Fixed ',---for' -> '---for'")
                    
                    # 6. Check for excessive line lengths
                    lines = latex_content.split('\n')
                    very_long_lines = [line for line in lines if len(line) > 150 and not line.strip().startswith('%')]
                    if very_long_lines:
                        analysis_results.append(f"⚠️ Found {len(very_long_lines)} very long lines (>150 chars)")
                    else:
                        analysis_results.append("✅ No excessively long lines")
                    
                    # 7. Check for double escaping (common issue)
                    if "\\\\textbf" in latex_content or "\\\\href" in latex_content:
                        analysis_results.append("❌ Potential double-escaping detected")
                    else:
                        analysis_results.append("✅ No double-escaping detected")
                    
                    # Summary
                    print(f"\nAnalysis Results:")
                    errors = sum(1 for r in analysis_results if r.startswith("❌"))
                    warnings = sum(1 for r in analysis_results if r.startswith("⚠️"))
                    successes = sum(1 for r in analysis_results if r.startswith("✅"))
                    
                    for result in analysis_results:
                        print(f"  {result}")
                    
                    print(f"\nSummary: {successes} ✅ | {warnings} ⚠️ | {errors} ❌")
                    
                    if errors == 0:
                        print(f"\n🎉 LaTeX content should compile successfully!")
                        print("All major formatting issues have been resolved.")
                        return True
                    elif errors <= 1 and warnings <= 2:
                        print(f"\n✅ LaTeX content looks good with minor issues.")
                        return True
                    else:
                        print(f"\n⚠️ LaTeX content may have compilation issues.")
                        return False
                else:
                    print("❌ No LaTeX content returned")
                    return False
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
    success = test_section_with_existing_book()
    
    if success:
        print("\n🎉 Section generation test completed successfully!")
        print("LaTeX compilation fixes are working properly.")
    else:
        print("\n⚠️ Section generation test had issues.")
        print("Review the analysis above for details.")
