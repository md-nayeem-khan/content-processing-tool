#!/usr/bin/env python3
"""
Test pandoc conversion directly
"""

try:
    import pypandoc
    
    # Test simple HTML
    test_html = "<p>This is <strong>bold</strong> text.</p>"
    
    print("Input HTML:")
    print(test_html)
    
    # Convert with pandoc
    latex_output = pypandoc.convert_text(
        test_html, 
        'latex', 
        format='html',
        extra_args=['--wrap=none', '--no-highlight', '--strip-comments']
    )
    
    print("\nPandoc LaTeX Output:")
    print(repr(latex_output))
    
    # Test with Jinja2 template
    from jinja2 import Environment, Template
    
    template_str = """Test: {{content}}
Safe: {{content | safe}}"""
    
    template = Template(template_str)
    
    result = template.render(content=latex_output)
    
    print("\nJinja2 Template Result:")
    print(repr(result))
    
except Exception as e:
    print(f"Error: {e}")
