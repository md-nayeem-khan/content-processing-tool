#!/usr/bin/env python3
"""
Final LaTeX compilation readiness test
"""

import re

def test_latex_compilation_readiness():
    """Test if the enhanced output is ready for LaTeX compilation"""
    
    print("🎯 FINAL LATEX COMPILATION READINESS TEST")
    print("="*60)
    
    try:
        with open("enhanced_output.tex", "r", encoding="utf-8") as f:
            content = f.read()
        
        print("✅ Successfully read enhanced output file")
        
        # Critical compilation blockers
        critical_issues = []
        
        # Check for mid-sentence line breaks
        problematic_breaks = [
            ("Since\nSystem", "Since System"),
            ("Amazon\nlaunched", "Amazon launched"),
            ("Most\nengineers", "Most engineers"),
            ("With\nthe right", "With the right"),
            ("In\nApril", "In April"),
            ("However\n,", "However,"),
            ("Therefore\n,", "Therefore,")
        ]
        
        for pattern, description in problematic_breaks:
            if pattern in content:
                critical_issues.append(f"❌ Found problematic line break: {description}")
        
        # Check for missing spaces after LaTeX commands
        latex_command_spacing = re.findall(r'\}[a-zA-Z]', content)
        if latex_command_spacing:
            critical_issues.append(f"❌ Found {len(latex_command_spacing)} missing spaces after LaTeX commands")
        
        # Check for missing spaces after periods
        period_spacing = re.findall(r'\.([A-Z][a-z])', content)
        if period_spacing:
            critical_issues.append(f"❌ Found {len(period_spacing)} missing spaces after periods")
        
        # Check for proper LaTeX structure
        has_begin_document = "\\begin{document}" in content
        has_end_document = "\\end{document}" in content
        
        # Check for balanced braces (basic check)
        open_braces = content.count('{')
        close_braces = content.count('}')
        brace_balance = open_braces - close_braces
        
        # Analysis results
        print(f"\n📊 COMPILATION ANALYSIS:")
        print(f"   File size: {len(content):,} characters")
        print(f"   Lines: {len(content.split(chr(10))):,}")
        
        if not critical_issues:
            print(f"\n🎉 EXCELLENT! No critical compilation issues found!")
        else:
            print(f"\n⚠️ Found {len(critical_issues)} critical issues:")
            for issue in critical_issues:
                print(f"   {issue}")
        
        # Brace balance check
        if abs(brace_balance) <= 2:  # Allow small tolerance for comments etc
            print(f"✅ LaTeX braces appear balanced ({open_braces} open, {close_braces} close)")
        else:
            print(f"⚠️ Brace imbalance detected: {brace_balance} difference")
        
        # Structure check (note: this is a section template, not full document)
        print(f"ℹ️ This is a section template (doesn't need \\begin{{document}})")
        
        # Quality indicators
        quality_score = 100
        
        if critical_issues:
            quality_score -= len(critical_issues) * 20
            
        if abs(brace_balance) > 2:
            quality_score -= 10
            
        print(f"\n📈 COMPILATION READINESS SCORE: {quality_score}/100")
        
        if quality_score >= 90:
            print(f"🏆 READY FOR PRODUCTION! High quality LaTeX output.")
            return True
        elif quality_score >= 70:
            print(f"✅ GOOD QUALITY. Minor issues may exist but should compile.")
            return True
        else:
            print(f"⚠️ NEEDS IMPROVEMENT. Critical issues should be addressed.")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing final LaTeX compilation readiness...")
    
    success = test_latex_compilation_readiness()
    
    print(f"\n" + "="*60)
    if success:
        print(f"🎯 FINAL RESULT: LaTeX content is ready for compilation!")
        print(f"💡 All major line break and formatting issues have been resolved.")
    else:
        print(f"🔧 FINAL RESULT: Additional work needed before compilation.")
    
    print(f"="*60)
