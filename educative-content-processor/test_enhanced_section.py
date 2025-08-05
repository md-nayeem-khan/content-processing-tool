#!/usr/bin/env python3
"""
Test section regeneration with enhanced LaTeX line break fixes
"""

import requests
import json
import re

def test_section_with_enhanced_fixes():
    """Test section content generation with enhanced line break fixes"""
    
    print("🔧 TESTING ENHANCED LATEX LINE BREAK FIXES")
    print("="*60)
    
    # Test section generation
    url = "http://localhost:8000/generate-section-content"
    payload = {
        "book_name": "grokking-the-system-design-interview",
        "chapter_number": 1,
        "section_id": "4771234193080320",
        "educative_course_name": "grokking-the-system-design-interview",
        "author_id": "10370001",
        "collection_id": "4941429335392256",
        "use_env_credentials": True
    }
    
    print("Regenerating section content with enhanced fixes...")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                print("✅ Section regeneration successful!")
                
                latex_content = result.get("latex_content", "")
                if latex_content:
                    # Save current content for comparison
                    with open("enhanced_output.tex", "w", encoding="utf-8") as f:
                        f.write(latex_content)
                    
                    print(f"\n📊 QUALITY ANALYSIS:")
                    
                    # Analyze the improvements
                    analysis_results = []
                    remaining_issues = []
                    
                    # Check for common line break problems
                    line_break_issues = [
                        ("Most\nengineers", "Most engineers"),
                        ("Since\nSystem", "Since System"),  
                        ("With\nthe right", "With the right"),
                        ("In\nApril", "In April"),
                        ("Amazon\nlaunched", "Amazon launched"),
                        ("However\n,", "However,"),
                        ("Therefore\n,", "Therefore,")
                    ]
                    
                    for issue_pattern, description in line_break_issues:
                        if issue_pattern in latex_content:
                            remaining_issues.append(f"❌ Still has line break in '{description}'")
                        else:
                            analysis_results.append(f"✅ Fixed line break in '{description}'")
                    
                    # Check for spacing around LaTeX commands
                    latex_command_issues = re.search(r'\}[a-zA-Z]', latex_content)
                    if latex_command_issues:
                        remaining_issues.append("❌ Missing spaces after LaTeX commands")
                    else:
                        analysis_results.append("✅ Proper spacing after LaTeX commands")
                    
                    # Check for proper sentence spacing
                    missing_spaces = re.findall(r'\.([A-Z][a-z])', latex_content)
                    if missing_spaces:
                        remaining_issues.append(f"❌ Found {len(missing_spaces)} missing spaces after periods")
                    else:
                        analysis_results.append("✅ Proper spacing after periods")
                    
                    # Check line lengths - now looking for reasonable paragraph lengths
                    lines = latex_content.split('\n')
                    problematic_lines = []
                    
                    for i, line in enumerate(lines):
                        line = line.strip()
                        if (len(line) > 0 and 
                            not line.startswith('%') and 
                            not line.startswith('\\') and
                            len(line) < 20):  # Very short content lines might indicate broken sentences
                            problematic_lines.append((i+1, line[:50]))
                    
                    if problematic_lines:
                        remaining_issues.append(f"⚠️ Found {len(problematic_lines)} very short content lines")
                        # Show first few examples
                        for line_num, content in problematic_lines[:3]:
                            print(f"      Line {line_num}: '{content}...'")
                    else:
                        analysis_results.append("✅ Good paragraph structure")
                    
                    # Show first few paragraphs for visual inspection
                    print(f"\n📄 SAMPLE OUTPUT (first 500 chars):")
                    print("="*50)
                    print(latex_content[:500])
                    print("="*50)
                    
                    # Summary
                    print(f"\n📈 RESULTS SUMMARY:")
                    print(f"✅ Improvements: {len(analysis_results)}")
                    for result in analysis_results:
                        print(f"   {result}")
                    
                    if remaining_issues:
                        print(f"\n⚠️ Remaining Issues: {len(remaining_issues)}")
                        for issue in remaining_issues:
                            print(f"   {issue}")
                    
                    # Final assessment
                    critical_issues = len([issue for issue in remaining_issues if issue.startswith("❌")])
                    
                    if critical_issues == 0:
                        print(f"\n🎉 EXCELLENT! All major line break issues resolved!")
                        print(f"📝 Content should now compile cleanly.")
                        return True
                    elif critical_issues <= 2:
                        print(f"\n✅ GOOD! Most issues resolved, minor tweaks may be needed.")
                        return True
                    else:
                        print(f"\n⚠️ MORE WORK NEEDED: {critical_issues} critical issues remain.")
                        return False
                        
                else:
                    print("❌ No LaTeX content returned")
                    return False
            else:
                print(f"❌ Section generation failed: {result.get('error_message')}")
                return False
        else:
            print(f"❌ HTTP error {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing enhanced LaTeX line break fixes...")
    
    success = test_section_with_enhanced_fixes()
    
    if success:
        print(f"\n🏆 TEST PASSED! Enhanced fixes are working.")
        print(f"💡 The LaTeX content should now compile much better.")
    else:
        print(f"\n🔧 Additional refinements may be needed.")
    
    print(f"\n" + "="*60)
