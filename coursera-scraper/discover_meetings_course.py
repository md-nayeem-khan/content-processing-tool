#!/usr/bin/env python3
"""
Discover the course structure for business-english-meetings.
"""

import os
import re
import json
import requests
from dotenv import load_dotenv

def discover_meetings_course():
    """Discover the business-english-meetings course structure."""
    print("Discovering Business English Meetings Course")
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

    # Try different possible course URLs
    possible_urls = [
        "https://www.coursera.org/learn/business-english-meetings",
        "https://www.coursera.org/learn/english-meetings",
        "https://www.coursera.org/learn/business-meetings"
    ]

    course_id = None
    found_course_url = None

    for course_url in possible_urls:
        try:
            print(f"Trying: {course_url}")
            response = requests.get(course_url, headers=headers, cookies=cookies)

            if response.status_code == 200:
                print(f"SUCCESS: Found course at {course_url}")
                found_course_url = course_url

                # Extract course ID from HTML
                html_content = response.text

                # Look for course ID patterns
                course_id_patterns = [
                    r'course["\']:\s*["\']([a-zA-Z0-9_~-]+)["\']',
                    r'courseId["\']:\s*["\']([a-zA-Z0-9_~-]+)["\']',
                    r'"id":\s*"([a-zA-Z0-9_~-]{20,})"',
                ]

                for pattern in course_id_patterns:
                    matches = re.findall(pattern, html_content)
                    for match in matches:
                        if len(match) > 15:  # Course IDs are typically long
                            course_id = match
                            print(f"Found potential course ID: {course_id}")
                            break
                    if course_id:
                        break

                # Save HTML for analysis
                with open('meetings_course_webpage.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print("Saved HTML to: meetings_course_webpage.html")

                break

            elif response.status_code == 404:
                print(f"  - Course not found at this URL")
            else:
                print(f"  - HTTP {response.status_code}")

        except Exception as e:
            print(f"  - Error: {e}")

    if not found_course_url:
        print("ERROR: Could not find the business-english-meetings course")
        return False

    if not course_id:
        print("WARNING: Could not extract course ID from webpage")
        return False

    print(f"\nFound course ID: {course_id}")

    # Now try to find lecture IDs by extracting them from the HTML
    print("\nExtracting lecture IDs from webpage...")

    with open('meetings_course_webpage.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Extract potential lecture IDs
    lecture_patterns = [
        r'lectureId["\']:\s*["\']([a-zA-Z0-9_]+)["\']',
        r'itemId["\']:\s*["\']([a-zA-Z0-9_]+)["\']',
        r'"id":\s*"([a-zA-Z0-9_]{4,8})"',
        r'~([a-zA-Z0-9_]{5,8})"',
    ]

    found_ids = set()
    for pattern in lecture_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            if 4 <= len(match) <= 8 and match.isalnum():
                found_ids.add(match)

    print(f"Found {len(found_ids)} potential lecture IDs")

    # Test these lecture IDs with the video API
    print("Testing lecture IDs with video API...")

    api_headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'x-coursera-application': 'ondemand',
        'x-requested-with': 'XMLHttpRequest',
        'authority': 'www.coursera.org'
    }
    api_cookies = {'CAUTH': cauth_cookie}

    valid_lectures = []

    for i, lecture_id in enumerate(sorted(found_ids), 1):
        lecture_url = f"https://www.coursera.org/api/onDemandLectureVideos.v1/{course_id}~{lecture_id}?includes=video&fields=onDemandVideos.v1(sources%2Csubtitles%2CsubtitlesVtt%2CsubtitlesTxt%2CsubtitlesAssetTags%2CdubbedSources%2CdubbedSubtitlesVtt%2CaudioDescriptionVideoSources)%2CdisableSkippingForward%2CstartMs%2CendMs"

        print(f"[{i:3d}/{len(found_ids)}] Testing {lecture_id}...", end=' ')

        try:
            response = requests.get(lecture_url, headers=api_headers, cookies=api_cookies)
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

    # Save results
    if valid_lectures:
        with open('meetings_valid_lectures.json', 'w', encoding='utf-8') as f:
            json.dump(valid_lectures, f, indent=2)
        print(f"\nSaved {len(valid_lectures)} valid lectures to: meetings_valid_lectures.json")

        # Save course configuration
        course_config = {
            'course_id': course_id,
            'course_name': 'Business English: Meetings',
            'course_url': found_course_url,
            'valid_lectures': valid_lectures
        }

        with open('meetings_course_config.json', 'w', encoding='utf-8') as f:
            json.dump(course_config, f, indent=2)

        print(f"Saved course configuration to: meetings_course_config.json")

    print(f"\nFOUND {len(valid_lectures)} VALID LECTURES:")
    for i, lecture in enumerate(valid_lectures, 1):
        print(f"  {i:2d}. Lecture ID: {lecture['lecture_id']} | Video ID: {lecture['video_id']}")

    return len(valid_lectures) > 0

if __name__ == "__main__":
    success = discover_meetings_course()
    if success:
        print("\nSuccess! Found valid lectures for business-english-meetings")
    else:
        print("\nFailed to discover course structure")