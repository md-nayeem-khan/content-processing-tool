"""File system management for course organization."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ..utils.sanitizer import (
    sanitize_course_name, sanitize_module_name,
    sanitize_lesson_name, create_safe_directory, ensure_unique_path
)
from ..utils.exceptions import FileSystemError, DirectoryCreationError, FileWriteError
from ..utils.logger import LoggerMixin
from ..core.course_models import Course, Module, Lesson, ContentAsset


class FileManager(LoggerMixin):
    """Manages file system operations for course content."""

    def __init__(self, base_output_dir: Union[str, Path] = "./courses"):
        """Initialize file manager with base output directory."""
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
        self.logger.info(f"File manager initialized with base directory: {self.base_output_dir}")

    def create_course_directory(self, course: Course) -> Path:
        """Create main directory for a course."""
        try:
            # Sanitize course name for directory
            dir_name = sanitize_course_name(course.name)
            course_path = self.base_output_dir / dir_name

            # Create directory safely
            course_path = create_safe_directory(course_path)

            # Update course with local path
            course.local_path = course_path

            self.logger.info(f"Created course directory: {course_path}")
            return course_path

        except Exception as e:
            raise DirectoryCreationError(f"Failed to create course directory for '{course.name}': {e}")

    def create_module_directory(self, module: Module, course_path: Path) -> Path:
        """Create directory for a module within a course."""
        try:
            # Sanitize module name with order
            dir_name = sanitize_module_name(module.name, module.order)
            module_path = course_path / dir_name

            # Create directory safely
            module_path = create_safe_directory(module_path)

            # Update module with local path
            module.local_path = module_path

            self.logger.debug(f"Created module directory: {module_path}")
            return module_path

        except Exception as e:
            raise DirectoryCreationError(f"Failed to create module directory for '{module.name}': {e}")

    def create_lesson_directory(self, lesson: Lesson, module_path: Path) -> Path:
        """Create directory for a lesson within a module."""
        try:
            # Sanitize lesson name with order
            dir_name = sanitize_lesson_name(lesson.name, lesson.order)
            lesson_path = module_path / dir_name

            # Create directory safely
            lesson_path = create_safe_directory(lesson_path)

            # Update lesson with local path
            lesson.local_path = lesson_path

            self.logger.debug(f"Created lesson directory: {lesson_path}")
            return lesson_path

        except Exception as e:
            raise DirectoryCreationError(f"Failed to create lesson directory for '{lesson.name}': {e}")

    def save_course_metadata(self, course: Course) -> Path:
        """Save course metadata to JSON file."""
        if not course.local_path:
            raise FileSystemError("Course local path not set")

        try:
            metadata_path = course.local_path / "course_metadata.json"

            # Prepare metadata
            metadata = {
                "id": course.id,
                "name": course.name,
                "slug": course.slug,
                "description": course.description,
                "instructor": course.instructor,
                "university": course.university,
                "language": course.language,
                "estimated_hours": course.estimated_hours,
                "total_modules": len(course.modules),
                "total_lessons": course.total_lessons,
                "total_assets": course.total_assets,
                "scraped_at": course.scraped_at.isoformat(),
                "metadata": course.metadata
            }

            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Saved course metadata: {metadata_path}")
            return metadata_path

        except Exception as e:
            raise FileWriteError(f"Failed to save course metadata: {e}")

    def save_module_metadata(self, module: Module) -> Path:
        """Save module metadata to JSON file."""
        if not module.local_path:
            raise FileSystemError("Module local path not set")

        try:
            metadata_path = module.local_path / "module_metadata.json"

            # Prepare metadata
            metadata = {
                "id": module.id,
                "name": module.name,
                "description": module.description,
                "order": module.order,
                "total_lessons": len(module.lessons),
                "metadata": module.metadata
            }

            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            self.logger.debug(f"Saved module metadata: {metadata_path}")
            return metadata_path

        except Exception as e:
            raise FileWriteError(f"Failed to save module metadata: {e}")

    def save_lesson_metadata(self, lesson: Lesson) -> Path:
        """Save lesson metadata to JSON file."""
        if not lesson.local_path:
            raise FileSystemError("Lesson local path not set")

        try:
            metadata_path = lesson.local_path / "lesson_metadata.json"

            # Prepare metadata including assets info
            assets_info = []
            for asset in lesson.assets:
                assets_info.append({
                    "name": asset.name,
                    "file_type": asset.file_type,
                    "file_size": asset.file_size,
                    "downloaded": asset.downloaded,
                    "local_path": str(asset.local_path) if asset.local_path else None
                })

            metadata = {
                "id": lesson.id,
                "name": lesson.name,
                "description": lesson.description,
                "order": lesson.order,
                "duration_minutes": lesson.duration_minutes,
                "total_assets": len(lesson.assets),
                "assets": assets_info,
                "metadata": lesson.metadata
            }

            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            self.logger.debug(f"Saved lesson metadata: {metadata_path}")
            return metadata_path

        except Exception as e:
            raise FileWriteError(f"Failed to save lesson metadata: {e}")

    def save_content_urls(self, urls: List[str], directory: Path, filename: str = "content_urls.txt") -> Path:
        """Save content URLs to a text file."""
        try:
            urls_path = directory / filename

            with open(urls_path, 'w', encoding='utf-8') as f:
                f.write(f"Content URLs - Generated: {datetime.now().isoformat()}\n")
                f.write("=" * 50 + "\n\n")

                for i, url in enumerate(urls, 1):
                    f.write(f"{i:3d}. {url}\n")

            self.logger.debug(f"Saved {len(urls)} URLs to: {urls_path}")
            return urls_path

        except Exception as e:
            raise FileWriteError(f"Failed to save content URLs: {e}")

    def create_full_structure(self, course: Course) -> Dict[str, Path]:
        """Create complete directory structure for a course."""
        paths = {}

        try:
            # Create course directory
            course_path = self.create_course_directory(course)
            paths['course'] = course_path

            # Save course metadata
            self.save_course_metadata(course)

            # Collect all URLs for the course
            all_urls = []

            # Process modules
            for module in course.modules:
                module_path = self.create_module_directory(module, course_path)
                paths[f"module_{module.id}"] = module_path

                # Save module metadata
                self.save_module_metadata(module)

                # Collect module URLs
                module_urls = []

                # Process lessons
                for lesson in module.lessons:
                    lesson_path = self.create_lesson_directory(lesson, module_path)
                    paths[f"lesson_{lesson.id}"] = lesson_path

                    # Save lesson metadata
                    self.save_lesson_metadata(lesson)

                    # Collect lesson URLs
                    lesson_urls = []
                    for asset in lesson.assets:
                        if asset.url:
                            lesson_urls.append(asset.url)
                            all_urls.append(asset.url)

                    # Save lesson URLs
                    if lesson_urls:
                        self.save_content_urls(lesson_urls, lesson_path)

                    module_urls.extend(lesson_urls)

                # Save module URLs
                if module_urls:
                    self.save_content_urls(module_urls, module_path)

            # Save all course URLs
            if all_urls:
                self.save_content_urls(all_urls, course_path)

            self.logger.info(f"Created complete structure for course '{course.name}' with {len(course.modules)} modules")
            return paths

        except Exception as e:
            self.logger.error(f"Failed to create course structure: {e}")
            raise FileSystemError(f"Failed to create course structure: {e}")

    def get_existing_course_path(self, course_name: str) -> Optional[Path]:
        """Check if course directory already exists."""
        sanitized_name = sanitize_course_name(course_name)
        potential_path = self.base_output_dir / sanitized_name

        if potential_path.exists() and potential_path.is_dir():
            return potential_path

        return None

    def cleanup_empty_directories(self, base_path: Path) -> None:
        """Remove empty directories recursively."""
        try:
            if not base_path.exists():
                return

            for item in base_path.rglob("*"):
                if item.is_dir() and not any(item.iterdir()):
                    item.rmdir()
                    self.logger.debug(f"Removed empty directory: {item}")

        except Exception as e:
            self.logger.warning(f"Failed to cleanup empty directories: {e}")

    def get_progress_file_path(self, course_path: Path) -> Path:
        """Get path for progress tracking file."""
        return course_path / ".scraping_progress.json"

    def save_progress(self, progress_data: Dict[str, Any], course_path: Path) -> None:
        """Save scraping progress to file."""
        try:
            progress_path = self.get_progress_file_path(course_path)

            with open(progress_path, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2, ensure_ascii=False)

            self.logger.debug(f"Saved progress to: {progress_path}")

        except Exception as e:
            self.logger.warning(f"Failed to save progress: {e}")

    def load_progress(self, course_path: Path) -> Optional[Dict[str, Any]]:
        """Load scraping progress from file."""
        try:
            progress_path = self.get_progress_file_path(course_path)

            if not progress_path.exists():
                return None

            with open(progress_path, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)

            self.logger.debug(f"Loaded progress from: {progress_path}")
            return progress_data

        except Exception as e:
            self.logger.warning(f"Failed to load progress: {e}")
            return None

    def download_asset(self, asset: ContentAsset, target_directory: Path, sequence_number: int = None) -> bool:
        """Download a single content asset (video, PDF, document, etc.)."""
        if not asset.url:
            self.logger.warning(f"No URL provided for asset: {asset.name}")
            return False

        try:
            import requests
            import time
            from ..utils.sanitizer import sanitize_file_name, sanitize_sequential_video_name

            target_directory.mkdir(parents=True, exist_ok=True)

            # Determine the filename based on asset type and whether sequence number is provided
            if asset.file_type == 'video' and sequence_number is not None:
                # For video files with sequence number, use sequential naming
                base_name = asset.name

                # Remove resolution pattern if present (e.g., _720p.mp4)
                resolution_patterns = ['_720p.mp4', '_480p.mp4', '_1080p.mp4', '_360p.mp4']
                for pattern in resolution_patterns:
                    if base_name.endswith(pattern):
                        base_name = base_name[:-len(pattern)]
                        break

                # Create sequential filename
                safe_filename = sanitize_sequential_video_name(sequence_number, base_name, '.mp4')
            else:
                # For non-video files or videos without sequence number, use regular naming
                safe_filename = sanitize_file_name(asset.name)

                # Add file extension if not present based on asset type
                # Special handling for video files to avoid .mp4.video extensions
                if asset.file_type == 'video':
                    # For video files, ensure they end with .mp4 (not .video)
                    if not safe_filename.lower().endswith('.mp4'):
                        # Remove any existing extension and add .mp4
                        if '.' in safe_filename:
                            safe_filename = safe_filename.rsplit('.', 1)[0]
                        safe_filename = f"{safe_filename}.mp4"
                elif asset.file_type and not safe_filename.lower().endswith(f'.{asset.file_type}'):
                    safe_filename = f"{safe_filename}.{asset.file_type}"

            file_path = target_directory / safe_filename

            # Skip if file already exists
            if file_path.exists():
                self.logger.info(f"File already exists: {file_path}")
                asset.local_path = file_path
                asset.downloaded = True
                return True

            # Download with authentication headers
            headers = {
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
                'sec-fetch-site': 'same-origin'
            }

            self.logger.info(f"Downloading: {asset.name} -> {file_path}")

            # Make download request with timeout and retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        asset.url,
                        headers=headers,
                        stream=True,
                        timeout=(10, 60),  # Connect timeout, read timeout
                        allow_redirects=True
                    )
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"Download attempt {attempt + 1} failed for {asset.name}: {e}. Retrying...")
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        raise

            # Get file size
            total_size = int(response.headers.get('content-length', 0))

            # Download in chunks with progress tracking
            downloaded_size = 0
            chunk_size = 8192

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)

            # Update asset metadata
            asset.local_path = file_path
            asset.file_size = downloaded_size
            asset.downloaded = True

            self.logger.info(f"Successfully downloaded: {asset.name} ({downloaded_size} bytes)")
            return True

        except Exception as e:
            self.logger.error(f"Failed to download {asset.name}: {e}")
            # Clean up partial download
            if 'file_path' in locals() and file_path.exists():
                try:
                    file_path.unlink()
                except:
                    pass
            return False