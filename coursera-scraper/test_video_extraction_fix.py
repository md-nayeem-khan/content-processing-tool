#!/usr/bin/env python3
"""
Test script to verify the multiple video extraction and download fixes.
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
from core.course_models import Lesson, ContentAsset
from core.file_manager import FileManager
from api.downloader import VideoDownloader

def test_video_extraction_fix():
    """Test the fixed video extraction for multiple videos per lesson."""
    print("Testing Fixed Video Extraction for Multiple Videos")
    print("=" * 70)

    # Load credentials
    load_dotenv()
    cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')

    if not cauth_cookie:
        print("ERROR: COURSERA_CAUTH_COOKIE not found in .env file")
        return

    try:
        # Initialize components
        auth = CourseraAuth(cauth_cookie=cauth_cookie)
        client = CourseraClient.from_config_file('config/api_endpoints.json', auth)
        file_manager = FileManager(base_path=Path('courses'))
        scraper = CourseraContentScraper(client, file_manager)

        # Test data for the lesson with multiple videos
        course_id = "46b4tHEkEeWbbw5cIAKQrw"
        video_item_ids = ["DKbsC", "2Zis7", "6AM0l"]

        print(f"Course ID: {course_id}")
        print(f"Testing {len(video_item_ids)} videos: {video_item_ids}")
        print()

        # Test individual video extraction
        extracted_assets = []
        for item_id in video_item_ids:
            print(f"Testing video extraction for {item_id}...")

            try:
                # Use the updated video extraction method
                video_assets = scraper._extract_video_assets_by_item_id(course_id, item_id)

                if video_assets:
                    print(f"  ✓ Successfully extracted {len(video_assets)} assets")
                    for asset in video_assets:
                        print(f"    - {asset.name} ({asset.file_type})")
                        print(f"      URL: {asset.url[:80]}...")
                        extracted_assets.append(asset)
                else:
                    print(f"  ✗ No assets extracted for {item_id}")

            except Exception as e:
                print(f"  ✗ Error extracting {item_id}: {e}")

        print(f"\nSUMMARY:")
        print(f"Total assets extracted: {len(extracted_assets)}")

        # Check if we have the expected videos
        video_720p_assets = [asset for asset in extracted_assets if "720p.mp4" in asset.name]
        print(f"720p MP4 videos found: {len(video_720p_assets)}")

        # Verify asset naming includes item_id
        print("\nAsset names:")
        for asset in video_720p_assets:
            print(f"  - {asset.name}")

        # Test if all expected videos are present
        expected_videos = [f"video_{item_id}_720p.mp4" for item_id in video_item_ids]
        actual_videos = [asset.name for asset in video_720p_assets]

        print(f"\nExpected videos: {expected_videos}")
        print(f"Actual videos:   {actual_videos}")

        success = len(video_720p_assets) == len(video_item_ids)
        print(f"\nTest Result: {'PASS' if success else 'FAIL'}")

        # Save test results for analysis
        test_results = {
            'test_name': 'video_extraction_fix',
            'course_id': course_id,
            'video_item_ids': video_item_ids,
            'extracted_assets': [
                {
                    'name': asset.name,
                    'url': asset.url,
                    'file_type': asset.file_type,
                    'metadata': asset.metadata
                }
                for asset in extracted_assets
            ],
            'summary': {
                'total_assets': len(extracted_assets),
                'video_720p_assets': len(video_720p_assets),
                'expected_videos': len(video_item_ids),
                'test_result': 'PASS' if success else 'FAIL'
            }
        }

        with open('video_extraction_fix_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2)

        print(f"\nTest results saved to: video_extraction_fix_test_results.json")
        return success

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_lesson_metadata_update():
    """Test if lesson metadata gets updated with correct video assets."""
    print("\n" + "=" * 70)
    print("Testing Lesson Metadata Update")
    print("=" * 70)

    # Read the current lesson metadata
    lesson_metadata_path = Path('courses/introduction-to-business-english-communication-course/module-01-introduction-to-business-english-communication/lesson-01-lesson-1-course-overview-and-assessment/lesson_metadata.json')

    if lesson_metadata_path.exists():
        with open(lesson_metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        print("Current lesson metadata assets:")
        for i, asset in enumerate(metadata.get('assets', []), 1):
            print(f"  {i}. {asset.get('name', 'Unknown')} ({asset.get('file_type', 'Unknown')})")
            if 'url' in asset and asset['url']:
                print(f"     URL: {asset['url'][:80]}...")
            else:
                print("     URL: Not set")

        # Check if we have video assets with URLs
        video_assets = [asset for asset in metadata.get('assets', []) if asset.get('file_type') == 'video']
        video_assets_with_urls = [asset for asset in video_assets if asset.get('url')]

        print(f"\nVideo assets: {len(video_assets)}")
        print(f"Video assets with URLs: {len(video_assets_with_urls)}")

        if len(video_assets_with_urls) >= 3:
            print("✓ Lesson metadata appears to be correctly updated")
            return True
        else:
            print("✗ Lesson metadata may need updating")
            return False
    else:
        print(f"Lesson metadata file not found: {lesson_metadata_path}")
        return False


if __name__ == "__main__":
    extraction_success = test_video_extraction_fix()
    metadata_success = test_lesson_metadata_update()

    print("\n" + "=" * 70)
    print("FINAL TEST RESULTS:")
    print("=" * 70)
    print(f"Video extraction test: {'PASS' if extraction_success else 'FAIL'}")
    print(f"Metadata update test:  {'PASS' if metadata_success else 'FAIL'}")
    print(f"Overall status:        {'PASS' if extraction_success and metadata_success else 'FAIL'}")