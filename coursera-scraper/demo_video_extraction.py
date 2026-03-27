#!/usr/bin/env python3
"""
Demo script showing how to extract video content from the business-english-intro course.
"""

import os
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from api.auth import CourseraAuth
from api.coursera_client import CourseraClient

def demo_video_extraction():
    """Demonstrate extracting video URLs and content from a real lecture."""
    print("🎬 Demo: Extracting Video Content from Business English Course")
    print("=" * 70)

    try:
        # Setup authentication
        auth = CourseraAuth()
        client = CourseraClient.from_config_file("config/api_endpoints.json", auth)

        # Real course and lecture from your business-english-intro course
        course_id = "46b4tHEkEeWbbw5cIAKQrw"
        lecture_id = "sf1NL"  # "Video Email Guidelines" lecture

        print(f"📚 Course ID: {course_id}")
        print(f"🎓 Lecture ID: {lecture_id}")
        print("\n🔄 Fetching video content...")

        # Get video data
        video_data = client.get_lecture_video(course_id, lecture_id)
        video_info = video_data['linked']['onDemandVideos.v1'][0]

        print("✅ Video data retrieved successfully!")
        print("\n📊 Available Content:")

        # Extract video URLs
        print("\n🎥 Video Sources:")
        if 'sources' in video_info and 'byResolution' in video_info['sources']:
            for resolution, source_data in video_info['sources']['byResolution'].items():
                print(f"  📺 {resolution}:")
                if 'mp4VideoUrl' in source_data:
                    print(f"     MP4: {source_data['mp4VideoUrl'][:80]}...")
                if 'webMVideoUrl' in source_data:
                    print(f"     WebM: {source_data['webMVideoUrl'][:80]}...")

        # Extract audio
        print("\n🔊 Audio Sources:")
        if 'sources' in video_info and 'audio' in video_info['sources']:
            for audio in video_info['sources']['audio']:
                format_type = audio['audioFormat']
                bitrate = audio['bitrate']
                url = audio['url']
                print(f"  🎵 {format_type} ({bitrate} bps): {url[:80]}...")

        # Extract subtitles
        print("\n📝 Subtitle Languages:")
        if 'subtitles' in video_info:
            subtitle_count = 0
            for lang, url in video_info['subtitles'].items():
                if subtitle_count < 5:  # Show first 5 languages
                    print(f"  🌐 {lang}: {url[:80]}...")
                subtitle_count += 1
            if subtitle_count > 5:
                print(f"  ... and {subtitle_count - 5} more languages")

        # Extract transcript
        print("\n📄 Transcripts:")
        if 'subtitlesTxt' in video_info:
            transcript_langs = ['en', 'es', 'fr', 'de', 'zh-CN']  # Show major languages
            for lang in transcript_langs:
                if lang in video_info['subtitlesTxt']:
                    url = video_info['subtitlesTxt'][lang]
                    print(f"  📜 {lang}: {url[:80]}...")

        # Show what the scraper would create
        print(f"\n📁 Folder Structure That Would Be Created:")
        course_name = "business-english-intro"
        module_name = "module-03-professional-communication"
        lesson_name = "lesson-01-video-email-guidelines"

        print(f"courses/")
        print(f"└── {course_name}/")
        print(f"    ├── course_metadata.json")
        print(f"    ├── content_urls.txt")
        print(f"    └── {module_name}/")
        print(f"        ├── module_metadata.json")
        print(f"        └── {lesson_name}/")
        print(f"            ├── lesson_metadata.json")
        print(f"            ├── video_720p.mp4          # Downloaded video")
        print(f"            ├── video_360p.mp4          # Lower resolution backup")
        print(f"            ├── audio_64kbps.mp3        # Audio version")
        print(f"            ├── subtitles_en.srt        # English subtitles")
        print(f"            ├── subtitles_es.srt        # Spanish subtitles")
        print(f"            ├── transcript_en.txt       # Text transcript")
        print(f"            └── content_urls.txt        # All URLs for reference")

        print(f"\n🎉 Demo completed successfully!")
        print(f"📋 Summary:")
        print(f"   - Video available in {len(video_info['sources']['byResolution'])} resolutions")
        print(f"   - Audio available in {len(video_info['sources']['audio'])} formats")
        print(f"   - Subtitles available in {len(video_info['subtitles'])} languages")
        print(f"   - Transcripts available in {len(video_info['subtitlesTxt'])} languages")

        return True

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

if __name__ == "__main__":
    demo_video_extraction()