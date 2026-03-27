#!/usr/bin/env python3
"""
Comprehensive test for the Coursera API integration.
Tests the real video content API we discovered.
"""

import os
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from api.auth import CourseraAuth
from api.coursera_client import CourseraClient
from config.settings import ConfigManager
from utils.logger import setup_logger

def test_video_api():
    """Test the real video content API."""
    print("🎬 Testing Real Video Content API")
    print("=" * 50)

    try:
        # Setup logging
        logger = setup_logger("test_api", log_level="DEBUG")

        # Load configuration
        config = ConfigManager()

        # Setup authentication
        auth = CourseraAuth()
        print(f"✅ Authentication initialized: {auth}")

        # Create API client
        client = CourseraClient.from_config_file("config/api_endpoints.json", auth)
        print(f"✅ API client initialized")

        # Test connection
        print("\n🔌 Testing API connection...")
        if client.test_connection():
            print("✅ API connection successful")
        else:
            print("❌ API connection failed")
            return False

        # Test real video endpoint
        print("\n🎥 Testing video content API...")
        course_id = "46b4tHEkEeWbbw5cIAKQrw"  # business-english-intro
        lecture_id = "sf1NL"  # Video email guidelines

        try:
            video_data = client.get_lecture_video(course_id, lecture_id)

            print(f"✅ Video API call successful!")
            print(f"📊 Response keys: {list(video_data.keys())}")

            # Check video sources
            if 'linked' in video_data and 'onDemandVideos.v1' in video_data['linked']:
                video_info = video_data['linked']['onDemandVideos.v1'][0]

                print(f"🎬 Video ID: {video_info.get('id', 'N/A')}")

                # Check video resolutions
                if 'sources' in video_info and 'byResolution' in video_info['sources']:
                    resolutions = list(video_info['sources']['byResolution'].keys())
                    print(f"📺 Available resolutions: {resolutions}")

                    # Check a specific resolution
                    if '720p' in video_info['sources']['byResolution']:
                        video_720p = video_info['sources']['byResolution']['720p']
                        print(f"🎞️  720p MP4 URL available: {'mp4VideoUrl' in video_720p}")
                        print(f"🎞️  720p WebM URL available: {'webMVideoUrl' in video_720p}")

                # Check subtitles
                if 'subtitles' in video_info:
                    subtitle_languages = list(video_info['subtitles'].keys())
                    print(f"📝 Available subtitle languages: {len(subtitle_languages)} ({subtitle_languages[:5]}...)")

                # Check audio
                if 'sources' in video_info and 'audio' in video_info['sources']:
                    audio_formats = [audio['audioFormat'] for audio in video_info['sources']['audio']]
                    print(f"🔊 Available audio formats: {audio_formats}")

                print("✅ Video content structure validation passed!")
                return True
            else:
                print("❌ Unexpected video response structure")
                return False

        except Exception as e:
            print(f"❌ Video API call failed: {e}")
            return False

    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return False

def test_course_search():
    """Test course search functionality."""
    print("\n🔍 Testing Course Search API")
    print("=" * 40)

    try:
        auth = CourseraAuth()
        client = CourseraClient.from_config_file("config/api_endpoints.json", auth)

        search_result = client.get('search_courses', search_term='business')

        if 'elements' in search_result:
            courses = search_result['elements']
            print(f"✅ Found {len(courses)} courses matching 'business'")

            if courses:
                first_course = courses[0]
                print(f"📚 First course: {first_course.get('name', 'N/A')}")
                print(f"🆔 Course ID: {first_course.get('id', 'N/A')}")
                print(f"🏫 University: {first_course.get('partnerIds', 'N/A')}")

            return True
        else:
            print("❌ Unexpected search response format")
            return False

    except Exception as e:
        print(f"❌ Course search failed: {e}")
        return False

def main():
    """Run comprehensive API tests."""
    print("🚀 Coursera API Integration Test")
    print("=" * 60)

    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("📝 Copy .env.test to .env and update with your credentials:")
        print("   cp .env.test .env")
        print("   # Edit .env with your actual CAUTH cookie and CSRF token")
        return False

    # Run tests
    tests = [
        ("Video Content API", test_video_api),
        ("Course Search API", test_course_search)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Your Coursera scraper is ready!")
        print("")
        print("🚀 Next steps:")
        print("   python -m src.main test")
        print("   python -m src.main scrape business-english-intro")
        return True
    else:
        print("⚠️  Some tests failed. Please check your configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)