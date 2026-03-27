#!/usr/bin/env python3
"""
Quick test script to verify Coursera API access.
Run this to test your authentication and API endpoints.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_coursera_api():
    """Test Coursera API access with your credentials."""

    # Load credentials
    cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')
    csrf_token = os.getenv('COURSERA_CSRF_TOKEN')
    csrf3_token_cookie = os.getenv('COURSERA_CSRF3_TOKEN_COOKIE')

    if not cauth_cookie or not csrf_token:
        print("❌ Missing credentials in .env file")
        print("Please set COURSERA_CAUTH_COOKIE and COURSERA_CSRF_TOKEN")
        return False

    # Setup headers and cookies
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'x-csrf3-token': csrf_token,
        'Origin': 'https://www.coursera.org',
        'Referer': 'https://www.coursera.org/',
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

    # Update headers for video endpoint
    headers.update({
        'accept': '*/*',
        'x-coursera-application': 'ondemand',
        'x-requested-with': 'XMLHttpRequest'
    })
    # Remove CSRF token header as it's not needed for this GET request
    if 'x-csrf3-token' in headers:
        del headers['x-csrf3-token']

    try:
        response = requests.get(test_url, headers=headers, cookies=cookies)
        print(f"📡 Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ API connection successful!")
            print(f"📄 Response preview: {response.text[:200]}...")
            return True
        elif response.status_code == 401:
            print("❌ Authentication failed - check your CAUTH cookie")
        elif response.status_code == 403:
            print("❌ CSRF token invalid - check your x-csrf3-token")
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"Response: {response.text[:200]}...")

        return False

    except Exception as e:
        print(f"❌ Network error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing Coursera API Access...")
    print("=" * 50)
    test_coursera_api()