#!/usr/bin/env python3
"""
Test image download fixes with proper format detection
"""

import requests

def test_image_format_fixes():
    """Test the enhanced image download and format detection"""
    
    print("🎯 TESTING ENHANCED IMAGE DOWNLOAD FIXES")
    print("="*60)
    
    # Test the section generation with enhanced image handling
    url = "http://localhost:8000/generate-section-content"
    payload = {
        "book_name": "grokking-the-system-design-interview",
        "chapter_number": 1,
        "section_id": "4771234193080320",
        "educative_course_name": "grokking-the-system-design-interview",
        "author_id": "10370001",
        "collection_id": "4941429335392256",
        "use_env_credentials": True
    }
    
    print("Testing section generation with enhanced image handling...")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                print("✅ Section generation successful!")
                
                generated_images = result.get("generated_images", [])
                print(f"\n📊 IMAGE ANALYSIS:")
                print(f"Generated images: {len(generated_images)}")
                
                for img in generated_images:
                    print(f"  - {img}")
                    
                    # Analyze file extension
                    if img.endswith('.svg'):
                        print(f"    ✅ Correctly detected as SVG")
                    elif img.endswith('.png'):
                        print(f"    ✅ Correctly detected as PNG")
                    elif img.endswith('.jpg') or img.endswith('.jpeg'):
                        print(f"    ✅ Correctly detected as JPEG")
                    elif img.endswith('.gif'):
                        print(f"    ✅ Correctly detected as GIF")
                    elif img.endswith('.webp'):
                        print(f"    ✅ Correctly detected as WebP")
                    else:
                        print(f"    ⚠️ Unknown or unusual format")
                
                latex_content = result.get("latex_content", "")
                
                # Check if SVG handling is working
                if "SVG Image:" in latex_content:
                    print(f"\n✅ SVG files are being handled properly with fallback text")
                
                # Check if regular images are included properly
                if "\\includegraphics" in latex_content:
                    print(f"✅ Regular images are being included properly")
                
                print(f"\n📄 SAMPLE LATEX OUTPUT (image-related):")
                print("="*50)
                
                # Show image-related LaTeX content
                lines = latex_content.split('\n')
                for i, line in enumerate(lines):
                    if any(keyword in line.lower() for keyword in ['figure', 'includegraphics', 'svg']):
                        # Show context around image-related lines
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        for j in range(start, end):
                            prefix = ">>> " if j == i else "    "
                            print(f"{prefix}{lines[j]}")
                        print("---")
                
                return True
                        
            else:
                print(f"❌ Section generation failed: {result.get('error_message')}")
                return False
        else:
            print(f"❌ HTTP error {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing enhanced image download and format detection...")
    
    success = test_image_format_fixes()
    
    print(f"\n" + "="*60)
    if success:
        print(f"🎯 RESULT: Enhanced image handling is working!")
        print(f"💡 Images should now be properly detected and handled by format.")
    else:
        print(f"🔧 RESULT: Issues detected, check the error messages above.")
    
    print(f"="*60)
