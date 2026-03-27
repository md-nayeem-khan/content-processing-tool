#!/usr/bin/env python3
"""
Extract video URLs for the existing course structure.
This will create content_urls.txt files that the downloader needs.
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

def extract_video_urls_for_course(course_name="introduction-to-business-english-communication-course"):
    """Extract video URLs for existing course structure."""
    print("=" * 80)
    print("VIDEO URL EXTRACTOR")
    print(f"Course: {course_name}")
    print("=" * 80)

    # Load credentials
    load_dotenv()
    cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')

    if not cauth_cookie:
        print("ERROR: COURSERA_CAUTH_COOKIE not found in .env file")
        return False

    # Load lecture discovery data
    discovery_file = "valid_lectures.json"
    if not Path(discovery_file).exists():
        print(f"ERROR: Discovery file not found: {discovery_file}")
        return False

    print(f"Loading lecture data from: {discovery_file}")
    with open(discovery_file, 'r', encoding='utf-8') as f:
        all_lectures = json.load(f)

    print(f"Found {len(all_lectures)} lectures in discovery data")

    # Check if course directory exists
    course_path = Path("courses") / course_name
    if not course_path.exists():
        print(f"ERROR: Course directory not found: {course_path}")
        return False

    # Setup API request headers
    api_headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-coursera-application': 'ondemand',
        'x-requested-with': 'XMLHttpRequest',
        'authority': 'www.coursera.org'
    }
    api_cookies = {'CAUTH': cauth_cookie}

    # Find all existing lesson directories
    lesson_dirs = []
    for module_dir in course_path.glob("module-*"):
        if module_dir.is_dir():
            for lesson_dir in module_dir.glob("lesson-*"):
                if lesson_dir.is_dir():
                    lesson_dirs.append(lesson_dir)

    print(f"Found {len(lesson_dirs)} lesson directories to process")
    print()

    # Statistics
    success_count = 0
    failed_count = 0

    # Process each existing lesson directory
    for lesson_idx, lesson_dir in enumerate(lesson_dirs):
        lesson_name = lesson_dir.name
        print(f"[{lesson_idx + 1:2d}/{len(lesson_dirs)}] Processing: {lesson_name}")

        # Check if content_urls.txt already exists
        content_urls_file = lesson_dir / "content_urls.txt"
        if content_urls_file.exists():
            print(f"     SKIP: URLs already extracted")
            continue

        # Try to extract lecture ID from lesson metadata
        metadata_file = lesson_dir / "lesson_metadata.json"
        lecture_id = None

        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

                # Try to find video assets and extract lecture ID
                for asset in metadata.get('assets', []):
                    if asset.get('file_type') == 'video' and 'name' in asset:
                        # Extract ID from video asset name like 'video_DKbsC'
                        video_name = asset['name']
                        if video_name.startswith('video_'):
                            lecture_id = video_name.split('_')[1]
                            break
            except:
                pass

        if not lecture_id:
            print(f"     ERROR: Could not extract lecture ID from metadata")
            failed_count += 1
            continue

        try:
            # Use the course ID from discovery data
            course_id = "46b4tHEkEeWbbw5cIAKQrw"  # Business English course ID

            # Get video data from Coursera API
            video_url = f"https://www.coursera.org/api/onDemandLectureVideos.v1/{course_id}~{lecture_id}?includes=video&fields=onDemandVideos.v1(sources%2Csubtitles%2CsubtitlesVtt%2CsubtitlesTxt%2CsubtitlesAssetTags%2CdubbedSources%2CdubbedSubtitlesVtt%2CaudioDescriptionVideoSources)%2CdisableSkippingForward%2CstartMs%2CendMs"

            response = requests.get(video_url, headers=api_headers, cookies=api_cookies)

            if response.status_code == 200:
                video_data = response.json()

                if 'linked' in video_data and 'onDemandVideos.v1' in video_data['linked']:
                    video_info = video_data['linked']['onDemandVideos.v1'][0]

                    # Extract video URLs
                    urls_extracted = extract_and_save_urls(video_info, lesson_dir, lecture_id)

                    print(f"     SUCCESS: Extracted {urls_extracted} URLs")
                    success_count += 1
                else:
                    print(f"     ERROR: No video data in response")
                    failed_count += 1
            else:
                print(f"     ERROR: HTTP {response.status_code}")
                failed_count += 1

        except Exception as e:
            print(f"     ERROR: {e}")
            failed_count += 1

    print()
    print("=" * 80)
    print("URL EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"Processed: {len(lesson_dirs)} lessons")
    print(f"Success: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"Course: {course_path}")

    if success_count > 0:
        print("\nNow you can run the download command to get the actual video files!")

    return success_count > 0


def extract_and_save_urls(video_info, lesson_dir, lecture_id):
    """Extract video URLs and save to content_urls.txt"""
    all_urls = []

    # Extract video URLs by resolution
    if 'sources' in video_info and 'byResolution' in video_info['sources']:
        for resolution, source_data in video_info['sources']['byResolution'].items():
            if 'mp4VideoUrl' in source_data:
                all_urls.append(f"{resolution} MP4: {source_data['mp4VideoUrl']}")
            if 'webMVideoUrl' in source_data:
                all_urls.append(f"{resolution} WebM: {source_data['webMVideoUrl']}")

    # Extract audio URLs
    if 'sources' in video_info and 'audio' in video_info['sources']:
        for audio_data in video_info['sources']['audio']:
            all_urls.append(f"Audio: {audio_data['url']}")

    # Extract subtitle URLs
    if 'subtitles' in video_info:
        for lang, url in video_info['subtitles'].items():
            all_urls.append(f"Subtitles {lang}: {url}")

    # Save all URLs to content_urls.txt
    with open(lesson_dir / "content_urls.txt", 'w', encoding='utf-8') as f:
        f.write(f"Content URLs for Lecture {lecture_id}\n")
        f.write("=" * 40 + "\n\n")
        for url in all_urls:
            f.write(url + "\n")

    return len(all_urls)


if __name__ == "__main__":
    success = extract_video_urls_for_course()
    if not success:
        exit(1)