#!/usr/bin/env python3
"""
Enhanced Video URL Extractor - Downloads ALL videos from ALL lessons.
Fixes the bug where only 1 video per lesson was processed.
Each lesson can contain multiple lecture videos!
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

def extract_all_video_urls(course_name="introduction-to-business-english-communication-course"):
    """Extract ALL video URLs for ALL videos in each lesson."""
    print("=" * 80)
    print("ENHANCED VIDEO URL EXTRACTOR")
    print("Fixed: Now extracts ALL videos from each lesson!")
    print(f"Course: {course_name}")
    print("=" * 80)

    # Load credentials
    load_dotenv()
    cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')

    if not cauth_cookie:
        print("ERROR: COURSERA_CAUTH_COOKIE not found in .env file")
        return False

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
    course_id = "46b4tHEkEeWbbw5cIAKQrw"  # Business English course ID

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
    total_videos_found = 0
    total_videos_extracted = 0
    total_lessons_processed = 0

    # Process each existing lesson directory
    for lesson_idx, lesson_dir in enumerate(lesson_dirs):
        lesson_name = lesson_dir.name
        print(f"[{lesson_idx + 1:2d}/{len(lesson_dirs)}] Processing: {lesson_name}")

        # Load lesson metadata to find ALL video assets
        metadata_file = lesson_dir / "lesson_metadata.json"
        if not metadata_file.exists():
            print(f"     ERROR: No metadata file found")
            continue

        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # Find ALL video assets in this lesson
            video_assets = []
            for asset in metadata.get('assets', []):
                if asset.get('file_type') == 'video' and 'name' in asset:
                    video_name = asset['name']
                    if video_name.startswith('video_'):
                        lecture_id = video_name.split('_')[1]
                        video_assets.append({
                            'asset_name': video_name,
                            'lecture_id': lecture_id
                        })

            if not video_assets:
                print(f"     SKIP: No video assets found in metadata")
                continue

            total_videos_found += len(video_assets)
            print(f"     Found {len(video_assets)} video assets: {[v['lecture_id'] for v in video_assets]}")

            # Extract URLs for ALL video assets in this lesson
            all_lesson_urls = []
            videos_extracted = 0

            for video_asset in video_assets:
                lecture_id = video_asset['lecture_id']
                asset_name = video_asset['asset_name']

                try:
                    # Get video data from Coursera API
                    video_url = f"https://www.coursera.org/api/onDemandLectureVideos.v1/{course_id}~{lecture_id}?includes=video&fields=onDemandVideos.v1(sources%2Csubtitles%2CsubtitlesVtt%2CsubtitlesTxt%2CsubtitlesAssetTags%2CdubbedSources%2CdubbedSubtitlesVtt%2CaudioDescriptionVideoSources)%2CdisableSkippingForward%2CstartMs%2CendMs"

                    response = requests.get(video_url, headers=api_headers, cookies=api_cookies)

                    if response.status_code == 200:
                        video_data = response.json()

                        if 'linked' in video_data and 'onDemandVideos.v1' in video_data['linked']:
                            video_info = video_data['linked']['onDemandVideos.v1'][0]

                            # Extract URLs for this specific video asset
                            video_urls = extract_video_urls(video_info, lecture_id, asset_name)
                            all_lesson_urls.extend(video_urls)
                            videos_extracted += 1

                            print(f"       OK {asset_name} ({lecture_id}): {len(video_urls)} URLs")
                        else:
                            print(f"       ERROR {asset_name} ({lecture_id}): No video data in response")
                    else:
                        print(f"       ERROR {asset_name} ({lecture_id}): HTTP {response.status_code}")

                except Exception as e:
                    print(f"       ERROR {asset_name} ({lecture_id}): {e}")

            # Save ALL video URLs to content_urls.txt
            if all_lesson_urls:
                content_urls_file = lesson_dir / "content_urls.txt"
                with open(content_urls_file, 'w', encoding='utf-8') as f:
                    f.write(f"Content URLs for {lesson_name}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Total Videos: {len(video_assets)}\n")
                    f.write(f"Total URLs: {len(all_lesson_urls)}\n\n")

                    for url in all_lesson_urls:
                        f.write(url + "\n")

                total_videos_extracted += videos_extracted
                total_lessons_processed += 1
                print(f"     SUCCESS: Extracted {len(all_lesson_urls)} URLs for {videos_extracted}/{len(video_assets)} videos")
            else:
                print(f"     FAILED: No URLs extracted")

        except Exception as e:
            print(f"     ERROR: {e}")

    print()
    print("=" * 80)
    print("ENHANCED URL EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"Lessons processed: {total_lessons_processed}/{len(lesson_dirs)}")
    print(f"Total videos found: {total_videos_found}")
    print(f"Total videos extracted: {total_videos_extracted}")
    print(f"Course: {course_path}")

    if total_videos_extracted > 0:
        print(f"\nSUCCESS: Extracted URLs for {total_videos_extracted} videos!")
        print("Now you can run the download command to get ALL video files!")

    return total_videos_extracted > 0


def extract_video_urls(video_info, lecture_id, asset_name):
    """Extract all video URLs from a single video asset."""
    urls = []

    # Add section header
    urls.append(f"")
    urls.append(f"# Video Asset: {asset_name} (Lecture ID: {lecture_id})")
    urls.append(f"# " + "=" * 50)

    # Extract video URLs by resolution
    if 'sources' in video_info and 'byResolution' in video_info['sources']:
        for resolution, source_data in video_info['sources']['byResolution'].items():
            if 'mp4VideoUrl' in source_data:
                urls.append(f"{resolution} MP4 ({asset_name}): {source_data['mp4VideoUrl']}")
            if 'webMVideoUrl' in source_data:
                urls.append(f"{resolution} WebM ({asset_name}): {source_data['webMVideoUrl']}")

    # Extract audio URLs
    if 'sources' in video_info and 'audio' in video_info['sources']:
        for audio_data in video_info['sources']['audio']:
            urls.append(f"Audio ({asset_name}): {audio_data['url']}")

    # Subtitles intentionally excluded - user doesn't want them downloaded

    return urls


if __name__ == "__main__":
    success = extract_all_video_urls()
    if not success:
        exit(1)