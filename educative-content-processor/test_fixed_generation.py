#!/usr/bin/env python3
"""
Test the fixed LaTeX generation
"""

import requests
import json

def test_fixed_generation():
    """Test the fixed section generation"""
    
    print("🔧 Testing FIXED Section Generation")
    print("="*50)
    
    # Generate section content
    response = requests.post('http://localhost:8000/generate-section-content', json={
        'book_name': 'test-system-design-fixed',
        'chapter_number': 1,
        'section_id': '4771234193080320',
        'educative_course_name': 'system-design-interview',
        'author_id': '10370001',
        'collection_id': '4941429335392256',
        'use_env_credentials': True
    })
    
    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        return
    
    result = response.json()
    if not result.get('success'):
        print(f"❌ Generation failed: {result.get('error_message')}")
        return
    
    latex_content = result.get('latex_content', '')
    
    # Save for analysis
    with open('fixed_latex_output.tex', 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print(f"✅ Content saved to fixed_latex_output.tex")
    print(f"📊 Content length: {len(latex_content)} characters")
    
    # Check for the fix
    if '\\textbackslash{}' in latex_content:
        print("❌ STILL HAS DOUBLE-ESCAPING ISSUE")
        print("   Found textbackslash{} in content")
    else:
        print("✅ DOUBLE-ESCAPING ISSUE FIXED!")
    
    # Check for proper LaTeX commands
    if '\\textbf{' in latex_content and '\\subsection{' in latex_content:
        print("✅ Proper LaTeX commands found")
    else:
        print("⚠️  LaTeX commands not found as expected")
    
    # Show first few lines of actual content (skip template header)
    lines = latex_content.split('\n')
    content_start = -1
    for i, line in enumerate(lines):
        if line.strip() and not line.startswith('%') and not line.startswith(' '):
            content_start = i
            break
    
    if content_start >= 0:
        print(f"\n📝 First content line (line {content_start + 1}):")
        print(f"    {lines[content_start][:200]}...")
        
        # Show next few lines too
        for i in range(content_start + 1, min(content_start + 4, len(lines))):
            if lines[i].strip():
                print(f"    {lines[i][:200]}...")

if __name__ == "__main__":
    test_fixed_generation()
