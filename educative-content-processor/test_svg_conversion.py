#!/usr/bin/env python3
"""
Quick test of the enhanced image conversion
"""
import asyncio
import sys
sys.path.append(".")
from section_processor import SectionContentProcessor

async def test_image_conversion():
    processor = SectionContentProcessor()
    
    # Initialize the images directory
    from pathlib import Path
    processor.images_dir = Path("Images")
    processor.images_dir.mkdir(exist_ok=True)
    
    # Create a test SVG
    test_svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="280" height="180" fill="lightgreen" stroke="darkgreen" stroke-width="3"/>
  <circle cx="150" cy="100" r="60" fill="yellow" stroke="orange" stroke-width="4"/>
  <text x="150" y="110" text-anchor="middle" font-family="Arial" font-size="18" fill="black">SVG to PNG Test</text>
</svg>'''
    
    # Save test SVG in the correct location
    from pathlib import Path
    test_svg_path = processor.images_dir / "test_drawio.svg"
    test_svg_path.write_text(test_svg_content, encoding='utf-8')
    
    print("🧪 Testing SVG to PNG conversion...")
    print(f"Created test SVG: {test_svg_path}")
    
    # Test conversion
    result = await processor._convert_image_to_png(str(test_svg_path))
    
    if result:
        print(f"✅ Conversion successful: {result}")
        # Check if the PNG file exists - it will be in the Images directory
        png_path = Path(result)
        if png_path.exists():
            print(f"✅ PNG file exists: {png_path} ({png_path.stat().st_size} bytes)")
        else:
            print(f"❌ PNG file not found: {png_path}")
    else:
        print("❌ Conversion failed")
    
    # Cleanup
    if test_svg_path.exists():
        test_svg_path.unlink()
        print(f"🧹 Cleaned up: {test_svg_path}")

if __name__ == '__main__':
    asyncio.run(test_image_conversion())
