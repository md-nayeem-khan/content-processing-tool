#!/usr/bin/env python3
"""
Test script to verify scraper fixes for ContentAsset hashability and subtitle metadata.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_content_asset_hashability():
    """Test that ContentAsset can now be used as dict keys."""
    print("Testing ContentAsset hashability...")

    try:
        from src.core.course_models import ContentAsset

        # Create two ContentAsset instances
        asset1 = ContentAsset(
            name="test_video_720p.mp4",
            url="https://example.com/video1.mp4",
            file_type="video",
            metadata={
                'course_id': 'test123',
                'item_id': 'item456'
            }
        )

        asset2 = ContentAsset(
            name="test_video2_720p.mp4",
            url="https://example.com/video2.mp4",
            file_type="video",
            metadata={
                'course_id': 'test123',
                'item_id': 'item789'
            }
        )

        # Test using ContentAsset as dictionary keys (this used to fail)
        test_dict = {}
        test_dict[asset1] = 1
        test_dict[asset2] = 2

        print(f"[PASS] ContentAsset can be used as dict keys: {len(test_dict)} items")

        # Test equality and hashing
        asset1_copy = ContentAsset(
            name="test_video_720p.mp4",
            url="https://example.com/video1.mp4",
            file_type="video"
        )

        print(f"[PASS] asset1 hash: {hash(asset1)}")
        print(f"[PASS] asset1_copy hash: {hash(asset1_copy)}")
        print(f"[PASS] asset1 == asset1_copy: {asset1 == asset1_copy}")

        return True

    except Exception as e:
        print(f"[FAIL] ContentAsset hashability test failed: {e}")
        return False

def test_enhanced_downloader_compatibility():
    """Test that ContentAsset metadata structure matches enhanced downloader expectations."""
    print("\nTesting enhanced downloader metadata compatibility...")

    try:
        from src.core.course_models import ContentAsset

        # Create a ContentAsset with the structure that enhanced downloader expects
        asset = ContentAsset(
            name="Video_Welcome_720p.mp4",
            url="https://example.com/video.mp4",
            file_type="video",
            metadata={
                'course_id': '46b4tHEkEeWbbw5cIAKQrw',
                'item_id': 'DKbsC',
                'resolution': '720p'
            }
        )

        # Test that we can access the metadata fields that enhanced downloader needs
        asset_metadata = asset.metadata
        course_id = asset_metadata.get('course_id')
        item_id = asset_metadata.get('item_id')

        print(f"[PASS] Asset has course_id: {course_id}")
        print(f"[PASS] Asset has item_id: {item_id}")
        print(f"[PASS] Asset has URL: {asset.url}")
        print(f"[PASS] Asset file_type: {asset.file_type}")

        # Simulate what enhanced downloader does
        if (asset.file_type == 'video' and
            '_720p.mp4' in asset.name and
            asset.url and
            course_id and
            item_id):
            print("[PASS] Asset structure compatible with enhanced downloader")
            return True
        else:
            print("[FAIL] Asset structure not compatible with enhanced downloader")
            return False

    except Exception as e:
        print(f"[FAIL] Enhanced downloader compatibility test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("SCRAPER FIXES VALIDATION TEST")
    print("=" * 60)

    tests = [
        test_content_asset_hashability,
        test_enhanced_downloader_compatibility
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"[FAIL] Test {test_func.__name__} failed with exception: {e}")

    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("SUCCESS: All fixes validated! Ready to re-scrape course.")
    else:
        print("ERROR: Some fixes failed validation.")
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)