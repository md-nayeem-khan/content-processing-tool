#!/usr/bin/env python3
"""
Utility script to analyze section ID status and provide recommendations
"""

import json
from pathlib import Path

def analyze_section_status():
    """Analyze which sections have original vs generated IDs"""
    metadata_file = Path("generated_books/grokking-the-system-design-interview/sections/section_metadata.json")
    
    if not metadata_file.exists():
        print("ERROR: Metadata file not found!")
        return
    
    # Load metadata
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    original_sections = []
    generated_sections = []
    
    # Analyze each chapter
    for chapter in metadata.get("chapters", []):
        chapter_number = chapter.get("chapter_number", 0)
        chapter_title = chapter.get("chapter_title", "")
        sections = chapter.get("sections", [])
        
        chapter_info = {
            "chapter_number": chapter_number,
            "chapter_title": chapter_title,
            "total_sections": len(sections),
            "original_ids": 0,
            "generated_ids": 0,
            "sections": []
        }
        
        for section in sections:
            section_id = section.get("section_id", "")
            section_title = section.get("section_title", "")
            
            # Heuristic: original IDs are typically 16-19 digits and start with specific patterns
            # Generated IDs from our script are 13-15 digits
            is_original = len(section_id) >= 16 and not section_id.startswith(('4000', '6550', '9256'))
            
            section_info = {
                "id": section_id,
                "title": section_title,
                "is_original": is_original,
                "id_length": len(section_id)
            }
            
            chapter_info["sections"].append(section_info)
            
            if is_original:
                chapter_info["original_ids"] += 1
                original_sections.append((chapter_number, section_title, section_id))
            else:
                chapter_info["generated_ids"] += 1
                generated_sections.append((chapter_number, section_title, section_id))
        
        # Print chapter summary
        print(f"📖 Chapter {chapter_number}: {chapter_title}")
        print(f"   📊 Total sections: {chapter_info['total_sections']}")
        print(f"   ✅ Original IDs: {chapter_info['original_ids']}")
        print(f"   🔧 Generated IDs: {chapter_info['generated_ids']}")
        
        if chapter_info["original_ids"] > 0:
            print(f"   🎯 Recommendation: Try generating this chapter - likely to succeed")
        else:
            print(f"   ⚠️  Recommendation: All IDs are generated - may fail due to API access")
        print()
    
    # Summary
    print("=" * 60)
    print("📈 OVERALL ANALYSIS")
    print("=" * 60)
    print(f"✅ Chapters with original IDs (likely to work): {len([ch for ch in metadata.get('chapters', []) if any(len(s.get('section_id', '')) >= 16 for s in ch.get('sections', []))])}")
    print(f"⚠️  Chapters with only generated IDs (may fail): {len([ch for ch in metadata.get('chapters', []) if all(len(s.get('section_id', '')) < 16 for s in ch.get('sections', []))])}")
    print(f"🔧 Total generated section IDs: {len(generated_sections)}")
    print(f"✅ Total original section IDs: {len(original_sections)}")
    
    # Recommendations
    print("\n🎯 RECOMMENDED TESTING ORDER:")
    print("=" * 40)
    working_chapters = []
    for chapter in metadata.get("chapters", []):
        if any(len(s.get("section_id", "")) >= 16 for s in chapter.get("sections", [])):
            working_chapters.append(chapter.get("chapter_number", 0))
    
    if working_chapters:
        print("Try these chapters first (have original section IDs):")
        for ch_num in sorted(working_chapters)[:10]:  # Show first 10
            chapter_data = next((ch for ch in metadata.get("chapters", []) if ch.get("chapter_number") == ch_num), {})
            print(f"   📖 Chapter {ch_num}: {chapter_data.get('chapter_title', 'Unknown')}")
    else:
        print("⚠️  No chapters with original IDs found - API access issues likely")

if __name__ == "__main__":
    analyze_section_status()
