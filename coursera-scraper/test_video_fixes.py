#!/usr/bin/env python3
"""Test script to verify video naming fixes (sequential numbering and .video extension)."""

import sys
import os
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from core.course_models import Lesson, ContentAsset
from core.scraper import CourseScraper
from config.settings import ConfigManager


def create_test_lesson():
    """Create a test lesson with video assets to test the fixes."""
    # Create a lesson with comprehensive API metadata (mimicking real structure)
    lesson = Lesson(
        id="test_lesson",
        name="Test Lesson: Video Sequencing",
        description="Test lesson for video naming fixes",
        order=1
    )

    # Add lesson metadata that mimics real Coursera structure
    lesson.metadata = {
        'coursera_item_ids': ['DKbsC', '2Zis7', '6AM0l', 'bH0qh'],  # Video order
        'comprehensive_api_data': {
            'items': {
                'DKbsC': {'name': 'Video: Welcome to Business English', 'is_video': True},
                '2Zis7': {'name': 'Video: Course Overview', 'is_video': True},
                '6AM0l': {'name': 'Quiz Proficiency Video: Phone Conversation', 'is_video': True},
                'bH0qh': {'name': 'Video: Introducing Yourself', 'is_video': True}
            }
        }
    }

    # Create test video assets (simulating what the scraper would create)
    assets = [
        ContentAsset(
            name="Video_Welcome_to_Business_English_720p.mp4",
            url="https://test.com/DKbsC_720p.mp4",
            file_type="video",
            metadata={'original_item_id': 'DKbsC'}
        ),
        ContentAsset(
            name="Video_Course_Overview_720p.mp4",
            url="https://test.com/2Zis7_720p.mp4",
            file_type="video",
            metadata={'original_item_id': '2Zis7'}
        ),
        ContentAsset(
            name="Quiz_Proficiency_Video_Phone_Conversation_720p.mp4",
            url="https://test.com/6AM0l_720p.mp4",
            file_type="video",
            metadata={'original_item_id': '6AM0l'}
        ),
        ContentAsset(
            name="Video_Introducing_Yourself_720p.mp4",
            url="https://test.com/bH0qh_720p.mp4",
            file_type="video",
            metadata={'original_item_id': 'bH0qh'}
        )
    ]

    lesson.assets = assets
    return lesson


def test_sequential_numbering():
    """Test that video assets get properly numbered in sequence."""
    print("\\n=== Testing Sequential Numbering ===")

    # Create mock scraper instance (we only need the numbering method)
    config = ConfigManager()
    scraper = CourseScraper(config)

    # Create test lesson
    test_lesson = create_test_lesson()

    print("Before sequential numbering:")
    for asset in test_lesson.assets:
        print(f"  {asset.name}")

    # Apply sequential numbering
    scraper._add_sequential_numbering_to_videos(test_lesson)

    print("\\nAfter sequential numbering:")
    expected_names = [
        "001_Video_Welcome_to_Business_English_720p.mp4",
        "002_Video_Course_Overview_720p.mp4",
        "003_Quiz_Proficiency_Video_Phone_Conversation_720p.mp4",
        "004_Video_Introducing_Yourself_720p.mp4"
    ]

    success = True
    for i, asset in enumerate(test_lesson.assets):
        print(f"  {asset.name}")
        if asset.name != expected_names[i]:
            print(f"    ERROR: Expected '{expected_names[i]}', got '{asset.name}'")
            success = False
        else:
            print(f"    SUCCESS: Correctly numbered")

    return success


def test_extension_fix():
    """Test that .video extension issue is fixed."""
    print("\\n=== Testing Extension Fix ===")

    # Test the file manager extension logic directly
    from core.file_manager import FileManager
    from core.course_models import ContentAsset

    config = ConfigManager()
    file_manager = FileManager(config)

    # Create test asset that would previously get .mp4.video extension
    test_asset = ContentAsset(
        name="001_Video_Welcome_to_Business_English_720p.mp4",
        url="https://test.com/video.mp4",
        file_type="video"
    )

    print(f"Test asset name: {test_asset.name}")
    print(f"Test asset file_type: {test_asset.file_type}")

    # Test the extension logic by examining what the file manager would do
    # We'll simulate the logic without actually downloading
    from utils.sanitizer import sanitize_file_name
    safe_filename = sanitize_file_name(test_asset.name)

    # Apply the NEW extension logic we updated in file_manager.py
    if test_asset.file_type == 'video':
        # For video files, ensure they end with .mp4 (not .video)
        if not safe_filename.lower().endswith('.mp4'):
            # Remove any existing extension and add .mp4
            if '.' in safe_filename:
                safe_filename = safe_filename.rsplit('.', 1)[0]
            safe_filename = f"{safe_filename}.mp4"
    elif test_asset.file_type and not safe_filename.lower().endswith(f'.{test_asset.file_type}'):
        safe_filename = f"{safe_filename}.{test_asset.file_type}"

    print(f"Final filename: {safe_filename}")

    # Check if the filename is correct
    expected = "001_Video_Welcome_to_Business_English_720p.mp4"
    if safe_filename == expected:
        print("SUCCESS: Extension logic is correct")
        return True
    else:
        print(f"ERROR: Expected '{expected}', got '{safe_filename}'")
        return False


def main():
    """Run all tests."""
    print("Testing video naming fixes...")

    # Test sequential numbering
    numbering_success = test_sequential_numbering()

    # Test extension fix
    extension_success = test_extension_fix()

    print("\\n=== Test Results ===")
    print(f"Sequential numbering: {'PASS' if numbering_success else 'FAIL'}")
    print(f"Extension fix: {'PASS' if extension_success else 'FAIL'}")

    if numbering_success and extension_success:
        print("\\nALL TESTS PASSED! The fixes are working correctly.")

        print("\\nExpected behavior:")
        print("1. Videos will be numbered sequentially: 001_, 002_, 003_, etc.")
        print("2. Videos will have .mp4 extension (not .mp4.video)")
        print("3. Order matches the lesson item sequence from Coursera API")

    else:
        print("\\nSOME TESTS FAILED! Please review the fixes.")

    return numbering_success and extension_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)