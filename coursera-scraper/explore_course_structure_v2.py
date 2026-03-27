#!/usr/bin/env python3
"""
Explore the full course structure for business-english-intro.
Try to discover all modules and lessons.
"""

import os
import json
import requests
from dotenv import load_dotenv

def explore_course_structure():
    """Explore the complete course structure."""
    print("Exploring Business English Course Structure")
    print("="*50)

    # Load credentials
    load_dotenv()
    cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')

    if not cauth_cookie:
        print("ERROR: COURSERA_CAUTH_COOKIE not found in .env file")
        return False

    # Setup request
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'x-coursera-application': 'ondemand',
        'x-requested-with': 'XMLHttpRequest',
        'authority': 'www.coursera.org'
    }
    cookies = {'CAUTH': cauth_cookie}

    course_id = "46b4tHEkEeWbbw5cIAKQrw"  # business-english-intro

    # Try the modules endpoint that returned 200
    modules_url = f'https://www.coursera.org/api/onDemandCourseModules.v1/course/{course_id}/modules'

    print(f"Trying Course Modules API...")
    print(f"URL: {modules_url}")

    try:
        response = requests.get(modules_url, headers=headers, cookies=cookies)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"Content Length: {len(response.text)}")
        print(f"Raw content preview: {response.text[:200]}")

        if response.status_code == 200:
            if response.text.strip():
                # Try to parse as JSON
                try:
                    data = response.json()
                    print("PARSED AS JSON!")
                    print(f"Keys: {list(data.keys())}")

                    # Save the response
                    with open('course_modules_response.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                    print("Saved to: course_modules_response.json")

                    return data

                except json.JSONDecodeError as e:
                    print(f"JSON parse error: {e}")

            else:
                print("Empty response body")

    except Exception as e:
        print(f"Request error: {e}")

    # Also try to check what lectures we can find by exploring different lecture IDs
    print("\nTrying to discover other lectures...")

    # Known lecture IDs from the working demo
    test_lectures = [
        "sf1NL",  # Video Email Guidelines (we know this works)
        "8fF_q",  # Let me try some common patterns
        "Gql5i",
        "w1yLV",
        "KqJD4",
        "JqP8H"
    ]

    found_lectures = []

    for lecture_id in test_lectures:
        lecture_url = f"https://www.coursera.org/api/onDemandLectureVideos.v1/{course_id}~{lecture_id}?includes=video&fields=onDemandVideos.v1(sources%2Csubtitles%2CsubtitlesVtt%2CsubtitlesTxt%2CsubtitlesAssetTags%2CdubbedSources%2CdubbedSubtitlesVtt%2CaudioDescriptionVideoSources)%2CdisableSkippingForward%2CstartMs%2CendMs"

        try:
            response = requests.get(lecture_url, headers=headers, cookies=cookies)
            if response.status_code == 200:
                data = response.json()
                print(f"Found lecture {lecture_id}!")

                # Get lesson name from response
                if 'linked' in data and 'onDemandVideos.v1' in data['linked']:
                    video_info = data['linked']['onDemandVideos.v1'][0]
                    print(f"  - Lecture ID: {lecture_id}")
                    print(f"  - Video ID: {video_info.get('id', 'N/A')}")

                found_lectures.append({
                    'lecture_id': lecture_id,
                    'data': data
                })
            else:
                print(f"Lecture {lecture_id}: HTTP {response.status_code}")

        except Exception as e:
            print(f"Error checking lecture {lecture_id}: {e}")

    if found_lectures:
        print(f"\nFound {len(found_lectures)} accessible lectures:")
        for lecture in found_lectures:
            print(f"  - {lecture['lecture_id']}")

    return found_lectures

if __name__ == "__main__":
    result = explore_course_structure()