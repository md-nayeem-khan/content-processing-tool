#!/usr/bin/env python3
"""
Try to get course structure by accessing the course webpage and extracting lecture IDs.
"""

import os
import re
import json
import requests
from dotenv import load_dotenv

def fetch_course_webpage():
    """Fetch the course webpage to extract lecture IDs."""
    print("Fetching Business English Course Webpage")
    print("="*50)

    # Load credentials
    load_dotenv()
    cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')

    if not cauth_cookie:
        print("ERROR: COURSERA_CAUTH_COOKIE not found in .env file")
        return False

    # Setup request to get the course webpage
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    cookies = {'CAUTH': cauth_cookie}

    course_url = "https://www.coursera.org/learn/business-english-intro"

    try:
        print(f"Fetching: {course_url}")
        response = requests.get(course_url, headers=headers, cookies=cookies)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            html_content = response.text
            print(f"Page size: {len(html_content)} characters")

            # Save the HTML for analysis
            with open('course_webpage.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("Saved HTML to: course_webpage.html")

            # Extract lecture IDs using regex patterns
            lecture_patterns = [
                r'lectureId["\']:\s*["\']([a-zA-Z0-9_]+)["\']',  # lectureId: "abc123"
                r'lecture["\']:\s*["\']([a-zA-Z0-9_]+)["\']',     # lecture: "abc123"
                r'itemId["\']:\s*["\']([a-zA-Z0-9_]+)["\']',      # itemId: "abc123"
                r'"id":\s*"([a-zA-Z0-9_]{5,})"',                 # "id": "abc123"
                r'~([a-zA-Z0-9_]{5,})"',                         # ~abc123"
            ]

            found_ids = set()

            for pattern in lecture_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    if len(match) >= 4:  # Filter for reasonable length IDs
                        found_ids.add(match)

            print(f"\nPotential lecture IDs found: {len(found_ids)}")

            # Sort and display found IDs
            sorted_ids = sorted(list(found_ids))
            for i, lecture_id in enumerate(sorted_ids[:20], 1):
                print(f"  {i:2d}. {lecture_id}")

            if len(sorted_ids) > 20:
                print(f"  ... and {len(sorted_ids) - 20} more")

            # Now test these IDs to see which ones work
            print(f"\nTesting lecture IDs...")
            return test_lecture_ids(sorted_ids[:10])  # Test first 10

        else:
            print(f"Failed to fetch course page: {response.status_code}")
            return False

    except Exception as e:
        print(f"Error fetching course page: {e}")
        return False


def test_lecture_ids(lecture_ids):
    """Test a list of lecture IDs to see which ones are valid."""
    load_dotenv()
    cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')

    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'x-coursera-application': 'ondemand',
        'x-requested-with': 'XMLHttpRequest',
        'authority': 'www.coursera.org'
    }
    cookies = {'CAUTH': cauth_cookie}

    course_id = "46b4tHEkEeWbbw5cIAKQrw"
    valid_lectures = []

    for lecture_id in lecture_ids:
        if len(lecture_id) < 4:  # Skip very short IDs
            continue

        lecture_url = f"https://www.coursera.org/api/onDemandLectureVideos.v1/{course_id}~{lecture_id}?includes=video&fields=onDemandVideos.v1(sources%2Csubtitles%2CsubtitlesVtt%2CsubtitlesTxt%2CsubtitlesAssetTags%2CdubbedSources%2CdubbedSubtitlesVtt%2CaudioDescriptionVideoSources)%2CdisableSkippingForward%2CstartMs%2CendMs"

        try:
            response = requests.get(lecture_url, headers=headers, cookies=cookies)
            if response.status_code == 200:
                data = response.json()
                if 'linked' in data and 'onDemandVideos.v1' in data['linked']:
                    video_info = data['linked']['onDemandVideos.v1'][0]

                    # Try to extract lesson name if available
                    lesson_name = "Unknown Lesson"

                    valid_lectures.append({
                        'lecture_id': lecture_id,
                        'lesson_name': lesson_name,
                        'video_id': video_info.get('id', 'N/A'),
                        'data': data
                    })

                    print(f"✓ VALID: {lecture_id} - Video ID: {video_info.get('id')}")

        except Exception as e:
            # Silently skip failed ones
            pass

    return valid_lectures

if __name__ == "__main__":
    valid_lectures = fetch_course_webpage()
    if valid_lectures:
        print(f"\nFOUND {len(valid_lectures)} VALID LECTURES:")
        for i, lecture in enumerate(valid_lectures, 1):
            print(f"  {i}. {lecture['lecture_id']} - {lecture['lesson_name']}")
    else:
        print("\nNo valid lectures found.")