#!/usr/bin/env python3

import requests
import os
from section_processor import SectionContentProcessor

def test_image_formats():
    """Test different image URLs to see what formats we get"""
    
    # Create images directory
    os.makedirs("images", exist_ok=True)
    
    # Initialize processor
    processor = SectionContentProcessor()
    
    # Test some different image URLs from various sections
    test_images = [
        "https://www.educative.io/api/collection/10370001/4941429335392256/page/4771234193080320/image/5995821323911168?page_type=collection_lesson",
        "https://www.educative.io/api/collection/10370001/4941429335392256/page/4771234193080320/image/5288634861617152?page_type=collection_lesson",
        "https://www.educative.io/api/collection/10370001/4941429335392256/page/4553686424903680/image/5170756670849024?page_type=collection_lesson",
    ]
    
    print("Testing image format detection...")
    print("="*50)
    
    for i, url in enumerate(test_images):
        print(f"\nTest {i+1}: {url}")
        try:
            result = processor._download_image(url)
            if result:
                filename = result
                print(f"✅ Downloaded: {filename}")
                
                # Check file size
                filepath = os.path.join("images", filename)
                if os.path.exists(filepath):
                    size = os.path.getsize(filepath)
                    print(f"   File size: {size} bytes")
                    
                    # Check first few bytes
                    with open(filepath, 'rb') as f:
                        header = f.read(20)
                        print(f"   Header bytes: {header.hex()}")
                else:
                    print(f"   ❌ File not found: {filepath}")
            else:
                print("❌ Download failed")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*50)
    print("Image directory contents:")
    if os.path.exists("images"):
        files = os.listdir("images")
        for file in files:
            filepath = os.path.join("images", file)
            size = os.path.getsize(filepath)
            print(f"  {file} ({size} bytes)")
    else:
        print("  No images directory found")

if __name__ == "__main__":
    test_image_formats()
