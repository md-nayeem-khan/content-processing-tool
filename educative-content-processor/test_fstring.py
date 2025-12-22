clean_content_0 = "\\textbf{Test content}"
clean_content_1 = "\\centering\\nImage here"

latex_output = f"""
\\noindent
\\begin{{minipage}}[t]{{0.48\\textwidth}}\\vspace{{0pt}}
{clean_content_0}
\\end{{minipage}}
\\hfill
\\begin{{minipage}}[t]{{0.48\\textwidth}}\\vspace{{0pt}}
{clean_content_1}
\\end{{minipage}}
"""

print("Generated LaTeX:")
print(latex_output)
print("\n" + "="*60)
print("Raw repr:")
print(repr(latex_output))
