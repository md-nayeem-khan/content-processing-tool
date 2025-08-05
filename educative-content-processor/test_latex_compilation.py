#!/usr/bin/env python3
"""
Test LaTeX compilation fixes
This script tests the enhanced _clean_latex_output method on the problematic content
"""

import re
from section_processor import SectionContentProcessor

def test_latex_cleaning():
    """Test the LaTeX cleaning on problematic content"""
    
    # Sample problematic content from user (extracted key problems)
    problematic_latex = """A \\textbf{System Design interview} is a technical evaluation of a candidate's ability to build robust and scalable systems. 
Unlike coding interviews, which typically involve a single solution, System Design interviews are open to discussion and involve multiple possible solutions that can be re-iterated.For many software engineers, System Design Interview questions remain a mysterious challenge.Most engineers have never actually worked on large-scale systems before, so explaining how to build one seems daunting.Since System Design interview questions are often open-ended, it can be difficult to know the best way to prepare.However, as someone who has participated in hundreds of System Design interviews, I can assure you there is a correct way to approach these questions.
In April 2008,I joined an \\href{https://www.educative.io/blog/25-years-of-developer-interviews}{internal team at Microsoft}working on a large-scale project to build a distributed storage solution.Amazon launched its Simple Storage Service in 2006, and Google launched its PaaS solution, Google App Engine, the same month I joined the team, so we were in the early land grab of cloud computing.Less than two years later, that project was launched to the world as a new product category: Microsoft Azure.By the time I started Educative, I had participated in hundreds of interview loops as both interviewee and interviewer.As Educative has scaled, I have participated in hundreds more.Design questions are open ended, and they're intentionally vague to start with.Such vagueness mimics the reality of modern day business.Interviewers often ask about a well-known problem,---for example, designing WhatsApp."""
    
    print("=== TESTING LATEX CLEANING ===")
    print("Original problematic content:")
    print(repr(problematic_latex[:200]))
    print("\n" + "="*50 + "\n")
    
    # Initialize processor and test cleaning
    processor = SectionContentProcessor()
    cleaned_latex = processor._clean_latex_output(problematic_latex)
    
    print("Cleaned content:")
    print(repr(cleaned_latex[:200]))
    print("\n" + "="*50 + "\n")
    
    print("Full cleaned content:")
    print(cleaned_latex)
    print("\n" + "="*50 + "\n")
    
    # Check for specific issues
    issues = []
    
    # Check for missing spaces after periods
    if re.search(r'\.([A-Z][a-z])', cleaned_latex):
        issues.append("❌ Missing spaces after periods found")
    else:
        print("✅ No missing spaces after periods")
    
    # Check for malformed href commands  
    if re.search(r'\\href\{[^}]*\{[^}]*\}\}', cleaned_latex):
        issues.append("❌ Malformed href commands found")
    else:
        print("✅ No malformed href commands")
    
    # Check for specific problematic patterns
    if "2008,I" in cleaned_latex:
        issues.append("❌ '2008,I' pattern still present")
    else:
        print("✅ Fixed '2008,I' -> '2008, I'")
    
    if "Azure.By" in cleaned_latex:
        issues.append("❌ 'Azure.By' pattern still present") 
    else:
        print("✅ Fixed 'Azure.By' -> 'Azure. By'")
        
    if ",---for" in cleaned_latex:
        issues.append("❌ ',---for' pattern still present")
    else:
        print("✅ Fixed ',---for' -> '---for'")
    
    # Check for lines that are too long (over 120 chars)
    long_lines = [line for line in cleaned_latex.split('\n') if len(line) > 120 and not line.strip().startswith('\\')]
    if long_lines:
        print(f"⚠️  Found {len(long_lines)} lines over 120 characters")
        for i, line in enumerate(long_lines[:3]):  # Show first 3
            print(f"   Line {i+1}: {len(line)} chars - {line[:80]}...")
    else:
        print("✅ No overly long lines found")
    
    if issues:
        print("\n❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("\n✅ ALL TESTS PASSED - LaTeX should compile properly")
        return True

def test_specific_patterns():
    """Test specific pattern fixes"""
    print("\n=== TESTING SPECIFIC PATTERNS ===")
    
    processor = SectionContentProcessor()
    
    test_cases = [
        ("April 2008,I joined", "April 2008, I joined"),
        ("Azure.By the time", "Azure. By the time"), 
        ("problem,---for example", "problem---for example"),
        ("interview.Such vagueness", "interview. Such vagueness"),
        ("systems.However, as someone", "systems. However, as someone"),
        ("questions.Since System Design", "questions. Since System Design"),
        ("\\href{url{text}}", "\\href{url}{text}"),
        ("\\href{url}text", "\\href{url}{text}")
    ]
    
    for input_text, expected in test_cases:
        cleaned = processor._clean_latex_output(input_text)
        if expected in cleaned:
            print(f"✅ '{input_text}' -> '{expected}'")
        else:
            print(f"❌ '{input_text}' -> '{cleaned}' (expected '{expected}')")

if __name__ == "__main__":
    print("Testing LaTeX cleaning improvements...")
    print("="*60)
    
    success = test_latex_cleaning()
    test_specific_patterns()
    
    if success:
        print("\n🎉 All tests passed! LaTeX content should now compile properly.")
    else:
        print("\n⚠️  Some issues detected. Review the output above.")
