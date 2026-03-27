#!/usr/bin/env python3
"""
Enhanced Video Downloader: Downloads ALL videos from each lesson.
Fixes the bug where only 1 video per lesson was downloaded.
Now handles multiple lecture videos per lesson properly!
"""

import os
import json
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from dotenv import load_dotenv
import re
from rich.console import Console
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TimeRemainingColumn

console = Console()

class EnhancedVideoDownloader:
    def __init__(self, course_name="introduction-to-business-english-communication-course"):
        self.course_name = course_name
        self.course_path = Path("courses") / course_name
        self.stats = {'downloaded': 0, 'skipped': 0, 'failed': 0, 'total_size': 0}

        # Load authentication
        load_dotenv()
        self.cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')

    async def download_all_videos(self):
        """Download ALL videos from all lessons."""
        console.print("[bold green]Enhanced Video Downloader[/bold green]")
        console.print("Downloads ALL videos from each lesson!")
        console.print(f"Course: {self.course_name}")
        console.print("=" * 80)

        if not self.cauth_cookie:
            console.print("[red]ERROR: COURSERA_CAUTH_COOKIE not found in .env file[/red]")
            return False

        if not self.course_path.exists():
            console.print(f"[red]ERROR: Course directory not found: {self.course_path}[/red]")
            return False

        # Find all lesson directories
        lesson_dirs = []
        for module_dir in self.course_path.glob("module-*"):
            if module_dir.is_dir():
                for lesson_dir in module_dir.glob("lesson-*"):
                    if lesson_dir.is_dir():
                        lesson_dirs.append(lesson_dir)

        console.print(f"Found {len(lesson_dirs)} lesson directories")

        # Process each lesson
        total_videos_to_download = 0
        video_tasks = []

        for lesson_dir in lesson_dirs:
            lesson_videos = self.discover_lesson_videos(lesson_dir)
            total_videos_to_download += len(lesson_videos)
            video_tasks.extend(lesson_videos)

        if not video_tasks:
            console.print("[yellow]No videos to download[/yellow]")
            return True

        console.print(f"Found {total_videos_to_download} videos to download")
        console.print()

        # Download all videos with progress tracking
        return await self.download_videos_async(video_tasks)

    def discover_lesson_videos(self, lesson_dir):
        """Discover all videos in a lesson from content_urls.txt."""
        content_urls_file = lesson_dir / "content_urls.txt"
        lesson_videos = []

        if not content_urls_file.exists():
            return lesson_videos

        try:
            with open(content_urls_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse all 720p MP4 URLs (one per video asset)
            lines = content.split('\n')
            current_asset = None

            for line in lines:
                # Look for video asset headers
                if line.startswith('# Video Asset:'):
                    # Extract asset name from "# Video Asset: video_DKbsC (Lecture ID: DKbsC)"
                    asset_match = re.search(r'Video Asset: (video_\w+)', line)
                    if asset_match:
                        current_asset = asset_match.group(1)

                # Look for 720p MP4 URLs
                elif '720p MP4' in line and current_asset:
                    url_start = line.find('https://')
                    if url_start != -1:
                        url = line[url_start:].strip()
                        filename = f"{current_asset}_720p.mp4"
                        local_path = lesson_dir / filename

                        lesson_videos.append({
                            'lesson_dir': lesson_dir,
                            'lesson_name': lesson_dir.name,
                            'asset_name': current_asset,
                            'filename': filename,
                            'url': url,
                            'local_path': local_path
                        })

                        # Reset current asset to avoid duplicates
                        current_asset = None

        except Exception as e:
            console.print(f"[red]Error reading URLs from {lesson_dir.name}: {e}[/red]")

        return lesson_videos

    async def download_videos_async(self, video_tasks):
        """Download all videos asynchronously with progress tracking."""
        # Filter out already downloaded videos
        new_video_tasks = []
        for video in video_tasks:
            if not video['local_path'].exists():
                new_video_tasks.append(video)
            else:
                self.stats['skipped'] += 1

        if not new_video_tasks:
            console.print("[yellow]All videos already downloaded[/yellow]")
            return True

        console.print(f"Downloading {len(new_video_tasks)} new videos (skipping {self.stats['skipped']} existing)")

        # Create download progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=False
        ) as progress:

            # Create main progress task
            main_task = progress.add_task(
                f"Downloading {len(new_video_tasks)} videos",
                total=len(new_video_tasks)
            )

            # Create semaphore to limit concurrent downloads
            semaphore = asyncio.Semaphore(3)  # Max 3 concurrent downloads

            # Create download tasks
            download_tasks = []
            for video in new_video_tasks:
                task = asyncio.create_task(
                    self.download_single_video(video, progress, main_task, semaphore)
                )
                download_tasks.append(task)

            # Wait for all downloads to complete
            await asyncio.gather(*download_tasks, return_exceptions=True)

            progress.update(main_task, description="Download completed")

        # Print results
        console.print()
        console.print(f"[green]SUCCESS: Downloaded {self.stats['downloaded']} videos[/green]")
        console.print(f"[blue]Skipped: {self.stats['skipped']} | Failed: {self.stats['failed']}[/blue]")
        console.print(f"Total size: {self.stats['total_size'] / 1024 / 1024:.1f} MB")

        return True

    async def download_single_video(self, video, progress, main_task, semaphore):
        """Download a single video file."""
        async with semaphore:
            video_task = progress.add_task(
                f"  {video['asset_name']}...",
                total=100
            )

            try:
                # Create lesson directory if it doesn't exist
                video['local_path'].parent.mkdir(parents=True, exist_ok=True)

                # Download the file
                await self.download_file(
                    url=video['url'],
                    local_path=video['local_path'],
                    progress=progress,
                    task_id=video_task
                )

                self.stats['downloaded'] += 1
                progress.update(video_task, description=f"  OK: {video['asset_name']}")

            except Exception as e:
                self.stats['failed'] += 1
                console.print(f"[red]Failed to download {video['filename']}: {e}[/red]")
                progress.update(video_task, description=f"  FAILED: {video['asset_name']}")

            finally:
                progress.advance(main_task)
                progress.remove_task(video_task)

    async def download_file(self, url, local_path, progress, task_id):
        """Download a file from URL with progress tracking."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        cookies = {'CAUTH': self.cauth_cookie}

        timeout = aiohttp.ClientTimeout(total=30 * 60)  # 30 minute timeout

        async with aiohttp.ClientSession(
            headers=headers,
            cookies=cookies,
            timeout=timeout
        ) as session:

            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: {url}")

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


async def main():
    """Main function to run enhanced video downloader."""
    try:
        downloader = EnhancedVideoDownloader()
        success = await downloader.download_all_videos()

        if not success:
            console.print("[red]Download failed[/red]")
            return False

        return True

    except KeyboardInterrupt:
        console.print("\n[yellow]Download interrupted by user[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]ERROR: {e}[/red]")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        exit(1)