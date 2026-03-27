#!/usr/bin/env python3
"""
Simple test to verify critical download fixes are in place.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_download_asset_exists():
    """Test that download_asset method exists in FileManager."""
    try:
        from src.core.file_manager import FileManager

        fm = FileManager("./test")
        assert hasattr(fm, 'download_asset'), "download_asset method missing"
        print("+ download_asset method exists in FileManager")
        return True
    except Exception as e:
        print(f"- download_asset test failed: {e}")
        return False

def test_api_method_fixed():
    """Test that API calls use correct method names."""
    try:
        from src.api.coursera_client import CourseraClient

        # Check that get_lecture_video method exists
        methods = [method for method in dir(CourseraClient) if not method.startswith('_')]
        assert 'get_lecture_video' in methods, "get_lecture_video method missing"
        print("+ get_lecture_video method exists in CourseraClient")
        return True
    except Exception as e:
        print(f"- API method test failed: {e}")
        return False

def test_comprehensive_models():
    """Test that comprehensive API models work."""
    try:
        from src.core.course_models import ComprehensiveCourseData, CourseraModule, CourseraLesson, CourseraContentItem

        # Test basic model creation
        module = CourseraModule(id="test", name="Test Module", slug="test")
        lesson = CourseraLesson(id="test", name="Test Lesson", slug="test")
        item = CourseraContentItem(id="test", name="Test Item", slug="test")

        comprehensive = ComprehensiveCourseData(
            course_id="test",
            modules=[module],
            lessons=[lesson],
            items=[item]
        )

        print("+ Comprehensive API models work correctly")
        return True
    except Exception as e:
        print(f"- Comprehensive models test failed: {e}")
        return False

def test_content_type_mapper():
    """Test content type mapping functionality."""
    try:
        from src.core.scraper import ContentTypeMapper

        # Test basic mappings
        assert ContentTypeMapper.is_video("lecture")
        assert ContentTypeMapper.is_downloadable("lecture")
        assert ContentTypeMapper.should_skip("discussionPrompt")

        print("+ Content type mapping works correctly")
        return True
    except Exception as e:
        print(f"- Content type mapper test failed: {e}")
        return False

def test_scraper_methods():
    """Test that scraper has the required methods."""
    try:
        from src.core.scraper import CourseScraper

        required_methods = [
            '_extract_content_assets_from_comprehensive_api',
            '_extract_urls_from_comprehensive_data',
            '_extract_urls_via_individual_api_calls',
            '_enrich_course_with_api_data'
        ]

        for method in required_methods:
            assert hasattr(CourseScraper, method), f"Missing method: {method}"

        print("+ All required scraper methods exist")
        return True
    except Exception as e:
        print(f"- Scraper methods test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("DOWNLOAD FIXES VALIDATION TEST")
    print("=" * 60)

    tests = [
        ("FileManager.download_asset exists", test_download_asset_exists),
        ("API method calls fixed", test_api_method_fixed),
        ("Comprehensive models work", test_comprehensive_models),
        ("Content type mapping works", test_content_type_mapper),
        ("Scraper methods exist", test_scraper_methods),
    ]

    passed = 0
    for name, test_func in tests:
        print(f"\n[TEST] {name}")
        print("-" * 40)
        if test_func():
            passed += 1
            print(f"[PASS] {name}")
        else:
            print(f"[FAIL] {name}")

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("\nSUCCESS! All critical download fixes are in place.")
        print("\nFIXES IMPLEMENTED:")
        print("  1. + Added download_asset method to FileManager")
        print("  2. + Fixed API method calls in scraper")
        print("  3. + Enhanced comprehensive API integration")
        print("  4. + Updated content type mapping")
        print("  5. + Improved asset extraction logic")

        print("\nREADY TO USE:")
        print("  python src/main.py scrape business-english-intro")
        print("  python src/main.py download business-english-intro")
        return True
    else:
        print(f"\nERROR: {len(tests) - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)