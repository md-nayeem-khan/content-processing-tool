#!/usr/bin/env python3
"""
Test script for image conversion capabilities
"""
import os
import sys
from pathlib import Path

def test_libraries():
    """Test which image libraries are available"""
    results = {}
    
    # Test cairosvg
    try:
        import cairosvg
        results['cairosvg'] = '✅ Available'
    except Exception as e:
        results['cairosvg'] = f'❌ Error: {e}'
    
    # Test Wand
    try:
        from wand.image import Image
        results['wand'] = '✅ Available'
    except Exception as e:
        results['wand'] = f'❌ Error: {e}'
    
    # Test Pillow
    try:
        from PIL import Image
        results['pillow'] = '✅ Available'
    except Exception as e:
        results['pillow'] = f'❌ Error: {e}'
    
    # Test subprocess for conversion
    try:
        import subprocess
        # Try different ImageMagick command variations
        for cmd in ['magick', 'convert', 'C:\\Program Files\\ImageMagick-7.1.2-Q16-HDRI\\magick.exe']:
            try:
                result = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    results['imagemagick_cli'] = f'✅ Available ({cmd})'
                    break
            except:
                continue
        else:
            results['imagemagick_cli'] = '❌ Not found'
    except Exception as e:
        results['imagemagick_cli'] = f'❌ Error: {e}'
    
    return results

def create_test_svg():
    """Create a simple test SVG"""
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="180" height="180" fill="lightblue" stroke="darkblue" stroke-width="2"/>
  <circle cx="100" cy="100" r="50" fill="yellow" stroke="orange" stroke-width="3"/>
  <text x="100" y="110" text-anchor="middle" font-family="Arial" font-size="16" fill="black">Test SVG</text>
</svg>'''
    
    svg_path = Path('test_image.svg')
    svg_path.write_text(svg_content)
    return svg_path

def test_conversion_methods(svg_path):
    """Test different conversion methods"""
    results = {}
    
    # Method 1: cairosvg
    try:
        import cairosvg
        png_path = 'test_cairosvg.png'
        cairosvg.svg2png(url=str(svg_path), write_to=png_path, output_width=400, output_height=400)
        if os.path.exists(png_path):
            results['cairosvg'] = f'✅ Success - {png_path}'
        else:
            results['cairosvg'] = '❌ Failed - no output file'
    except Exception as e:
        results['cairosvg'] = f'❌ Error: {e}'
    
    # Method 2: Wand
    try:
        from wand.image import Image
        png_path = 'test_wand.png'
        with Image(filename=str(svg_path)) as img:
            img.format = 'png'
            img.resize(400, 400)
            img.save(filename=png_path)
        if os.path.exists(png_path):
            results['wand'] = f'✅ Success - {png_path}'
        else:
            results['wand'] = '❌ Failed - no output file'
    except Exception as e:
        results['wand'] = f'❌ Error: {e}'
    
    # Method 3: ImageMagick CLI
    try:
        import subprocess
        png_path = 'test_imagemagick_cli.png'
        
        # Try different ImageMagick command variations
        for cmd in ['magick', 'convert', 'C:\\Program Files\\ImageMagick-7.1.2-Q16-HDRI\\magick.exe']:
            try:
                result = subprocess.run([
                    cmd,
                    str(svg_path),
                    '-resize', '400x400',
                    png_path
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and os.path.exists(png_path):
                    results['imagemagick_cli'] = f'✅ Success - {png_path} (using {cmd})'
                    break
                else:
                    continue
            except:
                continue
        else:
            results['imagemagick_cli'] = '❌ Failed - ImageMagick not found'
    except Exception as e:
        results['imagemagick_cli'] = f'❌ Error: {e}'
    
    return results

if __name__ == '__main__':
    print("=== Testing Image Conversion Libraries ===")
    
    # Test library availability
    print("\n1. Library Availability:")
    lib_results = test_libraries()
    for lib, status in lib_results.items():
        print(f"   {lib}: {status}")
    
    # Create test SVG
    print("\n2. Creating test SVG...")
    svg_path = create_test_svg()
    print(f"   Created: {svg_path}")
    
    # Test conversion methods
    print("\n3. Testing Conversion Methods:")
    conversion_results = test_conversion_methods(svg_path)
    for method, status in conversion_results.items():
        print(f"   {method}: {status}")
    
    # Cleanup
    print("\n4. Cleanup:")
    test_files = ['test_image.svg', 'test_cairosvg.png', 'test_wand.png', 'test_imagemagick_cli.png']
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"   Removed: {file}")
    
    print("\n=== Test Complete ===")
