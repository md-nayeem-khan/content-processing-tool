"""Video downloader for Coursera course content."""

import os
import json
import re
import time
import asyncio
import aiohttp
import aiofiles
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TimeRemainingColumn

from .auth import CourseraAuth
from ..core.file_manager import FileManager
from ..utils.exceptions import DownloadError
from ..utils.logger import LoggerMixin
from ..utils.sanitizer import sanitize_sequential_video_name


class VideoDownloader(LoggerMixin):
    """Video downloader with progress tracking and resume capability."""

    def __init__(
        self,
        auth: CourseraAuth,
        file_manager: FileManager,
        max_concurrent: int = 3,
        logger=None
    ):
        """Initialize the video downloader."""
        self.auth = auth
        self.file_manager = file_manager
        self.max_concurrent = max_concurrent
        self.console = Console()

        # Download statistics
        self.stats = {
            'downloaded': 0,
            'skipped': 0,
            'failed': 0,
            'total_size': 0
        }

        self.logger.info(f"Video downloader initialized (max concurrent: {max_concurrent})")

    def download_course_videos(
        self,
        course_path: Path,
        target_resolution: str = '720p',
        resume: bool = False
    ) -> Optional[Dict]:
        """Download all videos in a course at specified resolution."""
        try:
            self.logger.info(f"Starting video download for course: {course_path}")

            # Discover all video files to download
            video_files = self._discover_video_files(course_path, target_resolution)

            if not video_files:
                self.console.print(f"[yellow]No {target_resolution} videos found to download[/yellow]")
                return {'downloaded': 0, 'skipped': 0, 'failed': 0}

            self.console.print(f"[blue]Found {len(video_files)} videos to download[/blue]")

            # Filter out already downloaded files if not resuming
            if not resume:
                video_files = self._filter_existing_files(video_files)
                self.console.print(f"[blue]Will download {len(video_files)} new videos[/blue]")

            if not video_files:
                self.console.print("[yellow]All videos already downloaded[/yellow]")
                return {'downloaded': 0, 'skipped': len(video_files), 'failed': 0}

            # Start download process
            return asyncio.run(self._download_videos_async(video_files))

        except Exception as e:
            self.logger.error(f"Failed to download course videos: {e}")
            raise DownloadError(f"Download failed: {e}")

    def _sort_lesson_directories(self, lesson_dirs: List[Path]) -> List[Path]:
        """Sort lesson directories by module order and then by lesson order."""
        def extract_order_numbers(lesson_path: Path):
            """Extract module and lesson order numbers from path."""
            # Extract module number from path like: .../module-01-name/lesson-02-name
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

        # Sort by module order first, then by lesson order
        return sorted(lesson_dirs, key=extract_order_numbers)

    def _discover_video_files(self, course_path: Path, target_resolution: str) -> List[Dict]:
        """Discover all video files to download from lesson metadata."""
        video_files = []

        # Get all lesson directories and sort them by module and lesson order
        lesson_dirs = [d for d in course_path.rglob("lesson-*") if d.is_dir()]
        sorted_lesson_dirs = self._sort_lesson_directories(lesson_dirs)

        video_counter = 1  # Global sequential counter for all videos

        for lesson_dir in sorted_lesson_dirs:
            metadata_file = lesson_dir / "lesson_metadata.json"
            if not metadata_file.exists():
                continue

            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    lesson_metadata = json.load(f)

                # Find all video assets with target resolution and MP4 format
                lesson_name = lesson_metadata.get('name', 'Unknown Lesson')

                if 'assets' in lesson_metadata:
                    # Sort assets by name to ensure consistent ordering within a lesson
                    sorted_assets = sorted(lesson_metadata['assets'],
                                         key=lambda x: x.get('name', ''))

                    for asset in sorted_assets:
                        # Look for video assets with the specific resolution and MP4 format
                        asset_name = asset.get('name', '')

                        # Check if this is a video asset with target resolution and MP4 format
                        if (asset.get('file_type') == 'video' and
                            f'_{target_resolution}.mp4' in asset_name and
                            'url' in asset):

                            # Create properly sanitized sequential filename
                            # Extract resolution and create extension
                            extension = '.mp4'

                            # Remove resolution suffix for cleaner naming
                            base_name = asset_name
                            resolution_pattern = f'_{target_resolution}.mp4'
                            if base_name.endswith(resolution_pattern):
                                base_name = base_name[:-len(resolution_pattern)]

                            # Create sequential filename with proper sanitization
                            sequential_filename = sanitize_sequential_video_name(
                                video_counter,
                                base_name,
                                extension
                            )

                            target_local_path = lesson_dir / sequential_filename

                            # Only add if the actual video file doesn't exist
                            if not target_local_path.exists():
                                video_files.append({
                                    'lesson_path': lesson_dir,
                                    'lesson_name': lesson_name,
                                    'filename': sequential_filename,
                                    'original_filename': asset_name,
                                    'url': asset['url'],
                                    'local_path': target_local_path,
                                    'item_id': asset.get('metadata', {}).get('item_id', 'unknown'),
                                    'asset_info': asset,
                                    'sequence_number': video_counter
                                })
                                self.logger.debug(f"Found video to download: {lesson_name} - {sequential_filename}")

                            video_counter += 1

            except Exception as e:
                self.logger.warning(f"Failed to read lesson metadata from {metadata_file}: {e}")

        return video_files

    def _get_video_url(self, lesson_dir: Path, target_resolution: str) -> Optional[str]:
        """Extract video URL from content_urls.txt file for specific resolution."""
        content_urls_file = lesson_dir / "content_urls.txt"
        if not content_urls_file.exists():
            return None

        try:
            with open(content_urls_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for lines containing target resolution MP4 URLs
            lines = content.split('\n')
            for line in lines:
                # Look for lines with cloudfront URLs containing the target resolution
                if ('cloudfront.net' in line and
                    f'/{target_resolution}/' in line and
                    'index.mp4?' in line):

                    # Extract URL (should be after the line number)
                    url_start = line.find('https://')
                    if url_start != -1:
                        url = line[url_start:].strip()
                        self.logger.debug(f"Found {target_resolution} URL: {url[:100]}...")
                        return url

        except Exception as e:
            self.logger.warning(f"Failed to read content URLs from {content_urls_file}: {e}")

        return None

    def _filter_existing_files(self, video_files: List[Dict]) -> List[Dict]:
        """Filter out files that already exist."""
        new_files = []
        for video in video_files:
            if not video['local_path'].exists():
                new_files.append(video)
            else:
                self.stats['skipped'] += 1

        return new_files

    async def _download_videos_async(self, video_files: List[Dict]) -> Dict:
        """Download videos asynchronously with progress tracking."""
        # Create download progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TimeRemainingColumn(),
            console=self.console,
            transient=False
        ) as progress:

            # Create main progress task
            main_task = progress.add_task(
                f"Downloading {len(video_files)} videos",
                total=len(video_files)
            )

            # Create semaphore to limit concurrent downloads
            semaphore = asyncio.Semaphore(self.max_concurrent)

            # Create download tasks
            download_tasks = []
            for video in video_files:
                task = asyncio.create_task(
                    self._download_single_video(video, progress, main_task, semaphore)
                )
                download_tasks.append(task)

            # Wait for all downloads to complete
            await asyncio.gather(*download_tasks, return_exceptions=True)

            progress.update(main_task, description="Download completed")

        return {
            'downloaded': self.stats['downloaded'],
            'skipped': self.stats['skipped'],
            'failed': self.stats['failed']
        }

    async def _download_single_video(
        self,
        video: Dict,
        progress: Progress,
        main_task: TaskID,
        semaphore: asyncio.Semaphore
    ):
        """Download a single video file."""
        async with semaphore:
            video_task = progress.add_task(
                f"  {video['lesson_name'][:50]}...",
                total=100
            )

            try:
                # Create lesson directory if it doesn't exist
                video['local_path'].parent.mkdir(parents=True, exist_ok=True)

                # Download the file
                await self._download_file(
                    url=video['url'],
                    local_path=video['local_path'],
                    progress=progress,
                    task_id=video_task
                )

                self.stats['downloaded'] += 1
                progress.update(video_task, description=f"  SUCCESS: {video['lesson_name'][:40]}")

            except Exception as e:
                self.stats['failed'] += 1
                self.logger.error(f"Failed to download {video['filename']}: {e}")
                progress.update(video_task, description=f"  FAILED: {video['lesson_name'][:40]}")

            finally:
                progress.advance(main_task)
                progress.remove_task(video_task)

    async def _download_file(
        self,
        url: str,
        local_path: Path,
        progress: Progress,
        task_id: TaskID
    ):
        """Download a file from URL with progress tracking."""
        headers = self.auth.get_headers(include_csrf=False)
        cookies = self.auth.get_cookies()

        timeout = aiohttp.ClientTimeout(total=30 * 60)  # 30 minute timeout

        async with aiohttp.ClientSession(
            headers=headers,
            cookies=cookies,
            timeout=timeout
        ) as session:

            async with session.get(url) as response:
                if response.status != 200:
                    raise DownloadError(f"HTTP {response.status}: {url}")

                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0

                # Create temporary file
                temp_path = local_path.with_suffix('.tmp')

                try:
                    async with aiofiles.open(temp_path, 'wb') as file:
                        async for chunk in response.content.iter_chunked(8192):
                            await file.write(chunk)
                            downloaded_size += len(chunk)

                            # Update progress
                            if total_size > 0:
                                percentage = (downloaded_size / total_size) * 100
                                progress.update(task_id, completed=percentage)

                    # Move temp file to final location
                    temp_path.replace(local_path)

                    # Update total downloaded size
                    self.stats['total_size'] += downloaded_size

                except Exception as e:
                    # Clean up temp file on error
                    if temp_path.exists():
                        temp_path.unlink()
                    raise e