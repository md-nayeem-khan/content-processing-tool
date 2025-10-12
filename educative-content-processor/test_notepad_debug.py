"""
Debug Notepad markdown to LaTeX conversion
"""

import re

# The actual REFERENCE ANSWER text from the example
reference_answer = """The five steps in correct sequence are:
1. Determine system requirements and constraints
2. Recognize components
3. Generate design
4. Identify shortcomings in the initial design
5. Discuss trade-offs and improve iteratively"""

print("=" * 80)
print("ORIGINAL MARKDOWN:")
print("=" * 80)
print(reference_answer)
print()

# Fix markdown formatting: ensure blank line before numbered lists
import re
fixed_answer = re.sub(r'([^\n])\n(\d+\.\s)', r'\1\n\n\2', reference_answer)

print("=" * 80)
print("FIXED MARKDOWN (with blank line before list):")
print("=" * 80)
print(fixed_answer)
print()

# Test with pypandoc
try:
    import pypandoc
    
    latex_output_original = pypandoc.convert_text(
        reference_answer, 
        'latex', 
        format='markdown',
        extra_args=[
            '--wrap=none',
            '--no-highlight',
        ]
    )
    
    latex_output_fixed = pypandoc.convert_text(
        fixed_answer, 
        'latex', 
        format='markdown',
        extra_args=[
            '--wrap=none',
            '--no-highlight',
        ]
    )
    
    print("=" * 80)
    print("PANDOC LATEX OUTPUT (ORIGINAL):")
    print("=" * 80)
    print(latex_output_original)
    print()
    
    print("=" * 80)
    print("PANDOC LATEX OUTPUT (FIXED):")
    print("=" * 80)
    print(latex_output_fixed)
    print()
    
except Exception as e:
    print(f"Error: {e}")
