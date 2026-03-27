#!/usr/bin/env python3
"""
Direct demo: Extract and organize video content from business-english-intro course.
Works with the APIs we know are accessible.
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

def run_scraper_demo():
    """Run a direct demo of the scraper functionality."""
    print("="*60)
    print("COURSERA SCRAPER - LIVE DEMONSTRATION")
    print("="*60)

    # Load credentials
    load_dotenv()
    cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')

    if not cauth_cookie:
        print("ERROR: COURSERA_CAUTH_COOKIE not found in .env file")
        return False

    # Setup request parameters
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'x-coursera-application': 'ondemand',
        'x-requested-with': 'XMLHttpRequest',
        'authority': 'www.coursera.org'
    }
    cookies = {'CAUTH': cauth_cookie}

    # Course and lecture info
    course_id = "46b4tHEkEeWbbw5cIAKQrw"  # business-english-intro
    course_name = "business-english-intro"
    lecture_id = "sf1NL"  # Video Email Guidelines
    lesson_title = "video-email-guidelines"

    print(f"Course: {course_name}")
    print(f"Lecture: {lesson_title}")
    print(f"Course ID: {course_id}")
    print(f"Lecture ID: {lecture_id}")
    print()

    # Step 1: Fetch video content
    print("STEP 1: Fetching video content from Coursera API...")
    url = f"https://www.coursera.org/api/onDemandLectureVideos.v1/{course_id}~{lecture_id}?includes=video&fields=onDemandVideos.v1(sources%2Csubtitles%2CsubtitlesVtt%2CsubtitlesTxt%2CsubtitlesAssetTags%2CdubbedSources%2CdubbedSubtitlesVtt%2CaudioDescriptionVideoSources)%2CdisableSkippingForward%2CstartMs%2CendMs"

    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        if response.status_code != 200:
            print(f"ERROR: API request failed with status {response.status_code}")
            return False

        data = response.json()
        print("SUCCESS: Video content retrieved from Coursera API")
        print()

        # Step 2: Create folder structure
        print("STEP 2: Creating organized folder structure...")
        base_dir = Path("courses")
        course_dir = base_dir / course_name
        module_dir = course_dir / "module-03-professional-communication"
        lesson_dir = module_dir / f"lesson-01-{lesson_title}"

        # Create directories
        lesson_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created: {lesson_dir}")

        # Step 3: Extract and save content
        print()
        print("STEP 3: Extracting and saving content...")

        video_info = data['linked']['onDemandVideos.v1'][0]

        # Save metadata
        metadata = {
            "course_id": course_id,
            "course_name": course_name,
            "lecture_id": lecture_id,
            "lesson_title": lesson_title,
            "video_id": video_info.get('id'),
            "extracted_at": "2026-03-24",
            "available_resolutions": list(video_info['sources']['byResolution'].keys()),
            "available_subtitle_languages": len(video_info['subtitles']),
            "available_transcript_languages": len(video_info['subtitlesTxt'])
        }

        with open(lesson_dir / "lesson_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        print(f"Saved: lesson_metadata.json")

        # Save video URLs
        video_urls = []
        for resolution, source_data in video_info['sources']['byResolution'].items():
            if 'mp4VideoUrl' in source_data:
                video_urls.append(f"{resolution} MP4: {source_data['mp4VideoUrl']}")
            if 'webMVideoUrl' in source_data:
                video_urls.append(f"{resolution} WebM: {source_data['webMVideoUrl']}")

        with open(lesson_dir / "video_urls.txt", 'w', encoding='utf-8') as f:
            f.write("Video Download URLs\n")
            f.write("==================\n\n")
            for url in video_urls:
                f.write(f"{url}\n")
        print(f"Saved: video_urls.txt ({len(video_urls)} video URLs)")

        # Save audio URLs
        audio_urls = []
        for audio in video_info['sources']['audio']:
            audio_urls.append(f"{audio['audioFormat']} ({audio['bitrate']} bps): {audio['url']}")

        with open(lesson_dir / "audio_urls.txt", 'w', encoding='utf-8') as f:
            f.write("Audio Download URLs\n")
            f.write("==================\n\n")
            for url in audio_urls:
                f.write(f"{url}\n")
        print(f"Saved: audio_urls.txt ({len(audio_urls)} audio URLs)")

        # Save subtitle URLs (sample of major languages)
        major_languages = ['en', 'es', 'fr', 'de', 'zh-CN', 'ja', 'ko', 'hi', 'ru', 'ar']
        subtitle_urls = []
        for lang in major_languages:
            if lang in video_info['subtitles']:
                subtitle_urls.append(f"{lang} SRT: {video_info['subtitles'][lang]}")
            if lang in video_info['subtitlesTxt']:
                subtitle_urls.append(f"{lang} TXT: {video_info['subtitlesTxt'][lang]}")

        with open(lesson_dir / "subtitle_urls.txt", 'w', encoding='utf-8') as f:
            f.write("Subtitle & Transcript URLs\n")
            f.write("=========================\n\n")
            f.write(f"Available in {len(video_info['subtitles'])} languages total\n")
            f.write("Major languages shown below:\n\n")
            for url in subtitle_urls:
                f.write(f"{url}\n")
        print(f"Saved: subtitle_urls.txt ({len(video_info['subtitles'])} languages available)")

        # Save all URLs combined
        all_urls = video_urls + audio_urls + subtitle_urls
        with open(lesson_dir / "content_urls.txt", 'w', encoding='utf-8') as f:
            f.write("All Content URLs\n")
            f.write("===============\n\n")
            f.write(f"Extracted from: {course_name}\n")
            f.write(f"Lesson: {lesson_title}\n")
            f.write(f"Total content items: {len(all_urls)}\n\n")
            for url in all_urls:
                f.write(f"{url}\n")
        print(f"Saved: content_urls.txt (master list)")

        # Step 4: Show results
        print()
        print("STEP 4: Scraping completed successfully!")
        print()
        print("EXTRACTED CONTENT SUMMARY:")
        print("-" * 40)
        print(f"Video resolutions: {len(video_info['sources']['byResolution'])}")
        print(f"Audio formats: {len(video_info['sources']['audio'])}")
        print(f"Subtitle languages: {len(video_info['subtitles'])}")
        print(f"Transcript languages: {len(video_info['subtitlesTxt'])}")
        print()
        print("CREATED FILE STRUCTURE:")
        print("-" * 40)
        print(f"{lesson_dir}/")
        print("├── lesson_metadata.json      # Lesson information")
        print("├── video_urls.txt           # Video download URLs")
        print("├── audio_urls.txt           # Audio download URLs")
        print("├── subtitle_urls.txt        # Subtitle URLs")
        print("└── content_urls.txt         # Master URL list")
        print()
        print(f"Location: {lesson_dir.absolute()}")
        print()
        print("SUCCESS: Coursera scraper demonstration completed!")
        print("The scraper successfully extracted and organized course content.")

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = run_scraper_demo()
    if success:
        print("\nREADY FOR FULL DEPLOYMENT!")
    else:
        print("\nDemo failed. Check your credentials.")