#!/usr/bin/env python3
"""
Enhanced Video and Subtitle Downloader for Coursera
Downloads both 720p videos AND their corresponding English subtitles (.vtt)
with proper sequential naming and video name structure.
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
from typing import Dict, List, Optional, Tuple


class CourseraMediaDownloader:
    """Enhanced downloader for Coursera videos and subtitles."""

    def __init__(self, cauth_cookie: str):
        """Initialize the downloader with authentication."""
        self.cauth_cookie = cauth_cookie
        self.session = None

        # Headers for authenticated requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en',
            'Connection': 'keep-alive',
            'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-coursera-application': 'ondemand',
            'x-requested-with': 'XMLHttpRequest'
        }

        self.cookies = {'CAUTH': cauth_cookie}

        # Download statistics
        self.stats = {
            'videos': {'downloaded': 0, 'skipped': 0, 'failed': 0},
            'subtitles': {'downloaded': 0, 'skipped': 0, 'failed': 0},
            'total_size': 0
        }

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            cookies=self.cookies,
            timeout=aiohttp.ClientTimeout(total=30*60)  # 30 minute timeout
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    def sanitize_sequential_video_name(self, sequence_number: int, original_name: str, extension: str = '.mp4', max_length: int = 255) -> str:
        """Create sequential filename matching the existing naming convention."""
        # Create prefix with sequence number
        prefix = f"{sequence_number}_"

        # Remove extension if present to handle separately
        base_name = original_name
        if extension and original_name.endswith(extension):
            base_name = original_name[:-len(extension)]

        # Remove resolution patterns if present (e.g., _720p, _480p, etc.)
        resolution_patterns = ['_720p', '_540p', '_480p', '_360p', '_1080p']
        for pattern in resolution_patterns:
            if base_name.endswith(pattern):
                base_name = base_name[:-len(pattern)]
                break

        # Basic sanitization - replace problematic characters
        sanitized = re.sub(r'[^\w\-_. ]', '_', base_name)
        sanitized = re.sub(r'[_\-\s]+', '_', sanitized)
        sanitized = sanitized.strip('_.')

        # Calculate available length for base name
        available_length = max_length - len(prefix)
        if extension:
            if not extension.startswith('.'):
                extension = '.' + extension
            available_length -= len(extension)

        # Trim base name if needed
        if len(sanitized) > available_length:
            sanitized = sanitized[:available_length].rstrip('_.')

        # Combine prefix with sanitized name
        result = prefix + sanitized

        # Add extension
        if extension:
            result += extension

        # Fallback if name becomes too short
        if len(sanitized.strip('_')) == 0:
            timestamp = str(int(time.time()))
            if extension:
                result = f"{prefix}video_{timestamp}{extension}"
            else:
                result = f"{prefix}video_{timestamp}"

        return result

    def extract_video_metadata_from_lesson(self, lesson_dir: Path) -> Optional[Dict]:
        """Extract video metadata from lesson_metadata.json if available."""
        metadata_file = lesson_dir / "lesson_metadata.json"
        if not metadata_file.exists():
            return None

        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                lesson_metadata = json.load(f)

            # Look for video assets in the metadata
            if 'assets' in lesson_metadata:
                for asset in lesson_metadata['assets']:
                    if (asset.get('file_type') == 'video' and
                        '_720p.mp4' in asset.get('name', '') and
                        'metadata' in asset):

                        # Extract course_id and item_id from metadata
                        metadata = asset['metadata']
                        return {
                            'course_id': metadata.get('course_id'),
                            'item_id': metadata.get('item_id'),
                            'video_name': asset.get('name', ''),
                            'asset_metadata': metadata
                        }
        except Exception as e:
            print(f"     Warning: Could not parse lesson metadata: {e}")

        return None

    async def fetch_lecture_video_api(self, course_id: str, lecture_id: str) -> Optional[Dict]:
        """Fetch video and subtitle information from Coursera API."""
        if not course_id or not lecture_id:
            return None

        try:
            # Construct API URL
            url = f"https://www.coursera.org/api/onDemandLectureVideos.v1/{course_id}~{lecture_id}"
            params = {
                'includes': 'video',
                'fields': 'onDemandVideos.v1(sources,subtitles,subtitlesVtt,subtitlesTxt,subtitlesAssetTags,dubbedSources,dubbedSubtitlesVtt,audioDescriptionVideoSources),disableSkippingForward,startMs,endMs'
            }

            print(f"       Fetching video metadata from API...")

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    print(f"       Warning: API request failed with status {response.status}")
                    return None

        except Exception as e:
            print(f"       Warning: Could not fetch from API: {e}")
            return None

    def extract_subtitle_urls_from_api(self, api_data: Dict) -> List[Dict]:
        """Extract subtitle URLs from API response."""
        subtitle_urls = []

        try:
            if 'linked' in api_data and 'onDemandVideos.v1' in api_data['linked']:
                videos = api_data['linked']['onDemandVideos.v1']

                for video in videos:
                    if 'subtitlesVtt' in video:
                        subtitles_vtt = video['subtitlesVtt']

                        # Extract English subtitles
                        if 'en' in subtitles_vtt:
                            subtitle_url = subtitles_vtt['en']

                            # Convert relative URL to full URL
                            if subtitle_url.startswith('/api/'):
                                subtitle_url = f"https://www.coursera.org{subtitle_url}"

                            subtitle_urls.append({
                                'language': 'en',
                                'url': subtitle_url,
                                'format': 'vtt'
                            })

                        # Optionally, extract other subtitle languages
                        # for lang, url in subtitles_vtt.items():
                        #     if lang != 'en':  # Skip English as we already added it
                        #         if url.startswith('/api/'):
                        #             url = f"https://www.coursera.org{url}"
                        #         subtitle_urls.append({
                        #             'language': lang,
                        #             'url': url,
                        #             'format': 'vtt'
                        #         })

        except Exception as e:
            print(f"       Warning: Could not extract subtitle URLs: {e}")

        return subtitle_urls

    def extract_video_urls_from_content_file(self, lesson_dir: Path) -> List[Dict]:
        """Extract video URLs from content_urls.txt file."""
        content_urls_file = lesson_dir / "content_urls.txt"
        if not content_urls_file.exists():
            return []

        video_urls = []

        try:
            with open(content_urls_file, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')
            for line in lines:
                # Look for 720p MP4 videos
                if ('cloudfront.net' in line and
                    '/720p/' in line and
                    'index.mp4?' in line):

                    url_start = line.find('https://')
                    if url_start != -1:
                        url = line[url_start:].strip()
                        video_urls.append({
                            'url': url,
                            'resolution': '720p',
                            'format': 'mp4'
                        })
        except Exception as e:
            print(f"     Warning: Could not read content URLs: {e}")

        return video_urls

    def sort_lesson_directories(self, lesson_dirs: List[Path]) -> List[Path]:
        """Sort lesson directories by module order and then by lesson order."""
        def extract_order_numbers(lesson_path: Path):
            module_order = 0
            lesson_order = 0

            # Get module order from parent directory
            module_parent = lesson_path.parent.name
            module_match = re.search(r'module-(\d+)', module_parent)
            if module_match:
                module_order = int(module_match.group(1))

            # Get lesson order from directory name
            lesson_name = lesson_path.name
            lesson_match = re.search(r'lesson-(\d+)', lesson_name)
            if lesson_match:
                lesson_order = int(lesson_match.group(1))

            return (module_order, lesson_order)

        return sorted(lesson_dirs, key=extract_order_numbers)

    async def download_file(self, url: str, file_path: Path, file_type: str = 'file') -> Tuple[bool, any]:
        """Download a single file asynchronously."""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return False, f"HTTP {response.status}"

                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0

                # Create parent directory if it doesn't exist
                file_path.parent.mkdir(parents=True, exist_ok=True)

                # Create temporary file
                temp_path = file_path.with_suffix('.tmp')

                try:
                    async with aiofiles.open(temp_path, 'wb') as file:
                        async for chunk in response.content.iter_chunked(8192):
                            await file.write(chunk)
                            downloaded += len(chunk)

                    # Move temp file to final location
                    temp_path.replace(file_path)
                    self.stats['total_size'] += downloaded

                    return True, downloaded

                except Exception as e:
                    # Clean up temp file on error
                    if temp_path.exists():
                        temp_path.unlink()
                    raise e

        except Exception as e:
            return False, str(e)

    async def process_lesson(self, lesson_dir: Path, lesson_index: int, total_lessons: int, video_counter: int) -> int:
        """Process a single lesson to download video and subtitles."""
        print(f"[{lesson_index:2d}/{total_lessons}] Processing: {lesson_dir.name}")

        lesson_downloaded = 0
        lesson_skipped = 0
        lesson_failed = 0

        try:
            # Extract video URLs from content files
            video_urls = self.extract_video_urls_from_content_file(lesson_dir)

            if not video_urls:
                print(f"     No 720p MP4 videos found")
                return video_counter

            # Get metadata to fetch subtitles from API
            metadata = self.extract_video_metadata_from_lesson(lesson_dir)

            subtitle_urls = []
            if metadata:
                course_id = metadata['course_id']
                item_id = metadata['item_id']

                # Fetch subtitle information from API
                api_data = await self.fetch_lecture_video_api(course_id, item_id)
                if api_data:
                    subtitle_urls = self.extract_subtitle_urls_from_api(api_data)

            # Process each video
            for video_idx, video_info in enumerate(video_urls):
                video_url = video_info['url']

                # Generate base name from the video URL or lesson name
                if metadata:
                    base_name = metadata['video_name']
                    # Remove _720p.mp4 suffix if present
                    if base_name.endswith('_720p.mp4'):
                        base_name = base_name[:-9]
                else:
                    # Fallback to lesson name
                    base_name = lesson_dir.name

                # Generate sequential filenames
                video_filename = self.sanitize_sequential_video_name(video_counter, base_name, '.mp4')
                subtitle_filename = self.sanitize_sequential_video_name(video_counter, base_name, '.vtt')

                video_path = lesson_dir / video_filename
                subtitle_path = lesson_dir / subtitle_filename

                # Download video
                video_exists = video_path.exists() and video_path.stat().st_size > 1024
                if not video_exists:
                    print(f"       Downloading video: {video_filename}...", end=" ")
                    success, result = await self.download_file(video_url, video_path, 'video')

                    if success:
                        print(f"SUCCESS ({result:,} bytes)")
                        self.stats['videos']['downloaded'] += 1
                        lesson_downloaded += 1
                    else:
                        print(f"ERROR: {result}")
                        self.stats['videos']['failed'] += 1
                        lesson_failed += 1
                else:
                    print(f"       Video already exists: {video_filename}")
                    self.stats['videos']['skipped'] += 1
                    lesson_skipped += 1

                # Download English subtitles if available
                if subtitle_urls:
                    subtitle_exists = subtitle_path.exists() and subtitle_path.stat().st_size > 100
                    if not subtitle_exists:
                        # Find English subtitle
                        en_subtitle = next((sub for sub in subtitle_urls if sub['language'] == 'en'), None)

                        if en_subtitle:
                            print(f"       Downloading subtitle: {subtitle_filename}...", end=" ")
                            success, result = await self.download_file(en_subtitle['url'], subtitle_path, 'subtitle')

                            if success:
                                print(f"SUCCESS ({result:,} bytes)")
                                self.stats['subtitles']['downloaded'] += 1
                                lesson_downloaded += 1
                            else:
                                print(f"ERROR: {result}")
                                self.stats['subtitles']['failed'] += 1
                                lesson_failed += 1
                        else:
                            print(f"       No English subtitles found")
                    else:
                        print(f"       Subtitle already exists: {subtitle_filename}")
                        self.stats['subtitles']['skipped'] += 1
                        lesson_skipped += 1
                else:
                    print(f"       No subtitle data available from API")

                video_counter += 1

            if lesson_downloaded > 0 or lesson_failed > 0:
                print(f"     Lesson summary - Downloaded: {lesson_downloaded}, Skipped: {lesson_skipped}, Failed: {lesson_failed}")

        except Exception as e:
            print(f"     ERROR processing lesson: {e}")
            self.stats['videos']['failed'] += 1

        return video_counter

    async def download_course_media(self, course_name: str = "business-english-intro") -> bool:
        """Download all videos and subtitles for a course."""
        print("=" * 80)
        print("ENHANCED VIDEO AND SUBTITLE DOWNLOADER")
        print(f"Course: {course_name}")
        print("Downloads 720p videos + English subtitles with sequential naming")
        print("=" * 80)

        # Find course directory
        course_path = Path("courses") / course_name
        if not course_path.exists():
            print(f"ERROR: Course directory not found: {course_path}")
            print("Run the course scraper first to extract course structure.")
            return False

        print(f"Course directory: {course_path}")

        # Find all lesson directories and sort them
        lesson_dirs = []
        for module_dir in course_path.glob("module-*"):
            if module_dir.is_dir():
                for lesson_dir in module_dir.glob("lesson-*"):
                    if lesson_dir.is_dir():
                        lesson_dirs.append(lesson_dir)

        if not lesson_dirs:
            print("ERROR: No lesson directories found")
            return False

        # Sort lessons by module and lesson order
        sorted_lesson_dirs = self.sort_lesson_directories(lesson_dirs)

        print(f"Found {len(sorted_lesson_dirs)} lessons to process")
        print()

        # Process each lesson with sequential video counter
        video_counter = 1
        for lesson_idx, lesson_dir in enumerate(sorted_lesson_dirs, 1):
            video_counter = await self.process_lesson(lesson_dir, lesson_idx, len(sorted_lesson_dirs), video_counter)

        # Print final statistics
        print()
        print("=" * 80)
        print("DOWNLOAD COMPLETE")
        print("=" * 80)
        print(f"Course: {course_name}")
        print(f"Videos - Downloaded: {self.stats['videos']['downloaded']}, Skipped: {self.stats['videos']['skipped']}, Failed: {self.stats['videos']['failed']}")
        print(f"Subtitles - Downloaded: {self.stats['subtitles']['downloaded']}, Skipped: {self.stats['subtitles']['skipped']}, Failed: {self.stats['subtitles']['failed']}")
        print(f"Total Downloaded Size: {self.stats['total_size']:,} bytes ({self.stats['total_size'] / 1024 / 1024:.1f} MB)")
        print(f"Course directory: {course_path}")

        success = self.stats['videos']['downloaded'] > 0 or self.stats['subtitles']['downloaded'] > 0
        return success


async def main():
    """Main function to run the enhanced downloader."""
    print("Enhanced Video and Subtitle Downloader for Coursera")
    print("Downloads 720p videos + English subtitles with sequential naming")
    print()

    # Load credentials
    load_dotenv()
    cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')

    if not cauth_cookie:
        print("ERROR: COURSERA_CAUTH_COOKIE not found in .env file")
        print("Please add your Coursera CAUTH cookie to the .env file")
        return False

    try:
        async with CourseraMediaDownloader(cauth_cookie) as downloader:
            success = await downloader.download_course_media("business-english-intro")

        if success:
            print("\nSUCCESS: Downloaded videos and subtitles!")
            print("Files are named sequentially: 1_video_name.mp4, 1_video_name.vtt, etc.")
        else:
            print("\nFAILED: Could not download media files")

        return success

    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user")
        return False
    except Exception as e:
        print(f"\nERROR: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(main())