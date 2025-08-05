#!/usr/bin/env python3
"""
Utility script to fix empty section IDs in existing book metadata
This generates fallback IDs based on section titles and slugs
"""

import json
import hashlib
from pathlib import Path

def generate_fallback_id(title, slug, chapter_number, section_index):
    """Generate a consistent fallback ID for a section"""
    # Use slug if available, otherwise use title
    base_string = slug if slug else title
    # Add chapter and section context for uniqueness
    unique_string = f"{base_string}_ch{chapter_number}_s{section_index}"
    # Generate a 15-digit ID from hash
    return str(abs(hash(unique_string)) % (10**15))

def fix_section_ids():
    """Fix empty section IDs in the metadata file"""
    metadata_file = Path("generated_books/grokking-the-system-design-interview/sections/section_metadata.json")
    
    if not metadata_file.exists():
        print("ERROR: Metadata file not found!")
        return
    
    # Load existing metadata
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Track changes
    fixed_count = 0
    
    # Process each chapter
    for chapter in metadata.get("chapters", []):
        chapter_number = chapter.get("chapter_number", 0)
        chapter_title = chapter.get("chapter_title", "")
        
        # Process each section in the chapter
        for section_index, section in enumerate(chapter.get("sections", []), 1):
            section_id = section.get("section_id", "")
            section_title = section.get("section_title", "")
            section_slug = section.get("section_slug", "")
            
            # Check if section ID needs fixing
            if not section_id or section_id.strip() == "":
                # Generate a new fallback ID
                new_id = generate_fallback_id(section_title, section_slug, chapter_number, section_index)
                section["section_id"] = new_id
                
                # Update the section file path to use the new ID
                chapter_slug = chapter.get("chapter_slug", "")
                new_file_path = f"files/chapter_{chapter_number}_{chapter_slug}/section_{new_id}.tex"
                section["section_file"] = new_file_path
                
                print(f"Fixed: Chapter {chapter_number}, Section {section_index}: '{section_title}' -> ID: {new_id}")
                fixed_count += 1
    
    # Save the updated metadata
    if fixed_count > 0:
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ SUCCESS: Fixed {fixed_count} empty section IDs")
        print(f"📁 Updated metadata file: {metadata_file}")
        print("\n🔄 You can now retry generating section content for any chapter!")
    else:
        print("ℹ️  No empty section IDs found - metadata is already correct")

if __name__ == "__main__":
    fix_section_ids()
