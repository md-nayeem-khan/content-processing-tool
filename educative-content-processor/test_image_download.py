#!/usr/bin/env python3
"""
Test image download functionality with enhanced debugging
"""

import requests
import os
from pathlib import Path

def test_image_download_debug():
    """Test image download with detailed debugging"""
    
    print("🖼️ TESTING IMAGE DOWNLOAD FUNCTIONALITY")
    print("="*60)
    
    # Test image URL (example from Educative)
    test_image_urls = [
        "/api/collection/4941429335392256/4771234193080320/image/4299268706805637796",
        "/api/edpresso/shot/image/5685061141564388263",
    ]
    
    # Create test images directory
    test_dir = Path("test_images")
    test_dir.mkdir(exist_ok=True)
    
    for image_path in test_image_urls:
        print(f"\n🔍 Testing image: {image_path}")
        
        # Create full URL
        url = f"https://www.educative.io{image_path}"
        print(f"Full URL: {url}")
        
        # Test without authentication first
        try:
            print("\n1️⃣ Testing without authentication...")
            response = requests.head(url, timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test with basic headers
        try:
            print("\n2️⃣ Testing with basic headers...")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                "Referer": "https://www.educative.io/",
            }
            
            response = requests.head(url, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
            print(f"   Content-Length: {response.headers.get('content-length', 'Not set')}")
            
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test with authentication
        try:
            print("\n3️⃣ Testing with authentication...")
            
            cookie = os.getenv("EDUCATIVE_COOKIE")
            if not cookie:
                print("   ⚠️ No EDUCATIVE_COOKIE found in environment")
                continue
                
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept": "image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "image",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "same-origin",
                "Referer": "https://www.educative.io/",
                "Cookie": cookie
            }
            
            response = requests.get(url, headers=headers, timeout=20, stream=True)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
            print(f"   Content-Length: {response.headers.get('content-length', 'Not set')}")
            
            if response.status_code == 200:
                # Try to download a small portion to check content
                content_start = b""
                for chunk in response.iter_content(chunk_size=1024):
                    content_start = chunk
                    break
                
                print(f"   First few bytes (hex): {content_start[:20].hex()}")
                print(f"   First few bytes (text): {repr(content_start[:50])}")
                
                # Check if it looks like an image
                if content_start.startswith(b'\x89PNG'):
                    print("   ✅ Looks like a PNG image")
                elif content_start.startswith(b'\xff\xd8\xff'):
                    print("   ✅ Looks like a JPEG image")
                elif content_start.startswith(b'GIF'):
                    print("   ✅ Looks like a GIF image")
                elif content_start.startswith(b'<'):
                    print("   ❌ Looks like HTML/XML (probably an error page)")
                else:
                    print("   ⚠️ Unknown content type")
                
                # Save the full image for inspection
                filename = f"test_image_{abs(hash(url))}.bin"
                filepath = test_dir / filename
                
                response = requests.get(url, headers=headers, timeout=20)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                file_size = filepath.stat().st_size
                print(f"   📁 Saved as {filename} ({file_size} bytes)")
                
                if file_size > 0:
                    print("   ✅ File downloaded successfully")
                else:
                    print("   ❌ Downloaded file is empty")
            else:
                print(f"   ❌ Failed to download: HTTP {response.status_code}")
                try:
                    error_content = response.text[:200]
                    print(f"   Error content: {error_content}")
                except:
                    print("   Error content: Unable to decode")
                    
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\n" + "-"*40)
    
    print(f"\n📁 Test images saved in: {test_dir.absolute()}")

if __name__ == "__main__":
    test_image_download_debug()
