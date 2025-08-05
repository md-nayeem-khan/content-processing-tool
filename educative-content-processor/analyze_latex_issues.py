#!/usr/bin/env python3
"""
Test LaTeX compilation issues
"""

def analyze_latex_content():
    """Analyze the LaTeX content for common compilation issues"""
    
    # Sample problematic content from user
    content = r"""A \textbf{System Design interview} is a technical evaluation of a candidate's ability to build robust and scalable systems. Unlike coding interviews, which typically involve a single solution, System Design interviews are open to discussion and involve multiple possible solutions that can be re-iterated. For many software engineers, System Design Interview questions remain a mysterious challenge.Most engineers have never actually worked on large-scale systems before, so explaining how to build one seems daunting."""
    
    print("🔍 ANALYZING LATEX CONTENT FOR COMPILATION ISSUES")
    print("="*60)
    
    issues_found = []
    
    # Check for missing spaces after periods
    import re
    missing_spaces = re.findall(r'\.[A-Z]', content)
    if missing_spaces:
        issues_found.append(f"Missing spaces after periods: {missing_spaces}")
    
    # Check for very long lines (over 80 chars without breaks)
    lines = content.split('\n')
    long_lines = [i for i, line in enumerate(lines, 1) if len(line) > 120]
    if long_lines:
        issues_found.append(f"Very long lines at: {long_lines}")
    
    # Check for common LaTeX issues
    if '\\texttt{I joined' in content:
        issues_found.append("Suspicious \\texttt usage - should be normal text")
    
    if issues_found:
        print("❌ ISSUES FOUND:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
    else:
        print("✅ No obvious issues found")
    
    # Suggested fixes
    print(f"\n🔧 SUGGESTED FIXES:")
    print(f"   1. Add space after periods: challenge.Most → challenge. Most")
    print(f"   2. Fix texttt usage: \\texttt{{I joined → I joined")
    print(f"   3. Break long paragraphs into smaller chunks")
    print(f"   4. Check quote environment formatting")

if __name__ == "__main__":
    analyze_latex_content()
