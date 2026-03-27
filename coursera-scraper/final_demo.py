#!/usr/bin/env python3
"""
Final demo showing what content can be extracted from the business-english-intro course.
Simple version without complex imports.
"""

import os
import json
import requests
from dotenv import load_dotenv

def demo_extraction():
    """Demonstrate what the scraper can extract."""
    print("Coursera Video Content Extraction Demo")
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

    # Get video content from business-english-intro course
    course_id = "46b4tHEkEeWbbw5cIAKQrw"
    lecture_id = "sf1NL"  # Video Email Guidelines
    url = f"https://www.coursera.org/api/onDemandLectureVideos.v1/{course_id}~{lecture_id}?includes=video&fields=onDemandVideos.v1(sources%2Csubtitles%2CsubtitlesVtt%2CsubtitlesTxt%2CsubtitlesAssetTags%2CdubbedSources%2CdubbedSubtitlesVtt%2CaudioDescriptionVideoSources)%2CdisableSkippingForward%2CstartMs%2CendMs"

    try:
        response = requests.get(url, headers=headers, cookies=cookies)

        if response.status_code != 200:
            print(f"ERROR: API request failed with status {response.status_code}")
            return False

        data = response.json()
        video_info = data['linked']['onDemandVideos.v1'][0]

        print(f"Course ID: {course_id}")
        print(f"Lecture ID: {lecture_id}")
        print(f"Video ID: {video_info.get('id')}")
        print()

        print("EXTRACTABLE CONTENT:")
        print("-" * 30)

        # Video Sources
        print("1. VIDEO FILES:")
        if 'sources' in video_info and 'byResolution' in video_info['sources']:
            for resolution, source_data in video_info['sources']['byResolution'].items():
                print(f"   {resolution}:")
                if 'mp4VideoUrl' in source_data:
                    mp4_url = source_data['mp4VideoUrl']
                    print(f"     - MP4: ...{mp4_url[-50:]}")
                if 'webMVideoUrl' in source_data:
                    webm_url = source_data['webMVideoUrl']
                    print(f"     - WebM: ...{webm_url[-50:]}")

        # Audio Sources
        print("\n2. AUDIO FILES:")
        if 'sources' in video_info and 'audio' in video_info['sources']:
            for audio in video_info['sources']['audio']:
                format_type = audio['audioFormat']
                bitrate = audio['bitrate']
                audio_url = audio['url']
                print(f"   {format_type} ({bitrate} bps): ...{audio_url[-50:]}")

        # Subtitles
        print("\n3. SUBTITLE FILES (.srt):")
        if 'subtitles' in video_info:
            languages = list(video_info['subtitles'].keys())
            print(f"   Available in {len(languages)} languages:")
            for i, lang in enumerate(languages[:10]):  # Show first 10
                url = video_info['subtitles'][lang]
                print(f"     {lang}: ...{url[-50:]}")
            if len(languages) > 10:
                print(f"     ... and {len(languages) - 10} more languages")

        # Transcripts
        print("\n4. TRANSCRIPT FILES (.txt):")
        if 'subtitlesTxt' in video_info:
            transcript_languages = list(video_info['subtitlesTxt'].keys())
            print(f"   Available in {len(transcript_languages)} languages:")
            major_langs = ['en', 'es', 'fr', 'de', 'zh-CN', 'ja', 'ko']
            for lang in major_langs:
                if lang in video_info['subtitlesTxt']:
                    url = video_info['subtitlesTxt'][lang]
                    print(f"     {lang}: ...{url[-50:]}")

        # Folder structure
        print("\n5. FOLDER STRUCTURE TO BE CREATED:")
        print("   courses/")
        print("   └── business-english-intro/")
        print("       ├── course_metadata.json")
        print("       ├── content_urls.txt")
        print("       └── module-03-professional-communication/")
        print("           ├── module_metadata.json")
        print("           └── lesson-01-video-email-guidelines/")
        print("               ├── lesson_metadata.json")
        print("               ├── video_720p.mp4     # High quality video")
        print("               ├── video_360p.mp4     # Lower quality backup")
        print("               ├── audio_64kbps.mp3   # Audio version")
        print("               ├── subtitles_en.srt   # English subtitles")
        print("               ├── subtitles_es.srt   # Spanish subtitles")
        print("               ├── subtitles_fr.srt   # French subtitles")
        print("               ├── transcript_en.txt  # English transcript")
        print("               └── content_urls.txt   # All URLs for reference")

        print("\nSUMMARY:")
        print(f"✓ {len(video_info['sources']['byResolution'])} video resolutions available")
        print(f"✓ {len(video_info['sources']['audio'])} audio formats available")
        print(f"✓ {len(video_info['subtitles'])} subtitle languages available")
        print(f"✓ {len(video_info['subtitlesTxt'])} transcript languages available")

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = demo_extraction()
    if success:
        print("\nDemo completed successfully!")
        print("The scraper can extract all this content and organize it into folders.")
    else:
        print("\nDemo failed. Check your credentials.")