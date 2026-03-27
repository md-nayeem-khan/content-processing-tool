#!/usr/bin/env python3
"""
Simple test script to verify Coursera API access without Unicode characters.
"""

import os
import requests
from dotenv import load_dotenv

def test_coursera_api():
    """Test Coursera API access with your credentials."""

    # Load environment variables
    load_dotenv()

    # Load credentials
    cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')
    csrf_token = os.getenv('COURSERA_CSRF_TOKEN')
    csrf3_token_cookie = os.getenv('COURSERA_CSRF3_TOKEN_COOKIE')

    if not cauth_cookie:
        print("ERROR: Missing credentials in .env file")
        print("Please set COURSERA_CAUTH_COOKIE in .env")
        return False

    print("Testing Coursera API Access...")
    print("="*50)

    # Setup headers and cookies
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'x-coursera-application': 'ondemand',
        'x-requested-with': 'XMLHttpRequest',
        'authority': 'www.coursera.org'
    }

    cookies = {
        'CAUTH': cauth_cookie,
    }

    if csrf3_token_cookie:
        cookies['CSRF3-Token'] = csrf3_token_cookie

    # Test with the actual video API endpoint from your course
    course_id = "46b4tHEkEeWbbw5cIAKQrw"  # business-english-intro course ID
    lecture_id = "sf1NL"  # Video email guidelines lecture
    test_url = f"https://www.coursera.org/api/onDemandLectureVideos.v1/{course_id}~{lecture_id}?includes=video&fields=onDemandVideos.v1(sources%2Csubtitles%2CsubtitlesVtt%2CsubtitlesTxt%2CsubtitlesAssetTags%2CdubbedSources%2CdubbedSubtitlesVtt%2CaudioDescriptionVideoSources)%2CdisableSkippingForward%2CstartMs%2CendMs"

    try:
        print("Making API request...")
        response = requests.get(test_url, headers=headers, cookies=cookies)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("SUCCESS: API connection successful!")

            # Parse response
            try:
                data = response.json()
                print("Response structure:")
                print(f"  - Main keys: {list(data.keys())}")

                if 'linked' in data and 'onDemandVideos.v1' in data['linked']:
                    video_info = data['linked']['onDemandVideos.v1'][0]
                    print(f"  - Video ID: {video_info.get('id', 'N/A')}")

                    # Check video resolutions
                    if 'sources' in video_info and 'byResolution' in video_info['sources']:
                        resolutions = list(video_info['sources']['byResolution'].keys())
                        print(f"  - Available resolutions: {resolutions}")

                    # Check subtitles
                    if 'subtitles' in video_info:
                        subtitle_count = len(video_info['subtitles'])
                        print(f"  - Available subtitle languages: {subtitle_count}")

                print("SUCCESS: Video content structure validation passed!")
                return True

            except Exception as e:
                print(f"WARNING: Could not parse JSON response: {e}")
                print(f"Raw response: {response.text[:200]}...")
                return False

        elif response.status_code == 401:
            print("ERROR: Authentication failed - check your CAUTH cookie")
        elif response.status_code == 403:
            print("ERROR: Access forbidden - check permissions")
        elif response.status_code == 404:
            print("ERROR: Resource not found - check course/lecture IDs")
        else:
            print(f"ERROR: API call failed with status {response.status_code}")
            print(f"Response: {response.text[:200]}...")

        return False

    except Exception as e:
        print(f"ERROR: Network error: {e}")
        return False

if __name__ == "__main__":
    success = test_coursera_api()
    if success:
        print("\nAll tests PASSED! Ready to run the scraper.")
    else:
        print("\nTests FAILED. Please check your configuration.")