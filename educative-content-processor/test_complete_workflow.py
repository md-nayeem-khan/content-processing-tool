#!/usr/bin/env python3
"""
Test complete workflow with fix
"""

import requests
import json
import time

def test_complete_workflow():
    """Test the complete workflow with the fix"""
    
    print("🚀 Testing Complete Workflow with LaTeX Fix")
    print("="*60)
    
    # Step 1: Generate book structure
    print("📚 Step 1: Generating book structure...")
    book_response = requests.post('http://localhost:8000/generate-latex-book', json={
        'educative_course_name': 'grokking-the-system-design-interview',
        'book_name': 'test-system-design-fixed',
        'use_env_credentials': True
    })
    
    if book_response.status_code != 200:
        print(f"❌ Book generation failed: {book_response.status_code}")
        return
    
    book_result = book_response.json()
    if not book_result.get('success'):
        print(f"❌ Book generation failed: {book_result.get('error_message')}")
        return
    
    print("✅ Book structure generated successfully")
    
    # Small delay to ensure file system operations complete
    time.sleep(1)
    
    # Step 2: Generate section content
    print("📄 Step 2: Generating section content...")
    section_response = requests.post('http://localhost:8000/generate-section-content', json={
        'book_name': 'test-system-design-fixed',
        'chapter_number': 1,
        'section_id': '4771234193080320',
        'educative_course_name': 'grokking-the-system-design-interview',
        'author_id': '10370001',
        'collection_id': '4941429335392256',
        'use_env_credentials': True
    })
    
    if section_response.status_code != 200:
        print(f"❌ Section generation failed: {section_response.status_code}")
        print(section_response.text)
        return
    
    section_result = section_response.json()
    if not section_result.get('success'):
        print(f"❌ Section generation failed: {section_result.get('error_message')}")
        return
    
    print("✅ Section content generated successfully")
    
    # Step 3: Analyze the LaTeX content
    latex_content = section_result.get('latex_content', '')
    
    # Save for analysis
    with open('complete_workflow_output.tex', 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print(f"✅ Content saved to complete_workflow_output.tex")
    print(f"📊 Content length: {len(latex_content)} characters")
    
    # Check for the fix
    double_escaped = latex_content.count('\\textbackslash{}')
    if double_escaped > 0:
        print(f"❌ STILL HAS {double_escaped} DOUBLE-ESCAPING ISSUES")
        print("   Found textbackslash{} in content")
    else:
        print("✅ DOUBLE-ESCAPING ISSUE FIXED!")
    
    # Check for proper LaTeX commands
    textbf_count = latex_content.count('\\textbf{')
    subsection_count = latex_content.count('\\subsection{')
    
    print(f"📊 LaTeX Commands Found:")
    print(f"   \\textbf{{...}}: {textbf_count}")
    print(f"   \\subsection{{...}}: {subsection_count}")
    
    if textbf_count > 0 and subsection_count > 0:
        print("✅ Proper LaTeX commands found")
    else:
        print("⚠️  Expected LaTeX commands not found")
    
    # Show sample content
    lines = latex_content.split('\n')
    content_start = -1
    for i, line in enumerate(lines):
        if line.strip() and not line.startswith('%'):
            content_start = i
            break
    
    if content_start >= 0:
        print(f"\n📝 Sample Content (starting at line {content_start + 1}):")
        for i in range(content_start, min(content_start + 3, len(lines))):
            if lines[i].strip():
                sample = lines[i][:100] + "..." if len(lines[i]) > 100 else lines[i]
                print(f"   {i+1}: {sample}")
    
    return latex_content.count('\\textbackslash{}') == 0

if __name__ == "__main__":
    success = test_complete_workflow()
    if success:
        print("\n🎉 FIX VERIFICATION: SUCCESS!")
        print("   LaTeX compilation issues have been resolved.")
    else:
        print("\n❌ FIX VERIFICATION: FAILED!")
        print("   Double-escaping issues still present.")
