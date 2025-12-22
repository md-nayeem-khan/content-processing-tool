import pypandoc

# Test what Pandoc outputs for bold markdown with more text
markdown_text = """**A fresh look at system design:** Many system design courses provide a formula to attack a specific problem. This might seem attractive in a high-stress situation like an interview."""

latex = pypandoc.convert_text(
    markdown_text, 
    'latex', 
    format='markdown',
    extra_args=[
        '--wrap=none',
        '--no-highlight',
    ]
)

print("Pandoc output:")
print(repr(latex))  # Use repr to see newlines explicitly
print("\n" + "="*50 + "\n")
print("Actual output:")
print(latex)

# Test after strip
print("\n" + "="*50 + "\n")
print("After strip():")
print(repr(latex.strip()))
