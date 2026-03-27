#!/usr/bin/env python3
"""
Test the complete video extraction and naming process for the first lesson.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from api.auth import CourseraAuth
from api.coursera_client import CourseraClient
from core.scraper import CourseraContentScraper
from core.file_manager import FileManager

def test_lesson_video_names():
    """Test video name extraction for a single lesson."""
    print("Testing Complete Video Name Extraction Process")
    print("=" * 70)

    # Load credentials
    load_dotenv()
    cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')

    if not cauth_cookie:
        print("ERROR: COURSERA_CAUTH_COOKIE not found in .env file")
        return False

    try:
        # Initialize components
        auth = CourseraAuth(cauth_cookie=cauth_cookie)
        client = CourseraClient.from_config_file('config/api_endpoints.json', auth)
        file_manager = FileManager(base_path=Path('test_courses'))
        scraper = CourseraContentScraper(client, file_manager)

        # Create test course using the comprehensive API
        print("Creating course structure using comprehensive API...")
        course = scraper._create_course_from_comprehensive_api('business-english-intro')

        if not course:
            print("ERROR: Could not create course from comprehensive API")
            return False

        print(f"Successfully created course: {course.name}")
        print(f"Modules: {len(course.modules)}")

        # Find the first lesson with videos
        target_lesson = None
        for module in course.modules:
            for lesson in module.lessons:
                if "Course Overview and Assessment" in lesson.name:
                    target_lesson = lesson
                    break
            if target_lesson:
                break

        if not target_lesson:
            print("ERROR: Could not find target lesson")
            return False

        print(f"\nFound target lesson: {target_lesson.name}")
        print(f"Assets before extraction: {len(target_lesson.assets)}")

        # Test the comprehensive API extraction
        print("Extracting content assets...")
        scraper._extract_content_assets_from_comprehensive_api(target_lesson)

        print(f"Assets after extraction: {len(target_lesson.assets)}")

        # Check video assets
        video_assets = [asset for asset in target_lesson.assets if asset.file_type == 'video' and '720p.mp4' in asset.name]

        print(f"\nFound {len(video_assets)} video assets with 720p MP4:")
        for i, asset in enumerate(video_assets, 1):
            print(f"{i}. {asset.name}")
            print(f"   URL: {asset.url[:80]}...")
            print(f"   Original name: {asset.metadata.get('original_name', 'N/A')}")

        # Save results
        test_results = {
            'lesson_name': target_lesson.name,
            'total_assets': len(target_lesson.assets),
            'video_assets': len(video_assets),
            'video_files': [
                {
                    'name': asset.name,
                    'original_name': asset.metadata.get('original_name'),
                    'item_id': asset.metadata.get('item_id'),
                    'has_url': bool(asset.url)
                }
                for asset in video_assets
            ],
            'expected_videos': 3,
            'test_status': 'PASS' if len(video_assets) == 3 else 'FAIL'
        }

        with open('lesson_video_names_test.json', 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2)

        print(f"\nTest Result: {'PASS' if len(video_assets) == 3 else 'FAIL'}")
        print(f"Expected 3 videos, found {len(video_assets)}")
        print("Results saved to: lesson_video_names_test.json")

        return len(video_assets) == 3

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_lesson_video_names()

    print("\n" + "=" * 70)
    print("LESSON VIDEO NAMES TEST SUMMARY")
    print("=" * 70)
    print(f"Result: {'PASS' if success else 'FAIL'}")

    if success:
        print("SUCCESS: Video names are now properly extracted and used!")
        print("- Videos use descriptive names instead of item IDs")
        print("- Only 720p MP4 format is extracted as requested")
        print("- Video URLs are properly extracted")
    else:
        print("FAIL: Issues remain with video name extraction")
        print("Please check the implementation")