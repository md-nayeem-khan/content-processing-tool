#!/usr/bin/env python3
"""
Test all found lecture IDs systematically.
"""

import os
import re
import json
import requests
from dotenv import load_dotenv

def test_all_lecture_ids():
    """Test all potential lecture IDs found from webpage."""
    print("Testing All Potential Lecture IDs")
    print("="*50)

    # Load credentials
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

    # Read the webpage content
    try:
        with open('course_webpage.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print("course_webpage.html not found. Run scrape_course_webpage.py first.")
        return []

    # Extract all potential lecture IDs
    lecture_patterns = [
        r'lectureId["\']:\s*["\']([a-zA-Z0-9_]+)["\']',  # lectureId: "abc123"
        r'lecture["\']:\s*["\']([a-zA-Z0-9_]+)["\']',     # lecture: "abc123"
        r'itemId["\']:\s*["\']([a-zA-Z0-9_]+)["\']',      # itemId: "abc123"
        r'"id":\s*"([a-zA-Z0-9_]{4,8})"',                # "id": "abc123" (4-8 chars)
        r'~([a-zA-Z0-9_]{5,8})"',                        # ~abc123" (5-8 chars)
    ]

    found_ids = set()

    for pattern in lecture_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            # Filter for reasonable lecture ID length and format
            if 4 <= len(match) <= 8 and match.isalnum():
                found_ids.add(match)

    course_id = "46b4tHEkEeWbbw5cIAKQrw"
    valid_lectures = []

    print(f"Testing {len(found_ids)} potential lecture IDs...")

    for i, lecture_id in enumerate(sorted(found_ids), 1):
        lecture_url = f"https://www.coursera.org/api/onDemandLectureVideos.v1/{course_id}~{lecture_id}?includes=video&fields=onDemandVideos.v1(sources%2Csubtitles%2CsubtitlesVtt%2CsubtitlesTxt%2CsubtitlesAssetTags%2CdubbedSources%2CdubbedSubtitlesVtt%2CaudioDescriptionVideoSources)%2CdisableSkippingForward%2CstartMs%2CendMs"

        print(f"[{i:3d}/{len(found_ids)}] Testing {lecture_id}...", end=' ')

        try:
            response = requests.get(lecture_url, headers=headers, cookies=cookies)
            if response.status_code == 200:
                data = response.json()
                if 'linked' in data and 'onDemandVideos.v1' in data['linked']:
                    video_info = data['linked']['onDemandVideos.v1'][0]

                    valid_lectures.append({
                        'lecture_id': lecture_id,
                        'video_id': video_info.get('id', 'N/A'),
                        'data': data
                    })

                    print(f"SUCCESS! Video ID: {video_info.get('id')}")
                else:
                    print("ERROR: No video data")
            elif response.status_code == 404:
                print("ERROR: Not found")
            else:
                print(f"ERROR: HTTP {response.status_code}")

        except Exception as e:
            print(f"ERROR: {e}")

    # Save all valid lecture data
    if valid_lectures:
        with open('valid_lectures.json', 'w', encoding='utf-8') as f:
            json.dump(valid_lectures, f, indent=2)
        print(f"\nSaved {len(valid_lectures)} valid lectures to: valid_lectures.json")

    print(f"\nFOUND {len(valid_lectures)} VALID LECTURES:")
    for i, lecture in enumerate(valid_lectures, 1):
        print(f"  {i:2d}. Lecture ID: {lecture['lecture_id']} | Video ID: {lecture['video_id']}")

    return valid_lectures

if __name__ == "__main__":
    test_all_lecture_ids()