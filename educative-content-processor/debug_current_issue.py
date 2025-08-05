#!/usr/bin/env python3
"""
Debug script to trace the LaTeX conversion issue step by step
"""

import requests
import json

def debug_section_processing():
    """Debug the section processing step by step"""
    
    print("🔍 DEBUGGING LATEX CONVERSION ISSUE")
    print("="*60)
    
    # Test the /generate-section-content endpoint with the same parameters
    response = requests.post('http://localhost:8000/generate-section-content', json={
        'book_name': 'grokking-the-system-design-interview',
        'chapter_number': 1,
        'section_id': '4771234193080320',
        'educative_course_name': 'grokking-the-system-design-interview',
        'author_id': '10370001',
        'collection_id': '4941429335392256',
        'use_env_credentials': True
    })
    
    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    
    if not result.get('success'):
        print(f"❌ Section generation failed: {result.get('error_message')}")
        return
    
    latex_content = result.get('latex_content', '')
    
    # Save for analysis
    with open('debug_current_issue.tex', 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print(f"✅ Content saved to debug_current_issue.tex")
    print(f"📊 Content length: {len(latex_content)} characters")
    
    # Analyze the problematic patterns
    double_escaped = latex_content.count('\\textbackslash{}')
    textbf_issues = latex_content.count('\\textbackslash{}textbf\\textbackslash{}')
    subsection_issues = latex_content.count('\\textbackslash{}subsection\\textbackslash{}')
    
    print(f"\n📊 ISSUE ANALYSIS:")
    print(f"   \\textbackslash{{}} occurrences: {double_escaped}")
    print(f"   \\textbf escaping issues: {textbf_issues}")
    print(f"   \\subsection escaping issues: {subsection_issues}")
    
    # Find and show problematic lines
    lines = latex_content.split('\n')
    problematic_lines = []
    
    for i, line in enumerate(lines):
        if '\\textbackslash{}' in line:
            problematic_lines.append((i+1, line.strip()))
    
    print(f"\n❌ PROBLEMATIC LINES ({len(problematic_lines)} found):")
    for line_num, line in problematic_lines[:5]:  # Show first 5
        sample = line[:80] + "..." if len(line) > 80 else line
        print(f"   Line {line_num}: {sample}")
    
    if len(problematic_lines) > 5:
        print(f"   ... and {len(problematic_lines) - 5} more lines")
    
    # Check what should be correct LaTeX
    print(f"\n✅ WHAT SHOULD BE CORRECT:")
    print(f"   Instead of: \\textbackslash{{}}textbf\\textbackslash{{}}{{text\\textbackslash{{}}}}")
    print(f"   Should be:  \\textbf{{text}}")
    print(f"   Instead of: \\textbackslash{{}}subsection\\textbackslash{{}}{{title\\textbackslash{{}}}}")
    print(f"   Should be:  \\subsection{{title}}")

if __name__ == "__main__":
    debug_section_processing()
