"""Enhanced video and subtitle downloader for Coursera course content."""

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


class EnhancedVideoDownloader(LoggerMixin):
    """Enhanced video and subtitle downloader with progress tracking and resume capability."""

    def __init__(
        self,
        auth: CourseraAuth,
        file_manager: FileManager,
        max_concurrent: int = 3,
        download_subtitles: bool = True,
        subtitle_language: str = 'en',
        download_supplements: bool = False,
        logger=None
    ):
        """Initialize the enhanced downloader."""
        self.auth = auth
        self.file_manager = file_manager
        self.max_concurrent = max_concurrent
        self.download_subtitles = download_subtitles
        self.subtitle_language = subtitle_language
        self.download_supplements = download_supplements
        self.console = Console()

        # Download statistics
        self.stats = {
            'videos': {'downloaded': 0, 'skipped': 0, 'failed': 0},
            'subtitles': {'downloaded': 0, 'skipped': 0, 'failed': 0},
            'supplements': {'downloaded': 0, 'skipped': 0, 'failed': 0},
            'total_size': 0
        }

        self.logger.info(f"Enhanced video downloader initialized (max concurrent: {max_concurrent}, subtitles: {download_subtitles}, supplements: {download_supplements})")

    def download_course_videos_and_subtitles(
        self,
        course_path: Path,
        target_resolution: str = '720p',
        resume: bool = False
    ) -> Optional[Dict]:
        """Download all videos, subtitles, and supplements in a course at specified resolution."""
        try:
            self.logger.info(f"Starting video, subtitle, and supplement download for course: {course_path}")

            # Discover all video files to download
            media_files = self._discover_media_files(course_path, target_resolution)

            if not media_files:
                self.console.print(f"[yellow]No {target_resolution} videos found to download[/yellow]")
                return {'videos': self.stats['videos'], 'subtitles': self.stats['subtitles'], 'supplements': self.stats['supplements']}

            self.console.print(f"[blue]Found {len(media_files)} media files to download[/blue]")

            # Filter out already downloaded files if not resuming
            if not resume:
                media_files = self._filter_existing_media_files(media_files)
                self.console.print(f"[blue]Will download {len(media_files)} new files[/blue]")

            if not media_files:
                self.console.print("[yellow]All media files already downloaded[/yellow]")
                return {'videos': self.stats['videos'], 'subtitles': self.stats['subtitles'], 'supplements': self.stats['supplements']}

            # Start download process
            return asyncio.run(self._download_media_files_async(media_files))

        except Exception as e:
            self.logger.error(f"Failed to download course media: {e}")
            raise DownloadError(f"Download failed: {e}")

    def _sort_lesson_directories(self, lesson_dirs: List[Path]) -> List[Path]:
        """Sort lesson directories by module order and then by lesson order."""
        def extract_order_numbers(lesson_path: Path):
            """Extract module and lesson order numbers from path."""
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

    def _discover_media_files(self, course_path: Path, target_resolution: str) -> List[Dict]:
        """Discover all video and subtitle files to download from lesson metadata."""
        media_files = []

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

                lesson_name = lesson_metadata.get('name', 'Unknown Lesson')

                if 'assets' in lesson_metadata:
                    # Sort assets by name to ensure consistent ordering within a lesson
                    sorted_assets = sorted(lesson_metadata['assets'],
                                         key=lambda x: x.get('name', ''))

                    for asset in sorted_assets:
                        # Look for video assets with the specific resolution and MP4 format
                        asset_name = asset.get('name', '')

                        if (asset.get('file_type') == 'video' and
                            f'_{target_resolution}.mp4' in asset_name and
                            ('url' in asset or 'local_path' in asset)):  # Accept videos with URL or already downloaded

                            # Extract metadata for subtitle fetching - try multiple sources
                            asset_metadata = asset.get('metadata', {})
                            course_id = asset_metadata.get('course_id')
                            item_id = asset_metadata.get('item_id')

                            # If not found in asset metadata, try lesson-level metadata
                            if not course_id:
                                course_id = lesson_metadata.get('metadata', {}).get('course_id')

                            if not item_id:
                                # Try to map asset to item_id using comprehensive API data
                                comprehensive_data = lesson_metadata.get('metadata', {}).get('comprehensive_api_data', {})
                                if comprehensive_data:
                                    items = comprehensive_data.get('items', {})

                                    # Look for matching video name in items
                                    for potential_item_id, item_data in items.items():
                                        if (item_data.get('is_video', False) and
                                            item_data.get('name', '').replace(' ', '_').replace(':', '_').lower() in asset_name.lower()):
                                            item_id = potential_item_id
                                            break

                                    # If no name match, try sequential mapping based on asset position
                                    if not item_id:
                                        video_assets_so_far = sum(1 for a in sorted_assets[:sorted_assets.index(asset)]
                                                                if a.get('file_type') == 'video')
                                        video_item_ids = [iid for iid, item_data in items.items()
                                                         if item_data.get('is_video', False)]
                                        if video_assets_so_far < len(video_item_ids):
                                            item_id = video_item_ids[video_assets_so_far]

                            # Create video filename
                            base_name = asset_name
                            resolution_pattern = f'_{target_resolution}.mp4'
                            if base_name.endswith(resolution_pattern):
                                base_name = base_name[:-len(resolution_pattern)]

                            video_filename = sanitize_sequential_video_name(
                                video_counter, base_name, '.mp4'
                            )
                            subtitle_filename = sanitize_sequential_video_name(
                                video_counter, base_name, '.vtt'
                            )

                            video_path = lesson_dir / video_filename
                            subtitle_path = lesson_dir / subtitle_filename

                            # Add video file if URL exists or if it's already downloaded locally
                            video_url = asset.get('url')  # May be None for already downloaded videos
                            video_exists = video_path.exists() and video_path.stat().st_size > 1024

                            if not video_exists and video_url:  # Need to download
                                media_files.append({
                                    'type': 'video',
                                    'lesson_path': lesson_dir,
                                    'lesson_name': lesson_name,
                                    'filename': video_filename,
                                    'original_filename': asset_name,
                                    'url': video_url,
                                    'local_path': video_path,
                                    'item_id': item_id,
                                    'course_id': course_id,
                                    'asset_info': asset,
                                    'sequence_number': video_counter
                                })

                            # Add subtitle file if enabled and we have course_id + item_id
                            if (self.download_subtitles and course_id and item_id and
                                not subtitle_path.exists()):
                                media_files.append({
                                    'type': 'subtitle',
                                    'lesson_path': lesson_dir,
                                    'lesson_name': lesson_name,
                                    'filename': subtitle_filename,
                                    'local_path': subtitle_path,
                                    'item_id': item_id,
                                    'course_id': course_id,
                                    'language': self.subtitle_language,
                                    'sequence_number': video_counter,
                                    'subtitle_url': None  # To be fetched from API
                                })

                            video_counter += 1
                
                # Discover supplement items if enabled
                if self.download_supplements:
                    supplement_items = self._discover_supplement_items(lesson_metadata, lesson_dir, lesson_name)
                    media_files.extend(supplement_items)

            except Exception as e:
                self.logger.warning(f"Failed to read lesson metadata from {metadata_file}: {e}")

        return media_files

    def _discover_supplement_items(self, lesson_metadata: Dict, lesson_dir: Path, lesson_name: str) -> List[Dict]:
        """Discover supplement items from lesson metadata."""
        supplement_files = []
        
        try:
            # Extract course_id from lesson metadata
            course_id = lesson_metadata.get('metadata', {}).get('course_id')
            if not course_id:
                return supplement_files
            
            # Look through comprehensive API data for supplement items
            comprehensive_data = lesson_metadata.get('metadata', {}).get('comprehensive_api_data', {})
            if not comprehensive_data:
                return supplement_files
            
            items = comprehensive_data.get('items', {})
            
            # Counter for supplements in this lesson
            supplement_counter = 1
            
            for item_id, item_data in items.items():
                # Check if this is a supplement item
                content_type = item_data.get('content_type', '')
                
                if content_type == 'supplement':
                    item_name = item_data.get('name', f'Supplement_{supplement_counter}')
                    
                    # Create filename for supplement
                    supplement_filename = sanitize_sequential_video_name(
                        supplement_counter, item_name, '.html'
                    )
                    
                    supplement_path = lesson_dir / supplement_filename
                    
                    # Always add supplement to list, let filter_existing_files handle skipped count
                    supplement_files.append({
                        'type': 'supplement',
                        'lesson_path': lesson_dir,
                        'lesson_name': lesson_name,
                        'filename': supplement_filename,
                        'original_name': item_name,
                        'local_path': supplement_path,
                        'item_id': item_id,
                        'course_id': course_id,
                        'sequence_number': supplement_counter,
                        'supplement_content': None  # To be fetched from API
                    })
                    
                    if supplement_path.exists():
                        self.logger.debug(f"Found existing supplement: {lesson_name} - {supplement_filename}")
                    else:
                        self.logger.debug(f"Found supplement to download: {lesson_name} - {supplement_filename}")
                    
                    supplement_counter += 1
        
        except Exception as e:
            self.logger.warning(f"Failed to discover supplements in lesson {lesson_name}: {e}")
        
        return supplement_files

    def _filter_existing_media_files(self, media_files: List[Dict]) -> List[Dict]:
        """Filter out files that already exist."""
        new_files = []
        for media in media_files:
            if not media['local_path'].exists():
                new_files.append(media)
            else:
                # Check file size to ensure it's not a partial download
                file_size = media['local_path'].stat().st_size
                if media['type'] == 'video' and file_size < 1024:
                    new_files.append(media)  # Re-download small video files
                elif media['type'] == 'subtitle' and file_size < 100:
                    new_files.append(media)  # Re-download small subtitle files
                elif media['type'] == 'supplement' and file_size < 100:
                    new_files.append(media)  # Re-download small supplement files
                else:
                    if media['type'] == 'video':
                        self.stats['videos']['skipped'] += 1
                    elif media['type'] == 'subtitle':
                        self.stats['subtitles']['skipped'] += 1
                    elif media['type'] == 'supplement':
                        self.stats['supplements']['skipped'] += 1

        return new_files

    async def _fetch_subtitle_url(self, course_id: str, item_id: str, language: str = 'en') -> Optional[str]:
        """Fetch subtitle URL from Coursera API."""
        try:
            # Construct API URL
            api_url = f"https://www.coursera.org/api/onDemandLectureVideos.v1/{course_id}~{item_id}"
            params = {
                'includes': 'video',
                'fields': 'onDemandVideos.v1(sources,subtitles,subtitlesVtt,subtitlesTxt,subtitlesAssetTags,dubbedSources,dubbedSubtitlesVtt,audioDescriptionVideoSources),disableSkippingForward,startMs,endMs'
            }

            headers = self.auth.get_headers(include_csrf=False)
            cookies = self.auth.get_cookies()

            timeout = aiohttp.ClientTimeout(total=30)

            async with aiohttp.ClientSession(
                headers=headers,
                cookies=cookies,
                timeout=timeout
            ) as session:
                async with session.get(api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Extract subtitle URL from response
                        if ('linked' in data and
                            'onDemandVideos.v1' in data['linked']):

                            videos = data['linked']['onDemandVideos.v1']
                            for video in videos:
                                if 'subtitlesVtt' in video:
                                    subtitles_vtt = video['subtitlesVtt']

                                    if language in subtitles_vtt:
                                        subtitle_url = subtitles_vtt[language]

                                        # Convert relative URL to full URL
                                        if subtitle_url.startswith('/api/'):
                                            subtitle_url = f"https://www.coursera.org{subtitle_url}"

                                        return subtitle_url

        except Exception as e:
            self.logger.warning(f"Failed to fetch subtitle URL for {course_id}~{item_id}: {e}")

        return None

    async def _fetch_supplement_content(self, course_id: str, item_id: str) -> Optional[str]:
        """Fetch supplement HTML content from Coursera API."""
        try:
            # Construct API URL
            api_url = f"https://www.coursera.org/api/onDemandSupplements.v1/{course_id}~{item_id}"
            params = {
                'includes': 'asset',
                'fields': 'openCourseAssets.v1(typeName),openCourseAssets.v1(definition),minimumDurationToComplete'
            }

            headers = self.auth.get_headers(include_csrf=False)
            cookies = self.auth.get_cookies()

            timeout = aiohttp.ClientTimeout(total=30)

            async with aiohttp.ClientSession(
                headers=headers,
                cookies=cookies,
                timeout=timeout
            ) as session:
                async with session.get(api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Extract HTML content from response
                        if ('linked' in data and
                            'openCourseAssets.v1' in data['linked'] and
                            len(data['linked']['openCourseAssets.v1']) > 0):

                            asset = data['linked']['openCourseAssets.v1'][0]
                            definition = asset.get('definition', {})
                            
                            # Try to get renderableHtml from renderableHtmlWithMetadata
                            renderable_html_metadata = definition.get('renderableHtmlWithMetadata', {})
                            if 'renderableHtml' in renderable_html_metadata:
                                return renderable_html_metadata['renderableHtml']
                            
                            # Fallback: try direct renderableHtml field
                            if 'renderableHtml' in definition:
                                return definition['renderableHtml']

        except Exception as e:
            self.logger.warning(f"Failed to fetch supplement content for {course_id}~{item_id}: {e}")

        return None

    async def _download_media_files_async(self, media_files: List[Dict]) -> Dict:
        """Download media files asynchronously with progress tracking."""
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
                f"Downloading {len(media_files)} media files",
                total=len(media_files)
            )

            # Create semaphore to limit concurrent downloads
            semaphore = asyncio.Semaphore(self.max_concurrent)

            # Create download tasks
            download_tasks = []
            for media in media_files:
                task = asyncio.create_task(
                    self._download_single_media_file(media, progress, main_task, semaphore)
                )
                download_tasks.append(task)

            # Wait for all downloads to complete
            await asyncio.gather(*download_tasks, return_exceptions=True)

            progress.update(main_task, description="Download completed")

        return {
            'videos': self.stats['videos'],
            'subtitles': self.stats['subtitles'],
            'supplements': self.stats['supplements']
        }

    async def _download_single_media_file(
        self,
        media: Dict,
        progress: Progress,
        main_task: TaskID,
        semaphore: asyncio.Semaphore
    ):
        """Download a single media file (video, subtitle, or supplement)."""
        async with semaphore:
            file_task = progress.add_task(
                f"  {media['type'].title()}: {media['lesson_name'][:40]}...",
                total=100
            )

            try:
                # Create lesson directory if it doesn't exist
                media['local_path'].parent.mkdir(parents=True, exist_ok=True)

                if media['type'] == 'video':
                    # Download video file
                    download_url = media['url']
                    await self._download_file(
                        url=download_url,
                        local_path=media['local_path'],
                        progress=progress,
                        task_id=file_task
                    )
                    self.stats['videos']['downloaded'] += 1
                    
                elif media['type'] == 'subtitle':
                    # Fetch subtitle URL from API and download
                    download_url = await self._fetch_subtitle_url(
                        media['course_id'],
                        media['item_id'],
                        media['language']
                    )
                    if not download_url:
                        self.logger.warning(f"Could not fetch subtitle URL for {media['filename']}")
                        self.stats['subtitles']['failed'] += 1
                        progress.update(file_task, description=f"  FAILED: No subtitle URL")
                        return
                    
                    await self._download_file(
                        url=download_url,
                        local_path=media['local_path'],
                        progress=progress,
                        task_id=file_task
                    )
                    self.stats['subtitles']['downloaded'] += 1
                    
                elif media['type'] == 'supplement':
                    # Fetch supplement HTML content from API and save
                    html_content = await self._fetch_supplement_content(
                        media['course_id'],
                        media['item_id']
                    )
                    if not html_content:
                        self.logger.warning(f"Could not fetch supplement content for {media['filename']}")
                        self.stats['supplements']['failed'] += 1
                        progress.update(file_task, description=f"  FAILED: No supplement content")
                        return
                    
                    # Save HTML content to file
                    await self._save_html_content(
                        html_content=html_content,
                        local_path=media['local_path'],
                        progress=progress,
                        task_id=file_task
                    )
                    self.stats['supplements']['downloaded'] += 1
                    
                else:
                    raise ValueError(f"Unknown media type: {media['type']}")

                progress.update(file_task, description=f"  SUCCESS: {media['type'].title()}")

            except Exception as e:
                if media['type'] == 'video':
                    self.stats['videos']['failed'] += 1
                elif media['type'] == 'subtitle':
                    self.stats['subtitles']['failed'] += 1
                elif media['type'] == 'supplement':
                    self.stats['supplements']['failed'] += 1

                self.logger.error(f"Failed to download {media['filename']}: {e}")
                progress.update(file_task, description=f"  FAILED: {media['type'].title()}")

            finally:
                progress.advance(main_task)
                progress.remove_task(file_task)

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

    async def _save_html_content(
        self,
        html_content: str,
        local_path: Path,
        progress: Progress,
        task_id: TaskID
    ):
        """Save HTML content to a file."""
        try:
            # Create temporary file
            temp_path = local_path.with_suffix('.tmp')
            
            # Write HTML content
            async with aiofiles.open(temp_path, 'w', encoding='utf-8') as file:
                await file.write(html_content)
            
            # Move temp file to final location
            temp_path.replace(local_path)
            
            # Update progress to 100%
            progress.update(task_id, completed=100)
            
            # Update total downloaded size
            self.stats['total_size'] += len(html_content.encode('utf-8'))
            
        except Exception as e:
            # Clean up temp file on error
            if temp_path.exists():
                temp_path.unlink()
            raise e