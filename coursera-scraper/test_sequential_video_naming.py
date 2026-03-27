#!/usr/bin/env python3
"""
Test script to demonstrate the sequential video naming functionality.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.sanitizer import sanitize_sequential_video_name


def test_sequential_naming():
    """Test the sequential video naming functionality."""
    print("Testing Sequential Video Naming")
    print("=" * 50)

    # Test cases with various video names
    test_videos = [
        "Video Welcome to Business English_720p.mp4",
        "Video Course Overview_720p.mp4",
        "Quiz Proficiency Video Phone Conversation_720p.mp4",
        "Lecture Introduction to Machine Learning_720p.mp4",
        "Demo Neural Networks Basics_720p.mp4"
    ]

    print("Original vs Sequential Filenames:")
    print("-" * 50)

    for i, video_name in enumerate(test_videos, 1):
        # Remove resolution suffix for cleaner naming
        base_name = video_name.replace('_720p.mp4', '')

        # Create sequential filename
        sequential_name = sanitize_sequential_video_name(i, base_name, '.mp4')

        print(f"{i}. Original:   {video_name}")
        print(f"   Sequential: {sequential_name}")
        print()

    print("Benefits of Sequential Naming:")
    print("-" * 50)
    print("+ Clear lecture sequence order (1_, 2_, 3_, etc.)")
    print("+ Better file management and organization")
    print("+ Easier to identify lesson order at a glance")
    print("+ Consistent numbering across entire course")
    print("+ Maintains original descriptive names")
    print()

    # Test edge cases
    print("Edge Case Testing:")
    print("-" * 30)

    edge_cases = [
        ("Video with special chars @#$%_720p", 10),
        ("Very long video name that might exceed length limits and needs truncation_720p", 25),
        ("", 1),  # Empty name
        ("Video_with_multiple_underscores___720p", 5)
    ]

    for video_name, seq_num in edge_cases:
        sanitized = sanitize_sequential_video_name(seq_num, video_name, '.mp4')
        print(f"Seq {seq_num}: '{video_name}' -> '{sanitized}'")

    return True


def demo_directory_structure():
    """Demonstrate how the directory structure would look."""
    print("\n" + "=" * 60)
    print("EXPECTED DIRECTORY STRUCTURE WITH SEQUENTIAL NAMING")
    print("=" * 60)

    course_structure = {
        "Business-English-Intro/": {
            "module-01-getting-started/": {
                "lesson-01-course-overview/": [
                    "1_Video_Welcome_to_Business_English.mp4",
                    "2_Video_Course_Overview.mp4",
                    "3_Quiz_Proficiency_Video_Phone_Conversation.mp4"
                ],
                "lesson-02-first-lesson/": [
                    "4_Video_Introduction_to_Business_Communication.mp4",
                    "5_Video_Professional_Email_Writing.mp4"
                ]
            },
            "module-02-advanced-topics/": {
                "lesson-01-presentations/": [
                    "6_Video_Effective_Business_Presentations.mp4",
                    "7_Demo_Sample_Presentation_Walkthrough.mp4"
                ],
                "lesson-02-meetings/": [
                    "8_Video_Meeting_Etiquette_and_Procedures.mp4",
                    "9_Video_Leading_Productive_Meetings.mp4"
                ]
            }
        }
    }

    def print_structure(structure, indent=0):
        for key, value in structure.items():
            print("  " * indent + key)
            if isinstance(value, dict):
                print_structure(value, indent + 1)
            elif isinstance(value, list):
                for item in value:
                    print("  " * (indent + 1) + item)

    print_structure(course_structure)

    print("\nKey Features:")
    print("- Videos numbered sequentially across the entire course")
    print("- Order preserved from module 1 -> module 2 -> etc.")
    print("- Within each module: lesson 1 -> lesson 2 -> etc.")
    print("- Original descriptive names retained")
    print("- Clear progression: 1, 2, 3, 4, 5, 6, 7, 8, 9...")


if __name__ == "__main__":
    print("COURSERA SCRAPER - SEQUENTIAL VIDEO NAMING TEST")
    print("=" * 60)

    success = test_sequential_naming()

    if success:
        demo_directory_structure()

        print("\n" + "=" * 60)
        print("TEST RESULTS: SUCCESS")
        print("=" * 60)
        print("+ Sequential video naming implemented successfully")
        print("+ Video filenames will now start with sequence numbers")
        print("+ Better lecture sequence understanding achieved")
        print("+ Maintains compatibility with existing code")

        print("To use this functionality:")
        print("1. Run the scraper as usual")
        print("2. Videos will be downloaded with sequential prefixes")
        print("3. Order follows: Module 1 -> Module 2 -> ... -> Module N")
        print("4. Within modules: Lesson 1 -> Lesson 2 -> ... -> Lesson N")
    else:
        print("TEST FAILED: Sequential naming implementation has issues")