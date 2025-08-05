#!/usr/bin/env python3
"""
Test script to generate book structure and test section content generation
"""

from latex_generator import LaTeXBookGenerator
from main import SanitizedBookResponse, BookChapter, BookSection
import json
from pathlib import Path

def create_and_save_test_book():
    """Create and save test book structure to disk"""
    
    print("📚 Creating test book structure...")
    
    # Create mock data
    sections = [
        BookSection(
            id="4771234193080320",  # Use the example section ID from your request
            title="Resources to Prepare for a System Design Interview",
            slug="resources-to-prepare-for-system-design-interview",
            summary="Get familiar with resources and guidelines to prepare for the System Design interview."
        ),
        BookSection(
            id="5234567890123456", 
            title="System Design Fundamentals",
            slug="system-design-fundamentals",
            summary="Understanding core concepts of system design"
        )
    ]
    
    chapters = [
        BookChapter(
            id="1",
            title="System Design Interview Preparation",
            sections=sections,
            summary="Comprehensive guide to preparing for system design interviews"
        )
    ]
    
    book_data = SanitizedBookResponse(
        success=True,
        book_title="System Design Interview Guide",
        book_summary="A comprehensive guide to system design interviews",
        book_brief_summary="Master system design interviews",
        chapters=chapters,
        total_chapters=1,
        total_sections=2,
        course_url="https://example.com/system-design-course"
    )
    
    # Generate and save book
    generator = LaTeXBookGenerator()
    generated_files = generator.generate_book(book_data, "test-system-design")
    
    # Save to disk
    book_path = generator.save_book_to_disk(generated_files, "test-system-design")
    
    print(f"✅ Book structure saved to: {book_path}")
    
    # Read and display metadata
    metadata_file = Path(book_path) / "sections" / "section_metadata.json"
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        print(f"\n📋 Book Metadata:")
        print(f"Title: {metadata['book_title']}")
        print(f"Chapters: {len(metadata['chapters'])}")
        
        for chapter in metadata['chapters']:
            print(f"\nChapter {chapter['chapter_number']}: {chapter['chapter_title']}")
            for section in chapter['sections']:
                print(f"  - Section {section['section_id']}: {section['section_title']}")
                print(f"    File: {section['section_file']}")
                print(f"    Status: {section['content_status']}")
    
    return book_path, metadata

if __name__ == "__main__":
    book_path, metadata = create_and_save_test_book()
    
    print(f"\n🎯 Test book ready for section content generation!")
    print(f"Book name: test-system-design")
    print(f"Available section ID: 4771234193080320")
    print(f"Chapter number: 1")
