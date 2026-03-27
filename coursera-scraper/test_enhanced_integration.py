#!/usr/bin/env python3
"""
Test script to verify enhanced downloader integration works correctly.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")

    try:
        from src.api.enhanced_downloader import EnhancedVideoDownloader
        print("[PASS] EnhancedVideoDownloader imported successfully")

        from src.api.auth import CourseraAuth
        print("[PASS] CourseraAuth imported successfully")

        from src.core.file_manager import FileManager
        print("[PASS] FileManager imported successfully")

        from src.utils.logger import LoggerMixin
        print("[PASS] LoggerMixin imported successfully")

        from src.utils.sanitizer import sanitize_sequential_video_name
        print("[PASS] sanitize_sequential_video_name imported successfully")

        return True

    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False

def test_enhanced_downloader_creation():
    """Test that EnhancedVideoDownloader can be created."""
    print("\nTesting EnhancedVideoDownloader creation...")

    try:
        from src.api.enhanced_downloader import EnhancedVideoDownloader
        from src.api.auth import CourseraAuth
        from src.core.file_manager import FileManager
        from src.utils.logger import setup_logger

        # Mock auth and file manager
        auth = CourseraAuth()  # This might fail if no credentials, but that's ok
        file_manager = FileManager("test_output")
        logger = setup_logger()

        # Try to create the downloader
        downloader = EnhancedVideoDownloader(
            auth=auth,
            file_manager=file_manager,
            max_concurrent=2,
            download_subtitles=True,
            subtitle_language='en',
            logger=logger
        )

        print("[PASS] EnhancedVideoDownloader created successfully")
        print(f"[PASS] Subtitle support enabled: {downloader.download_subtitles}")
        print(f"[PASS] Subtitle language: {downloader.subtitle_language}")
        print(f"[PASS] Max concurrent: {downloader.max_concurrent}")

        return True

    except Exception as e:
        print(f"[FAIL] Failed to create EnhancedVideoDownloader: {e}")
        return False

def test_main_cli_import():
    """Test that the main CLI module can be imported with our changes."""
    print("\nTesting main CLI module...")

    try:
        from src.main import cli
        print("[PASS] Main CLI module imported successfully")
        return True

    except Exception as e:
        print(f"[FAIL] Failed to import main CLI: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("ENHANCED DOWNLOADER INTEGRATION TEST")
    print("=" * 60)

    tests = [
        test_imports,
        test_enhanced_downloader_creation,
        test_main_cli_import
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
        print("SUCCESS: ALL TESTS PASSED! Enhanced downloader integration is ready.")
        print("\nYou can now run:")
        print("  python -m src.main download <course-name> --subtitles")
        print("  python -m src.main download <course-name> --no-subtitles  # videos only")
    else:
        print("ERROR: Some tests failed. Check the errors above.")
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)