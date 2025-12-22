"""Test cairosvg functionality"""
try:
    import cairosvg
    print("✓ cairosvg imported successfully")
    
    test_svg = '<svg width="100" height="100"><circle cx="50" cy="50" r="40" fill="red" /></svg>'
    png_data = cairosvg.svg2png(bytestring=test_svg.encode('utf-8'))
    print(f"✓ cairosvg works! PNG size: {len(png_data)} bytes")
    
except Exception as e:
    print("✗ cairosvg failed:")
    print(f"  Error: {type(e).__name__} - {str(e)}")
    import traceback
    traceback.print_exc()
