#!/usr/bin/env python3
"""
Debug LaTeX compilation issues
"""

import requests
import json
import re
from pathlib import Path

def test_section_generation():
    """Test section generation and analyze LaTeX output"""
    print("🔧 Testing Section Generation and LaTeX Output")
    print("="*60)
    
    # Generate section content
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
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    if not result.get('success'):
        print(f"❌ Generation failed: {result.get('error_message')}")
        return
    
    latex_content = result.get('latex_content', '')
    
    # Save for analysis
    debug_file = Path('debug_latex_output.tex')
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print(f"✅ Content saved to {debug_file}")
    print(f"📊 Content length: {len(latex_content)} characters")
    
    # Analyze issues
    issues = []
    
    # 1. Check for strikethrough issues
    strikethrough_matches = re.findall(r'~~[^~]*~~', latex_content)
    if strikethrough_matches:
        issues.append(f"Unprocessed strikethrough: {len(strikethrough_matches)} instances")
        print(f"   Found: {strikethrough_matches[:3]}")  # Show first 3
    
    # 2. Check for empty tags
    empty_emph = latex_content.count('\\emph{}')
    if empty_emph > 0:
        issues.append(f"Empty \\emph{{}}: {empty_emph} instances")
    
    # 3. Check for carriage returns
    carriage_returns = latex_content.count('\r')
    if carriage_returns > 0:
        issues.append(f"Carriage returns: {carriage_returns} instances")
    
    # 4. Check for excessive spacing
    double_spaces = latex_content.count('  ')
    if double_spaces > 0:
        issues.append(f"Double spaces: {double_spaces} instances")
    
    # 5. Check for problematic quote patterns
    quote_issues = re.findall(r'\\begin\{quote\}\s*\n\s*\n', latex_content)
    if quote_issues:
        issues.append(f"Quote formatting issues: {len(quote_issues)} instances")
    
    # 6. Check for line ending consistency
    mixed_endings = '\r\n' in latex_content and '\n' in latex_content.replace('\r\n', '')
    if mixed_endings:
        issues.append("Mixed line endings detected")
    
    print("\n🐛 Issues Found:")
    if issues:
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("   ✅ No major issues detected!")
    
    # Show sample problematic content
    print("\n📝 Sample Content (first 500 chars):")
    print("-" * 50)
    print(latex_content[:500])
    print("-" * 50)
    
    # Show around strikethrough if present
    if strikethrough_matches:
        print("\n⚠️  Strikethrough Context:")
        for match in strikethrough_matches[:2]:
            start = latex_content.find(match)
            context = latex_content[max(0, start-50):start+len(match)+50]
            print(f"   ...{context}...")
    
    return latex_content, issues

def analyze_pandoc_conversion():
    """Test pandoc conversion directly"""
    print("\n🔬 Testing Pandoc Conversion")
    print("="*40)
    
    try:
        import pypandoc
        
        # Test HTML with strikethrough
        test_html = """
        <p>This is a test with ~~strikethrough~~ text.</p>
        <p>And some <em></em> empty tags.</p>
        <p>Multiple   spaces and line breaks.</p>
        """
        
        print("Input HTML:")
        print(test_html)
        
        # Convert with pandoc
        latex_output = pypandoc.convert_text(
            test_html, 
            'latex', 
            format='html',
            extra_args=['--wrap=none', '--no-highlight', '--strip-comments']
        )
        
        print("\nPandoc Output:")
        print(repr(latex_output))
        
    except ImportError:
        print("❌ Pypandoc not available")
    except Exception as e:
        print(f"❌ Pandoc conversion failed: {e}")

if __name__ == "__main__":
    latex_content, issues = test_section_generation()
    analyze_pandoc_conversion()
    
    if issues:
        print(f"\n🔧 {len(issues)} issues need to be fixed in the section processor")
    else:
        print("\n✅ LaTeX output looks good!")
