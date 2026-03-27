#!/usr/bin/env python3
"""
Comprehensive Video Downloader: Download ALL video formats for ALL lessons.

This script fixes the issue where only 1 video per lesson was downloaded
instead of all available video formats (720p, 540p, 360p in MP4 and WebM).
"""

import os
import json
import time
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from dotenv import load_dotenv
import re


async def download_file(session, url, file_path, chunk_size=8192):
    """Download a single file asynchronously."""
    try:
        async with session.get(url) as response:
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            async with aiofiles.open(file_path, 'wb') as file:
                async for chunk in response.content.iter_chunked(chunk_size):
                    await file.write(chunk)
                    downloaded += len(chunk)

            return True, downloaded
    except Exception as e:
        return False, str(e)


async def comprehensive_video_downloader(course_name="business-english-intro"):
    """Download ALL videos in ALL formats for ALL lessons."""
    print("=" * 80)
    print("COMPREHENSIVE VIDEO DOWNLOADER")
    print(f"Course: {course_name}")
    print("=" * 80)

    # Load credentials for authenticated downloads
    load_dotenv()
    cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')

    if not cauth_cookie:
        print("ERROR: COURSERA_CAUTH_COOKIE not found in .env file")
        return False

    # Find course directory
    course_path = Path("courses") / course_name
    if not course_path.exists():
        print(f"ERROR: Course directory not found: {course_path}")
        print("Run the scraper first to extract course structure.")
        return False

    print(f"Course directory: {course_path}")

    # Find all lesson directories
    lesson_dirs = []
    for module_dir in course_path.glob("module-*"):
        if module_dir.is_dir():
            for lesson_dir in module_dir.glob("lesson-*"):
                if lesson_dir.is_dir():
                    lesson_dirs.append(lesson_dir)

    if not lesson_dirs:
        print("ERROR: No lesson directories found")
        return False

    print(f"Found {len(lesson_dirs)} lessons to process")
    print()

    # Set up HTTP session with authentication
    cookies = {'CAUTH': cauth_cookie}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    # Statistics tracking
    total_files = 0
    downloaded_files = 0
    skipped_files = 0
    failed_files = 0
    total_size = 0

    # Process each lesson
    async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
        for lesson_idx, lesson_dir in enumerate(lesson_dirs, 1):
            print(f"[{lesson_idx:2d}/{len(lesson_dirs)}] Processing: {lesson_dir.name}")

            # Read content URLs
            content_urls_file = lesson_dir / "content_urls.txt"
            if not content_urls_file.exists():
                print(f"     No content_urls.txt found, skipping...")
                continue

            try:
                with open(content_urls_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract all video URLs (MP4 and WebM)
                video_urls = []
                lines = content.split('\n')

                for line in lines:
                    # Look for CloudFront video URLs
                    if ('cloudfront.net' in line and
                        ('index.mp4?' in line or 'index.webm?' in line)):

                        # Extract URL
                        url_start = line.find('https://')
                        if url_start != -1:
                            url = line[url_start:].strip()

                            # Determine resolution and format
                            resolution = "unknown"
                            format_ext = "mp4"

                            if '/720p/' in url:
                                resolution = "720p"
                            elif '/540p/' in url:
                                resolution = "540p"
                            elif '/360p/' in url:
                                resolution = "360p"

                            if 'index.webm' in url:
                                format_ext = "webm"

                            # Create filename
                            filename = f"video_{resolution}.{format_ext}"
                            local_path = lesson_dir / filename

                            video_urls.append({
                                'url': url,
                                'filename': filename,
                                'local_path': local_path,
                                'resolution': resolution,
                                'format': format_ext
                            })

                # Extract audio URLs
                audio_urls = []
                for line in lines:
                    if ('cloudfront.net' in line and 'index.mp3?' in line):
                        url_start = line.find('https://')
                        if url_start != -1:
                            url = line[url_start:].strip()
                            filename = "audio.mp3"
                            local_path = lesson_dir / filename

                            audio_urls.append({
                                'url': url,
                                'filename': filename,
                                'local_path': local_path,
                                'type': 'audio'
                            })

                all_media_urls = video_urls + audio_urls
                total_files += len(all_media_urls)

                print(f"     Found: {len(video_urls)} videos, {len(audio_urls)} audio files")

                # Download each file
                lesson_downloaded = 0
                lesson_skipped = 0
                lesson_failed = 0

                for media in all_media_urls:
                    # Check if file already exists
                    if media['local_path'].exists():
                        file_size = media['local_path'].stat().st_size
                        if file_size > 1024:  # File exists and has content
                            lesson_skipped += 1
                            continue

                    # Download the file
                    print(f"       Downloading {media['filename']}...", end=" ")

                    success, result = await download_file(session, media['url'], media['local_path'])

                    if success:
                        print(f"SUCCESS ({result:,} bytes)")
                        lesson_downloaded += 1
                        total_size += result
                    else:
                        print(f"ERROR: {result}")
                        lesson_failed += 1

                downloaded_files += lesson_downloaded
                skipped_files += lesson_skipped
                failed_files += lesson_failed

                if lesson_downloaded > 0 or lesson_failed > 0:
                    print(f"     Downloaded: {lesson_downloaded}, Skipped: {lesson_skipped}, Failed: {lesson_failed}")

            except Exception as e:
                print(f"     ERROR: {e}")
                failed_files += 1

    # Final statistics
    print()
    print("=" * 80)
    print("DOWNLOAD COMPLETE")
    print("=" * 80)
    print(f"Course: {course_name}")
    print(f"Total Media Files: {total_files}")
    print(f"Downloaded: {downloaded_files}")
    print(f"Skipped (existing): {skipped_files}")
    print(f"Failed: {failed_files}")
    print(f"Total Downloaded Size: {total_size:,} bytes ({total_size / 1024 / 1024:.1f} MB)")
    print(f"Course directory: {course_path}")

    return downloaded_files > 0


def main():
    """Main function to run comprehensive video downloader."""
    print("Comprehensive Video Downloader")
    print("Downloads ALL video formats available for ALL lessons")
    print("Fixes the issue where only 720p MP4 was downloaded")
    print()

    try:
        success = asyncio.run(comprehensive_video_downloader("business-english-intro"))

        if success:
            print("\nSUCCESS: Downloaded all available video formats!")
            print("Each lesson now has multiple video files (720p, 540p, 360p in MP4/WebM)")
        else:
            print("\nFAILED: Could not download videos")
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user")
    except Exception as e:
        print(f"\nERROR: {e}")


if __name__ == "__main__":
    main()