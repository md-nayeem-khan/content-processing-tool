#!/usr/bin/env python3
"""
Test script to verify the fixes by running a new scraping/downloading process.
"""

import os
import sys
import subprocess
from pathlib import Path

def test_comprehensive_fix():
    """Test the complete process with fixes."""
    print("Testing Complete Video Extraction and Download Process")
    print("=" * 70)

    # Step 1: Test comprehensive scraping with the fix
    print("Step 1: Run comprehensive course scraper with fixed logic...")

    try:
        result = subprocess.run([
            sys.executable, "comprehensive_course_scraper.py"
        ], capture_output=True, text=True, timeout=300)

        print("Scraper output:")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)

    except subprocess.TimeoutExpired:
        print("Scraper timed out after 5 minutes")
    except Exception as e:
        print(f"Error running scraper: {e}")

    # Step 2: Check the lesson metadata for multiple videos
    print("\n" + "=" * 70)
    print("Step 2: Check updated lesson metadata...")

    lesson_metadata_path = Path('courses/introduction-to-business-english-communication-course/module-01-introduction-to-business-english-communication/lesson-01-lesson-1-course-overview-and-assessment/lesson_metadata.json')

    if lesson_metadata_path.exists():
        import json
        with open(lesson_metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        print(f"Lesson: {metadata.get('name', 'Unknown')}")
        print(f"Total assets: {metadata.get('total_assets', 0)}")

        video_assets = [asset for asset in metadata.get('assets', []) if asset.get('file_type') == 'video']
        video_assets_with_urls = [asset for asset in video_assets if asset.get('url')]

        print(f"Video assets found: {len(video_assets)}")
        print(f"Video assets with URLs: {len(video_assets_with_urls)}")

        print("\nVideo assets details:")
        for i, asset in enumerate(video_assets_with_urls, 1):
            name = asset.get('name', 'Unknown')
            url = asset.get('url', 'No URL')[:80] + '...' if asset.get('url', '') else 'No URL'
            print(f"  {i}. {name}")
            print(f"     URL: {url}")

        expected_videos = 3  # DKbsC, 2Zis7, 6AM0l
        success = len(video_assets_with_urls) >= expected_videos

        print(f"\nExpected videos: {expected_videos}")
        print(f"Found videos:    {len(video_assets_with_urls)}")
        print(f"Status: {'PASS' if success else 'FAIL'}")

        return success
    else:
        print(f"Lesson metadata not found: {lesson_metadata_path}")
        return False


def check_current_downloads():
    """Check what's currently downloaded."""
    print("\n" + "=" * 70)
    print("Checking Current Downloaded Files")
    print("=" * 70)

    lesson_dir = Path('courses/introduction-to-business-english-communication-course/module-01-introduction-to-business-english-communication/lesson-01-lesson-1-course-overview-and-assessment')

    if lesson_dir.exists():
        video_files = list(lesson_dir.glob("*.video"))
        print(f"Current .video files: {len(video_files)}")

        for video_file in video_files:
            size_mb = video_file.stat().st_size / 1024 / 1024
            print(f"  - {video_file.name} ({size_mb:.1f} MB)")

        # Look for files with item_id in name
        files_with_itemid = [f for f in video_files if any(item_id in f.name for item_id in ['DKbsC', '2Zis7', '6AM0l'])]
        print(f"\nFiles with item IDs: {len(files_with_itemid)}")

        for file in files_with_itemid:
            print(f"  - {file.name}")

        return len(files_with_itemid)
    else:
        print(f"Lesson directory not found: {lesson_dir}")
        return 0


if __name__ == "__main__":
    # First check current state
    current_downloads = check_current_downloads()

    # Run the comprehensive test
    success = test_comprehensive_fix()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Lesson metadata test: {'PASS' if success else 'FAIL'}")
    print(f"Downloads with item IDs: {current_downloads}")

    if success:
        print("✓ Video extraction logic has been successfully fixed!")
        print("✓ Multiple videos are now properly detected and processed")
    else:
        print("✗ Issues remain with video extraction")
        print("Please check the implementation for any remaining bugs")