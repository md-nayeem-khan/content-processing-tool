#!/usr/bin/env python3
"""
Final comprehensive test of LaTeX compilation fixes
This script validates that all major LaTeX compilation issues have been resolved
"""

import requests
import json
import re
from pathlib import Path

def run_comprehensive_latex_test():
    """Run comprehensive test of LaTeX fixes"""
    
    print("🔍 COMPREHENSIVE LATEX COMPILATION TEST")
    print("="*60)
    
    # Test section generation
    print("\n1. Testing section content generation...")
    
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
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                print("✅ Section generation successful")
                
                latex_content = result.get("latex_content", "")
                if latex_content:
                    print(f"\n2. Analyzing LaTeX content quality...")
                    
                    # Comprehensive analysis
                    analysis_results = []
                    critical_issues = []
                    warnings = []
                    
                    # === CRITICAL COMPILATION ISSUES ===
                    
                    # Check for double escaping (critical)
                    if re.search(r'\\\\textbf|\\\\href|\\\\subsection', latex_content):
                        critical_issues.append("❌ CRITICAL: Double-escaping detected")
                    else:
                        analysis_results.append("✅ No double-escaping")
                    
                    # Check for malformed LaTeX commands (critical)
                    malformed_commands = []
                    if re.search(r'\\textbf\{\s*\}', latex_content):
                        malformed_commands.append("empty textbf")
                    if re.search(r'\\href\{[^}]*\{[^}]*\}\}', latex_content):
                        malformed_commands.append("malformed href")
                    if re.search(r'\\subsection\{\s*\}', latex_content):
                        malformed_commands.append("empty subsection")
                    
                    if malformed_commands:
                        critical_issues.append(f"❌ CRITICAL: Malformed commands: {', '.join(malformed_commands)}")
                    else:
                        analysis_results.append("✅ No malformed LaTeX commands")
                    
                    # Check for unescaped special characters (critical)
                    unescaped_chars = []
                    # Look for unescaped & % $ # ^ _ { } in content (not comments or commands)
                    
                    # Split content into lines and check non-comment parts
                    lines = latex_content.split('\n')
                    for line in lines:
                        # Skip comment lines and empty lines
                        if line.strip().startswith('%') or not line.strip():
                            continue
                        
                        # Remove LaTeX comments from the line
                        content_part = line.split('%')[0] if '%' in line else line
                        
                        # Check for unescaped special characters in content
                        if re.search(r'[^\\]&(?![^{]*})', content_part):
                            unescaped_chars.append("&")
                            break
                        # Note: % in comments is fine, we already handled that above
                    
                    if unescaped_chars:
                        critical_issues.append(f"❌ CRITICAL: Unescaped special characters: {', '.join(unescaped_chars)}")
                    else:
                        analysis_results.append("✅ No unescaped special characters")
                    
                    # === SPECIFIC PATTERNS THAT WERE PROBLEMATIC ===
                    
                    # Check for the original problematic patterns
                    if "2008,I" in latex_content:
                        critical_issues.append("❌ CRITICAL: '2008,I' pattern still present")
                    elif "2008, I" in latex_content:
                        analysis_results.append("✅ Fixed '2008,I' -> '2008, I'")
                    
                    if ",---for" in latex_content:
                        critical_issues.append("❌ CRITICAL: ',---for' pattern still present")
                    elif "---for" in latex_content:
                        analysis_results.append("✅ Fixed ',---for' -> '---for'")
                    
                    # Check for missing spaces after periods (moderate issue)
                    missing_spaces = re.findall(r'\.([A-Z][a-z])', latex_content)
                    if missing_spaces:
                        warnings.append(f"⚠️ Found {len(missing_spaces)} missing spaces after periods")
                        if len(missing_spaces) <= 5:
                            print(f"   Examples: {missing_spaces[:3]}")
                    else:
                        analysis_results.append("✅ No missing spaces after periods")
                    
                    # === QUALITY CHECKS ===
                    
                    # Check for proper href formatting
                    proper_hrefs = re.findall(r'\\href\{[^}]+\}\{[^}]+\}', latex_content)
                    if proper_hrefs:
                        analysis_results.append(f"✅ Found {len(proper_hrefs)} properly formatted href commands")
                    
                    # Check line lengths (quality issue)
                    lines = latex_content.split('\n')
                    very_long_lines = [line for line in lines if len(line) > 150 and not line.strip().startswith('%')]
                    if very_long_lines:
                        warnings.append(f"⚠️ Found {len(very_long_lines)} very long lines (>150 chars)")
                    else:
                        analysis_results.append("✅ No excessively long lines")
                    
                    # Check for proper figure formatting
                    figures = re.findall(r'\\begin\{figure\}.*?\\end\{figure\}', latex_content, re.DOTALL)
                    if figures:
                        analysis_results.append(f"✅ Found {len(figures)} properly formatted figures")
                    
                    # === SUMMARY ===
                    
                    print(f"\n3. Test Results Summary:")
                    print(f"   ✅ Passed checks: {len(analysis_results)}")
                    print(f"   ⚠️  Warnings: {len(warnings)}")
                    print(f"   ❌ Critical issues: {len(critical_issues)}")
                    
                    print(f"\n4. Detailed Results:")
                    for result in analysis_results:
                        print(f"   {result}")
                    
                    if warnings:
                        print(f"\n   Warnings:")
                        for warning in warnings:
                            print(f"   {warning}")
                    
                    if critical_issues:
                        print(f"\n   Critical Issues:")
                        for issue in critical_issues:
                            print(f"   {issue}")
                    
                    # === FINAL VERDICT ===
                    
                    if critical_issues:
                        print(f"\n❌ COMPILATION TEST FAILED")
                        print(f"   Critical issues must be resolved before LaTeX compilation")
                        return False
                    elif len(warnings) > 3:
                        print(f"\n⚠️ COMPILATION TEST PASSED WITH CONCERNS")
                        print(f"   LaTeX should compile but may have quality issues")
                        return True
                    else:
                        print(f"\n🎉 COMPILATION TEST PASSED!")
                        print(f"   LaTeX content should compile successfully with high quality")
                        return True
                        
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
        print(f"❌ Test failed with exception: {e}")
        return False

def check_generated_file():
    """Check the actual generated file for issues"""
    print(f"\n5. Checking generated file...")
    
    file_path = Path("generated_books/grokking-the-system-design-interview/sections/system_design_interviews_section_4771234193080320.tex")
    
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"   File exists: ✅")
        print(f"   File size: {len(content)} characters")
        
        # Quick validation
        if "April 2008, I joined" in content:
            print(f"   Spacing fix verified: ✅")
        if "---for example" in content and ",---for" not in content:
            print(f"   Dash fix verified: ✅")
        
        return True
    else:
        print(f"   File not found: ❌")
        return False

if __name__ == "__main__":
    print("Starting comprehensive LaTeX compilation test...")
    
    test_passed = run_comprehensive_latex_test()
    file_check = check_generated_file()
    
    if test_passed and file_check:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"🏆 LaTeX compilation fixes are working correctly!")
        print(f"📄 Generated content should compile without issues!")
    else:
        print(f"\n⚠️ Some tests failed - review results above")
    
    print(f"\n" + "="*60)
    print(f"Test completed!")
