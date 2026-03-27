#!/usr/bin/env python3
"""
Demo script showing how to use the enhanced video and subtitle downloader.
This script demonstrates downloading both videos and English subtitles with proper naming.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.api.auth import CourseraAuth
from src.api.enhanced_downloader import EnhancedVideoDownloader
from src.core.file_manager import FileManager


def main():
    """Demonstrate enhanced video and subtitle downloading."""
    print("=" * 80)
    print("ENHANCED VIDEO AND SUBTITLE DOWNLOADER DEMO")
    print("=" * 80)

    # Load environment variables
    load_dotenv()

    # Get authentication cookie
    cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')
    if not cauth_cookie:
        print("ERROR: COURSERA_CAUTH_COOKIE not found in .env file")
        print("Please add your Coursera CAUTH cookie to the .env file")
        return False

    try:
        # Initialize authentication
        print("Initializing authentication...")
        auth = CourseraAuth()
        auth.cauth_cookie = cauth_cookie

        # Initialize file manager
        print("Initializing file manager...")
        file_manager = FileManager("./courses")

        # Initialize enhanced downloader
        print("Initializing enhanced downloader...")
        downloader = EnhancedVideoDownloader(
            auth=auth,
            file_manager=file_manager,
            max_concurrent=3,           # Download 3 files simultaneously
            download_subtitles=True,    # Enable subtitle downloading
            subtitle_language='en'      # Download English subtitles
        )

        # Set course path (assuming the course has already been scraped)
        course_path = Path("courses/business-english-intro")

        if not course_path.exists():
            print(f"ERROR: Course directory not found: {course_path}")
            print("Please run the course scraper first to extract the course structure.")
            return False

        print(f"Course path: {course_path}")
        print()

        # Download videos and subtitles
        print("Starting download of videos and subtitles...")
        print("This will download:")
        print("- 720p MP4 videos with sequential naming (1_video_name.mp4)")
        print("- English VTT subtitles with matching names (1_video_name.vtt)")
        print()

        result = downloader.download_course_videos_and_subtitles(
            course_path=course_path,
            target_resolution="720p",
            resume=False  # Set to True to resume interrupted downloads
        )

        # Print results
        print("\n" + "=" * 80)
        print("DOWNLOAD RESULTS")
        print("=" * 80)

        if result:
            print("Videos:")
            print(f"  Downloaded: {result['videos']['downloaded']}")
            print(f"  Skipped: {result['videos']['skipped']}")
            print(f"  Failed: {result['videos']['failed']}")
            print()
            print("Subtitles:")
            print(f"  Downloaded: {result['subtitles']['downloaded']}")
            print(f"  Skipped: {result['subtitles']['skipped']}")
            print(f"  Failed: {result['subtitles']['failed']}")
            print()

            total_downloaded = result['videos']['downloaded'] + result['subtitles']['downloaded']
            if total_downloaded > 0:
                print(f"SUCCESS: {total_downloaded} files downloaded successfully!")
                print("\nFile naming convention:")
                print("- Videos: 1_video_name.mp4, 2_video_name.mp4, ...")
                print("- Subtitles: 1_video_name.vtt, 2_video_name.vtt, ...")
                return True
            else:
                print("No new files were downloaded (all files may already exist).")
                return True
        else:
            print("ERROR: Download failed")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)