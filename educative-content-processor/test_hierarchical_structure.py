#!/usr/bin/env python3

import requests
import time
import os
from pathlib import Path

def test_hierarchical_structure():
    """Test the new hierarchical file and image organization"""
    
    print("🏗️ TESTING NEW HIERARCHICAL STRUCTURE")
    print("="*60)
    
    # Test book creation first
    print("\n1. Creating book structure...")
    book_url = "http://localhost:8000/generate-latex-book"
    book_payload = {
        "educative_course_name": "grokking-the-system-design-interview",
        "book_name": "hierarchical-test-book",
        "use_env_credentials": True
    }
    
    try:
        book_response = requests.post(book_url, json=book_payload, timeout=60)
        
        if book_response.status_code == 200:
            book_result = book_response.json()
            
            if book_result.get("success"):
                print("✅ Book structure created successfully!")
                print(f"Book path: {book_result.get('book_path')}")
                
                # Test section generation with new structure
                print("\n2. Testing section generation with hierarchical structure...")
                
                section_url = "http://localhost:8000/generate-section-content"
                section_payload = {
                    "book_name": "hierarchical-test-book",
                    "chapter_number": 1,
                    "section_id": "4771234193080320",
                    "educative_course_name": "grokking-the-system-design-interview",
                    "author_id": "10370001",
                    "collection_id": "4941429335392256",
                    "use_env_credentials": True
                }
                
                section_response = requests.post(section_url, json=section_payload, timeout=60)
                
                if section_response.status_code == 200:
                    section_result = section_response.json()
                    
                    if section_result.get("success"):
                        print("✅ Section generated successfully!")
                        print(f"Section file: {section_result.get('section_file_path')}")
                        print(f"Generated images: {len(section_result.get('generated_images', []))}")
                        
                        # Check file structure
                        print("\n3. Verifying hierarchical structure...")
                        book_path = Path("generated_books/hierarchical-test-book")
                        
                        if book_path.exists():
                            print("\n📁 Book Directory Structure:")
                            for root, dirs, files in os.walk(book_path):
                                level = root.replace(str(book_path), '').count(os.sep)
                                indent = ' ' * 4 * level
                                print(f"{indent}{os.path.basename(root)}/")
                                subindent = ' ' * 4 * (level + 1)
                                for file in files:
                                    file_path = Path(root) / file
                                    size = file_path.stat().st_size if file_path.exists() else 0
                                    print(f"{subindent}{file} ({size} bytes)")
                            
                            # Check specific structure elements
                            print("\n✅ Structure Analysis:")
                            
                            # Check for chapter directories in files/
                            files_dir = book_path / "files"
                            chapter_dirs = [d for d in files_dir.iterdir() if d.is_dir() and d.name.startswith("chapter_")]
                            if chapter_dirs:
                                print(f"   ✅ Chapter directories found: {len(chapter_dirs)}")
                                for chapter_dir in chapter_dirs:
                                    section_files = list(chapter_dir.glob("section_*.tex"))
                                    print(f"      {chapter_dir.name}: {len(section_files)} section files")
                            else:
                                print("   ❌ No chapter directories found in files/")
                            
                            # Check for hierarchical image structure
                            images_dir = book_path / "Images"
                            if images_dir.exists():
                                chapter_image_dirs = [d for d in images_dir.iterdir() if d.is_dir() and d.name.startswith("chapter_")]
                                if chapter_image_dirs:
                                    print(f"   ✅ Image chapter directories found: {len(chapter_image_dirs)}")
                                    for chapter_dir in chapter_image_dirs:
                                        section_dirs = [d for d in chapter_dir.iterdir() if d.is_dir() and d.name.startswith("section_")]
                                        print(f"      {chapter_dir.name}: {len(section_dirs)} section directories")
                                        for section_dir in section_dirs:
                                            image_files = list(section_dir.glob("*.*"))
                                            if image_files:
                                                print(f"         {section_dir.name}: {len(image_files)} images")
                                                for img in image_files:
                                                    print(f"            - {img.name}")
                                else:
                                    print("   ⚠️ No hierarchical image directories found (may be expected if no images)")
                            else:
                                print("   ❌ Images directory not found")
                        
                        # Test LaTeX compilation readiness
                        print("\n4. Testing LaTeX references...")
                        
                        # Check if chapter files reference sections correctly
                        chapter_files = list((book_path / "files").glob("chapter_*.tex"))
                        if chapter_files:
                            sample_chapter = chapter_files[0]
                            with open(sample_chapter, 'r', encoding='utf-8') as f:
                                chapter_content = f.read()
                            
                            if "\\IfFileExists{chapter_" in chapter_content:
                                print("   ✅ Chapter files use new hierarchical section references")
                            else:
                                print("   ❌ Chapter files still use old section references")
                        
                    else:
                        print(f"❌ Section generation failed: {section_result.get('error_message')}")
                else:
                    print(f"❌ Section API call failed: {section_response.status_code}")
                    print(section_response.text[:500])
            else:
                print(f"❌ Book creation failed: {book_result.get('error_message')}")
        else:
            print(f"❌ Book API call failed: {book_response.status_code}")
            print(book_response.text[:500])
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")

if __name__ == "__main__":
    test_hierarchical_structure()
