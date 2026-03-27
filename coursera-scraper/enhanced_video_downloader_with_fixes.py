#!/usr/bin/env python3
"""
Enhanced Video Downloader with Sequential Numbering and Extension Fixes

This script downloads videos from the URLs extracted by comprehensive_course_scraper.py
and applies the fixes for:
1. Sequential numbering (001_, 002_, etc.)
2. Proper .mp4 extension (not .mp4.video)
"""

import os
import json
import requests
import time
from pathlib import Path
from dotenv import load_dotenv
import re


def extract_video_name_from_url_content(content_urls_file):
    """Extract video names and create proper sequential naming."""
    try:
        with open(content_urls_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract 720p MP4 URLs with better parsing
        video_info = []
        lines = content.split('\n')

        for line in lines:
            # Look for 720p MP4 URLs
            if '720p MP4:' in line and 'cloudfront.net' in line:
                # Extract URL
                url_start = line.find('https://')
                if url_start != -1:
                    url = line[url_start:].strip()
                    video_info.append({
                        'resolution': '720p',
                        'format': 'mp4',
                        'url': url
                    })

        return video_info

    except Exception as e:
        print(f"Error parsing content URLs: {e}")
        return []


def create_sequential_video_name(video_index, lesson_name, lesson_metadata=None):
    """Create properly numbered video name based on sequence."""
    try:
        # Extract meaningful name from lesson name or metadata
        if lesson_metadata and 'lecture_id' in lesson_metadata:
            base_name = f"Video_{lesson_metadata['lecture_id']}"
        else:
            # Clean up lesson name
            clean_name = lesson_name.replace('lesson-', '').replace('-', '_').title()
            base_name = f"Video_{clean_name}"

        # Add sequential number prefix
        sequential_name = f"{video_index:03d}_{base_name}_720p.mp4"

        return sequential_name

    except Exception as e:
        print(f"Error creating sequential name: {e}")
        return f"{video_index:03d}_Video_720p.mp4"


def sanitize_filename_for_video(filename):
    """Sanitize filename and ensure proper .mp4 extension (not .mp4.video)."""
    import unicodedata
    import re

    # Basic sanitization
    sanitized = unicodedata.normalize('NFKD', filename)
    sanitized = re.sub(r'[^\w\-_. ]', '_', sanitized)
    sanitized = re.sub(r'[_\-\s]+', '_', sanitized)
    sanitized = sanitized.strip('_.')

    # CRITICAL: Ensure .mp4 extension only (not .mp4.video)
    if not sanitized.lower().endswith('.mp4'):
        # Remove any existing extension and add .mp4
        if '.' in sanitized:
            sanitized = sanitized.rsplit('.', 1)[0]
        sanitized = f"{sanitized}.mp4"

    return sanitized


def download_video(url, local_path, headers, cookies):
    """Download a single video file with proper error handling."""
    try:
        print(f"  Downloading to: {local_path.name}")

        # Create directory if needed
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # Download with progress
        response = requests.get(url, headers=headers, cookies=cookies, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        # Create temporary file
        temp_path = local_path.with_suffix('.tmp')

        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)

                    # Show progress
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(f"  Progress: {progress:.1f}%", end='\r')

        # Move temp file to final location with CORRECT extension
        final_path = local_path.parent / sanitize_filename_for_video(local_path.name)
        temp_path.replace(final_path)

        print(f"  SUCCESS: Downloaded {final_path.name}")
        return True

    except Exception as e:
        print(f"  ERROR: Failed to download - {e}")
        # Clean up temp file
        temp_path = local_path.with_suffix('.tmp')
        if temp_path.exists():
            temp_path.unlink()
        return False


def download_course_videos_with_fixes(course_dir="courses/business-english-intro"):
    """Download all videos from extracted URLs with proper naming fixes."""

    print("Enhanced Video Downloader with Sequential Numbering & Extension Fixes")
    print("=" * 70)

    # Load credentials
    load_dotenv()
    cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')

    if not cauth_cookie:
        print("ERROR: COURSERA_CAUTH_COOKIE not found in .env file")
        return False

    # Setup authentication
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    cookies = {'CAUTH': cauth_cookie}

    course_path = Path(course_dir)
    if not course_path.exists():
        print(f"ERROR: Course directory not found: {course_path}")
        return False

    print(f"Course directory: {course_path}")
    print()

    # Process each module
    total_downloaded = 0
    total_failed = 0

    for module_dir in sorted(course_path.glob("module-*")):
        if not module_dir.is_dir():
            continue

        print(f"Processing {module_dir.name}:")
        module_video_count = 0

        # Process each lesson in the module
        for lesson_dir in sorted(module_dir.glob("lesson-*")):
            if not lesson_dir.is_dir():
                continue

            content_urls_file = lesson_dir / "content_urls.txt"
            lesson_metadata_file = lesson_dir / "lesson_metadata.json"

            if not content_urls_file.exists():
                print(f"  Skipping {lesson_dir.name} - no content URLs")
                continue

            # Load lesson metadata for naming
            lesson_metadata = None
            if lesson_metadata_file.exists():
                try:
                    with open(lesson_metadata_file, 'r', encoding='utf-8') as f:
                        lesson_metadata = json.load(f)
                except:
                    pass

            # Extract video URLs
            video_info = extract_video_name_from_url_content(content_urls_file)

            if not video_info:
                print(f"  Skipping {lesson_dir.name} - no 720p MP4 videos found")
                continue

            print(f"  {lesson_dir.name}: Found {len(video_info)} videos")

            # Download each video with sequential numbering
            for i, video_data in enumerate(video_info, 1):
                try:
                    # Create sequential filename with proper naming
                    sequential_filename = create_sequential_video_name(
                        module_video_count + i,  # Global sequence across module
                        lesson_dir.name,
                        lesson_metadata
                    )

                    # Ensure proper extension (this prevents .mp4.video)
                    sequential_filename = sanitize_filename_for_video(sequential_filename)

                    video_path = lesson_dir / sequential_filename

                    # Skip if already exists
                    if video_path.exists():
                        print(f"    SKIP: {sequential_filename} (already exists)")
                        continue

                    print(f"    [{i}/{len(video_info)}] Downloading: {sequential_filename}")

                    success = download_video(
                        video_data['url'],
                        video_path,
                        headers,
                        cookies
                    )

                    if success:
                        total_downloaded += 1
                    else:
                        total_failed += 1

                    # Small delay between downloads
                    time.sleep(1)

                except Exception as e:
                    print(f"    ERROR: Failed to process video {i}: {e}")
                    total_failed += 1

            module_video_count += len(video_info)

        print()

    print("=" * 70)
    print(f"Download Summary:")
    print(f"Successfully downloaded: {total_downloaded} videos")
    print(f"Failed downloads: {total_failed} videos")
    print(f"Total processed: {total_downloaded + total_failed} videos")
    print()
    print("Fixes Applied:")
    print("✓ Sequential numbering (001_, 002_, 003_, etc.)")
    print("✓ Proper .mp4 extension (no .mp4.video)")
    print("✓ 720p MP4 format only")
    print()
    print("Check your course directory for properly named videos!")

    return total_downloaded > 0


if __name__ == "__main__":
    success = download_course_videos_with_fixes()
    if success:
        print("SUCCESS: Video download completed with fixes applied!")
    else:
        print("ERROR: Video download failed!")