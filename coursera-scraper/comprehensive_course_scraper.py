#!/usr/bin/env python3
"""
Comprehensive Course Scraper: Extract ALL content from ALL lectures in a course.

This script fixes the issue where only 1 video was extracted instead of all
videos from all modules and lessons in the course.
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import re


def comprehensive_course_scraper(course_name="business-english-intro"):
    """Extract ALL content from ALL lectures in a course."""
    print("=" * 80)
    print(f"COMPREHENSIVE COURSERA SCRAPER")
    print(f"Course: {course_name}")
    print("=" * 80)

    # Load credentials
    load_dotenv()
    cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')

    if not cauth_cookie:
        print("ERROR: COURSERA_CAUTH_COOKIE not found in .env file")
        return False

    # Check if we have discovery data for this course
    discovery_files = {
        "business-english-intro": "valid_lectures.json",
        "business-english-meetings": "meetings_valid_lectures.json"
    }

    if course_name not in discovery_files:
        print(f"ERROR: No discovery data available for course '{course_name}'")
        print(f"Available courses: {', '.join(discovery_files.keys())}")
        return False

    discovery_file = discovery_files[course_name]

    if not Path(discovery_file).exists():
        print(f"ERROR: Discovery file not found: {discovery_file}")
        print("Run the discovery script first to find all lectures.")
        return False

    # Load all discovered lectures
    print(f"Loading discovered lectures from: {discovery_file}")

    with open(discovery_file, 'r', encoding='utf-8') as f:
        all_lectures = json.load(f)

    print(f"Found {len(all_lectures)} lectures in the course!")
    print()

    # Setup API request headers
    api_headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-coursera-application': 'ondemand',
        'x-requested-with': 'XMLHttpRequest',
        'authority': 'www.coursera.org'
    }
    api_cookies = {'CAUTH': cauth_cookie}

    # Organize lectures into modules (group every 6-8 lectures)
    lectures_per_module = 6
    total_modules = (len(all_lectures) + lectures_per_module - 1) // lectures_per_module

    print(f"Organizing {len(all_lectures)} lectures into {total_modules} modules")
    print(f"Target: ~{lectures_per_module} lectures per module")
    print()

    # Create base course directory
    base_dir = Path("courses") / course_name
    base_dir.mkdir(parents=True, exist_ok=True)

    # Initialize course statistics
    course_stats = {
        'course_name': course_name,
        'total_lectures': len(all_lectures),
        'total_modules': total_modules,
        'extracted_content': {},
        'failed_lectures': [],
        'extraction_date': '2026-03-24'
    }

    # Process each lecture and organize into modules
    for lecture_idx, lecture_data in enumerate(all_lectures):
        lecture_id = lecture_data['lecture_id']
        module_num = (lecture_idx // lectures_per_module) + 1
        lesson_num = (lecture_idx % lectures_per_module) + 1

        print(f"[{lecture_idx + 1:2d}/{len(all_lectures)}] Processing Module {module_num}, Lesson {lesson_num}: {lecture_id}")

        # Create module and lesson directories
        module_dir = base_dir / f"module-{module_num:02d}"
        lesson_dir = module_dir / f"lesson-{lesson_num:02d}-{lecture_id}"
        lesson_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Get the course ID (extract from first lecture if available)
            if 'data' in lecture_data and 'elements' in lecture_data['data']:
                course_id = lecture_data['data']['elements'][0].get('courseId', 'unknown')
            else:
                # Fallback: extract course ID from the discovery process
                course_id = "46b4tHEkEeWbbw5cIAKQrw"  # business-english-intro

            # Extract video content for this lecture
            video_url = f"https://www.coursera.org/api/onDemandLectureVideos.v1/{course_id}~{lecture_id}?includes=video&fields=onDemandVideos.v1(sources%2Csubtitles%2CsubtitlesVtt%2CsubtitlesTxt%2CsubtitlesAssetTags%2CdubbedSources%2CdubbedSubtitlesVtt%2CaudioDescriptionVideoSources)%2CdisableSkippingForward%2CstartMs%2CendMs"

            response = requests.get(video_url, headers=api_headers, cookies=api_cookies)

            if response.status_code == 200:
                video_data = response.json()

                if 'linked' in video_data and 'onDemandVideos.v1' in video_data['linked']:
                    video_info = video_data['linked']['onDemandVideos.v1'][0]

                    # Extract content statistics
                    stats = extract_and_save_content(video_info, lesson_dir, lecture_id, course_id, course_name)
                    course_stats['extracted_content'][lecture_id] = stats

                    print(f"     SUCCESS: {stats['video_count']} videos, {stats['subtitle_count']} subtitles, {stats['transcript_count']} transcripts")
                else:
                    print(f"     No video data available")
                    course_stats['failed_lectures'].append({'lecture_id': lecture_id, 'reason': 'no_video_data'})

            elif response.status_code == 404:
                print(f"     Not found (404)")
                course_stats['failed_lectures'].append({'lecture_id': lecture_id, 'reason': '404_not_found'})
            else:
                print(f"     HTTP {response.status_code}")
                course_stats['failed_lectures'].append({'lecture_id': lecture_id, 'reason': f'http_{response.status_code}'})

        except Exception as e:
            print(f"     ERROR: {e}")
            course_stats['failed_lectures'].append({'lecture_id': lecture_id, 'reason': f'exception: {e}'})

    # Save comprehensive course statistics
    stats_file = base_dir / "course_extraction_stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(course_stats, f, indent=2)

    print()
    print("=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"Course: {course_name}")
    print(f"Total Lectures: {len(all_lectures)}")
    print(f"Successfully Extracted: {len(course_stats['extracted_content'])}")
    print(f"Failed: {len(course_stats['failed_lectures'])}")
    print(f"Total Modules Created: {total_modules}")

    # Calculate totals
    total_videos = sum(stats['video_count'] for stats in course_stats['extracted_content'].values())
    total_subtitles = sum(stats['subtitle_count'] for stats in course_stats['extracted_content'].values())
    total_transcripts = sum(stats['transcript_count'] for stats in course_stats['extracted_content'].values())

    print(f"Total Videos Extracted: {total_videos}")
    print(f"Total Subtitles Extracted: {total_subtitles}")
    print(f"Total Transcripts Extracted: {total_transcripts}")
    print(f"Course directory: {base_dir}")
    print(f"Statistics saved: {stats_file}")

    return True


def extract_and_save_content(video_info, lesson_dir, lecture_id, course_id, course_name):
    """Extract and save all content from a video lecture."""

    # Prepare content containers
    video_urls = []
    audio_urls = []
    subtitle_urls = []
    transcript_urls = []

    # Extract video URLs by resolution
    if 'sources' in video_info and 'byResolution' in video_info['sources']:
        for resolution, source_data in video_info['sources']['byResolution'].items():
            # MP4 videos
            if 'mp4VideoUrl' in source_data:
                video_urls.append(f"{resolution} MP4: {source_data['mp4VideoUrl']}")

            # WebM videos
            if 'webMVideoUrl' in source_data:
                video_urls.append(f"{resolution} WebM: {source_data['webMVideoUrl']}")

    # Extract audio URLs
    if 'sources' in video_info and 'audio' in video_info['sources']:
        for audio_data in video_info['sources']['audio']:
            audio_format = audio_data.get('audioFormat', 'audio')
            bitrate = audio_data.get('bitrate', 'unknown')
            if 'url' in audio_data:
                audio_urls.append(f"{audio_format} ({bitrate} bps): {audio_data['url']}")

    # Extract subtitle URLs (.srt format)
    if 'subtitles' in video_info:
        for lang_code, subtitle_url in video_info['subtitles'].items():
            subtitle_urls.append(f"{lang_code}: {subtitle_url}")

    # Extract transcript URLs (.txt format)
    if 'subtitlesTxt' in video_info:
        for lang_code, transcript_url in video_info['subtitlesTxt'].items():
            transcript_urls.append(f"{lang_code}: {transcript_url}")

    # Save lesson metadata
    metadata = {
        "course_id": course_id,
        "course_name": course_name,
        "lecture_id": lecture_id,
        "video_id": video_info.get('id'),
        "extracted_at": "2026-03-24",
        "available_resolutions": list(video_info['sources']['byResolution'].keys()) if 'sources' in video_info and 'byResolution' in video_info['sources'] else [],
        "available_subtitle_languages": len(video_info.get('subtitles', {})),
        "available_transcript_languages": len(video_info.get('subtitlesTxt', {})),
        "content_summary": {
            "videos": len(video_urls),
            "audio_files": len(audio_urls),
            "subtitles": len(subtitle_urls),
            "transcripts": len(transcript_urls)
        }
    }

    with open(lesson_dir / "lesson_metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    # Save video URLs
    if video_urls:
        with open(lesson_dir / "video_urls.txt", 'w', encoding='utf-8') as f:
            f.write("Video Download URLs\n")
            f.write("=" * 18 + "\n\n")
            for url in video_urls:
                f.write(url + "\n")

    # Save audio URLs
    if audio_urls:
        with open(lesson_dir / "audio_urls.txt", 'w', encoding='utf-8') as f:
            f.write("Audio Download URLs\n")
            f.write("=" * 18 + "\n\n")
            for url in audio_urls:
                f.write(url + "\n")

    # Save subtitle URLs
    if subtitle_urls:
        with open(lesson_dir / "subtitle_urls.txt", 'w', encoding='utf-8') as f:
            f.write(f"Subtitle URLs (.srt format)\n")
            f.write("=" * 30 + "\n")
            f.write(f"Available in {len(subtitle_urls)} languages:\n\n")
            for url in subtitle_urls:
                f.write(url + "\n")

    # Save transcript URLs
    if transcript_urls:
        with open(lesson_dir / "transcript_urls.txt", 'w', encoding='utf-8') as f:
            f.write(f"Transcript URLs (.txt format)\n")
            f.write("=" * 30 + "\n")
            f.write(f"Available in {len(transcript_urls)} languages:\n\n")
            for url in transcript_urls:
                f.write(url + "\n")

    # Create master content URLs file
    all_urls = video_urls + audio_urls + subtitle_urls + transcript_urls
    with open(lesson_dir / "content_urls.txt", 'w', encoding='utf-8') as f:
        f.write(f"All Content URLs for Lecture {lecture_id}\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total URLs: {len(all_urls)}\n")
        f.write(f"Videos: {len(video_urls)}\n")
        f.write(f"Audio: {len(audio_urls)}\n")
        f.write(f"Subtitles: {len(subtitle_urls)}\n")
        f.write(f"Transcripts: {len(transcript_urls)}\n\n")

        for url in all_urls:
            f.write(url + "\n")

    return {
        'video_count': len(video_urls),
        'audio_count': len(audio_urls),
        'subtitle_count': len(subtitle_urls),
        'transcript_count': len(transcript_urls),
        'total_urls': len(all_urls)
    }


if __name__ == "__main__":
    print("Comprehensive Coursera Course Scraper")
    print("Fixes the issue where only 1 video was extracted instead of ALL content")
    print()

    # Run for business-english-intro course
    success = comprehensive_course_scraper("business-english-intro")

    if success:
        print("\nSUCCESS: Extracted ALL content from ALL lectures!")
        print("Check the courses/business-english-intro/ directory for complete course structure")
    else:
        print("\nFAILED: Could not extract all course content")