#!/usr/bin/env python3
"""
Test the enhanced LaTeX line break and spacing fixes
"""

import re

def test_enhanced_fixes():
    """Test the new line break and spacing fixes"""
    
    # Test content with the problems from the user's sample
    test_content = """For many software engineers, System Design Interview questions remain a mysterious challenge. Most
engineers have never actually worked on large-scale systems before, so explaining how to build one seems daunting. Since
System Design interview questions are often open-ended, it can be difficult to know the best way to prepare.

However, as someone who has participated in hundreds of System Design interviews, I can assure you there is a correct way to approach these questions. With
the right mindset and preparation, you can feel confident and ready to tackle any System Design question that comes your way.

In
April 2008, I joined an \\href{https://www.educative.io/blog/25-years-of-developer-interviews}{internal team at Microsoft}working on a large-scale project to build a distributed storage solution. Amazon
launched its Simple Storage Service in 2006."""

    print("=== TESTING ENHANCED LATEX FIXES ===")
    print("Original content:")
    print(repr(test_content))
    print("\n" + "="*60 + "\n")
    
    # Apply the enhanced fixes
    fixed_content = apply_enhanced_fixes(test_content)
    
    print("Fixed content:")
    print(repr(fixed_content))
    print("\n" + "="*60 + "\n")
    
    print("Rendered content:")
    print(fixed_content)
    print("\n" + "="*60 + "\n")
    
    # Check specific improvements
    improvements = []
    issues = []
    
    # Check for line break fixes
    if "Most\nengineers" not in fixed_content:
        improvements.append("✅ Fixed line break in 'Most engineers'")
    else:
        issues.append("❌ Line break in 'Most engineers' not fixed")
    
    if "Since\nSystem" not in fixed_content:
        improvements.append("✅ Fixed line break in 'Since System'")
    else:
        issues.append("❌ Line break in 'Since System' not fixed")
        
    if "With\nthe right" not in fixed_content:
        improvements.append("✅ Fixed line break in 'With the right'")
    else:
        issues.append("❌ Line break in 'With the right' not fixed")
    
    if "In\nApril" not in fixed_content:
        improvements.append("✅ Fixed line break in 'In April'")
    else:
        issues.append("❌ Line break in 'In April' not fixed")
        
    if "Microsoft}working" not in fixed_content:
        improvements.append("✅ Fixed spacing after 'Microsoft}'")
    else:
        issues.append("❌ Spacing after 'Microsoft}' not fixed")
    
    print("Analysis Results:")
    for improvement in improvements:
        print(f"  {improvement}")
    
    for issue in issues:
        print(f"  {issue}")
    
    if len(issues) == 0:
        print(f"\n🎉 ALL FIXES WORKING CORRECTLY!")
        return True
    else:
        print(f"\n⚠️ Some fixes need adjustment")
        return False

def apply_enhanced_fixes(latex_content: str) -> str:
    """Apply the enhanced LaTeX fixes"""
    if not latex_content:
        return latex_content
        
    # Fix "April 2008,I joined" -> "April 2008, I joined"
    latex_content = re.sub(r'(\d{4}),([A-Z])', r'\1, \2', latex_content)
    
    # Fix "problem,---for example" -> "problem---for example"  
    latex_content = re.sub(r',---', r'---', latex_content)
    
    # Fix other missing spaces after punctuation that might span components
    latex_content = re.sub(r'([.!?,;:])([A-Z])', r'\1 \2', latex_content)
    
    # Fix sentence boundaries that might be split across components
    latex_content = re.sub(r'\.([A-Z][a-z])', r'. \1', latex_content)
    
    # Fix line breaks that split words inappropriately
    latex_content = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', latex_content)
    
    # Fix line breaks in the middle of sentences
    lines = latex_content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        current_line = lines[i].strip()
        
        # Skip empty lines and LaTeX commands
        if not current_line or current_line.startswith('%') or current_line.startswith('\\'):
            fixed_lines.append(lines[i])
            i += 1
            continue
        
        # Check if this line should be joined with the next
        if (i + 1 < len(lines) and 
            current_line and 
            not current_line.endswith(('.', '!', '?', ':', '}')) and
            not current_line.endswith('\\\\') and
            lines[i + 1].strip() and
            not lines[i + 1].strip().startswith('\\') and
            not lines[i + 1].strip().startswith('%')):
            
            # Join with next line
            next_line = lines[i + 1].strip()
            joined_line = current_line + ' ' + next_line
            fixed_lines.append(joined_line)
            i += 2  # Skip the next line since we joined it
        else:
            fixed_lines.append(lines[i])
            i += 1
    
    latex_content = '\n'.join(fixed_lines)
    
    # Fix specific spacing issues around LaTeX commands
    # Fix "Microsoft}working" -> "Microsoft} working"
    latex_content = re.sub(r'(\}+)([a-zA-Z])', r'\1 \2', latex_content)
    
    # Fix ". In\nApril" -> ". In April" 
    latex_content = re.sub(r'\. ([A-Z])\n([a-z])', r'. \1\2', latex_content)
    
    # Clean up any double spaces created by fixes
    latex_content = re.sub(r'  +', ' ', latex_content)
    
    # Clean up excessive newlines but preserve structure
    latex_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', latex_content)
    
    return latex_content

if __name__ == "__main__":
    success = test_enhanced_fixes()
    
    if success:
        print("\n✅ Enhanced LaTeX fixes are working correctly!")
    else:
        print("\n⚠️ Some fixes need refinement.")
