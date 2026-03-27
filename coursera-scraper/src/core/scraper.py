"""Core scraping orchestration logic."""

import asyncio
import time
import re
import requests
from typing import Optional, List, Dict, Any
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn

from .course_models import (
    Course, Module, Lesson, ContentAsset, ScrapingProgress,
    ComprehensiveCourseData, CourseraModule, CourseraLesson,
    CourseraContentItem, ContentSummary, ComprehensiveCourseConverter
)
from .file_manager import FileManager
from ..api.coursera_client import CourseraClient, ResponseParser
from ..config.settings import ConfigManager
from ..utils.exceptions import (
    CourseraScraperError, APIError, CourseNotFoundError,
    FileSystemError, ValidationError
)
from ..utils.logger import LoggerMixin
from ..utils.sanitizer import get_file_extension, sanitize_file_name


# Content type constants to avoid stringly-typed code
class ContentType:
    VIDEO = 'video'
    READING = 'reading'
    SUPPLEMENT = 'supplement'
    ASSIGNMENT = 'assignment'

class CourseraContentType:
    """Content types from Coursera comprehensive API."""
    LECTURE = 'lecture'
    SUPPLEMENT = 'supplement'
    UNGRADED_ASSIGNMENT = 'ungradedAssignment'
    DISCUSSION_PROMPT = 'discussionPrompt'
    PHASED_PEER = 'phasedPeer'
    STAFF_GRADED = 'staffGraded'
    GRADED_LTI = 'gradedLti'

class ExcludedContentType:
    QUIZ = 'quiz'
    DISCUSSION = 'discussion'
    PEER = 'peer'
    EXAM = 'exam'
    GRADED_LTI = 'gradedLti'

class ContentTypeMapper:
    """Maps Coursera API content types to our internal types."""

    DOWNLOADABLE_TYPES = {
        CourseraContentType.LECTURE,
        CourseraContentType.SUPPLEMENT,
        CourseraContentType.UNGRADED_ASSIGNMENT,
        CourseraContentType.STAFF_GRADED,
    }

    VIDEO_TYPES = {
        CourseraContentType.LECTURE
    }

    READING_TYPES = {
        CourseraContentType.SUPPLEMENT
    }

    ASSIGNMENT_TYPES = {
        CourseraContentType.UNGRADED_ASSIGNMENT,
        CourseraContentType.STAFF_GRADED,
        CourseraContentType.PHASED_PEER
    }

    # Content types to skip (not downloadable or not content)
    EXCLUDED_TYPES = {
        CourseraContentType.DISCUSSION_PROMPT,
        ExcludedContentType.QUIZ,
        ExcludedContentType.DISCUSSION,
        ExcludedContentType.EXAM,
        ExcludedContentType.GRADED_LTI
    }

    @classmethod
    def is_downloadable(cls, content_type: str) -> bool:
        """Check if content type is downloadable."""
        return content_type in cls.DOWNLOADABLE_TYPES

    @classmethod
    def is_video(cls, content_type: str) -> bool:
        """Check if content type is a video."""
        return content_type in cls.VIDEO_TYPES

    @classmethod
    def is_reading(cls, content_type: str) -> bool:
        """Check if content type is reading material."""
        return content_type in cls.READING_TYPES

    @classmethod
    def is_assignment(cls, content_type: str) -> bool:
        """Check if content type is an assignment."""
        return content_type in cls.ASSIGNMENT_TYPES

    @classmethod
    def should_skip(cls, content_type: str) -> bool:
        """Check if content type should be skipped."""
        return content_type in cls.EXCLUDED_TYPES

    @classmethod
    def map_to_internal_type(cls, coursera_type: str) -> str:
        """Map Coursera content type to internal type."""
        if cls.is_video(coursera_type):
            return ContentType.VIDEO
        elif cls.is_reading(coursera_type):
            return ContentType.READING
        elif cls.is_assignment(coursera_type):
            return ContentType.ASSIGNMENT
        else:
            return ContentType.SUPPLEMENT


class CourseScraper(LoggerMixin):
    """Main course scraping orchestrator."""

    def __init__(
        self,
        client: CourseraClient,
        file_manager: FileManager,
        config: ConfigManager,
        logger=None
    ):
        """Initialize the course scraper."""
        self.client = client
        self.file_manager = file_manager
        self.config = config
        self.console = Console()

        # Initialize response parser
        self.parser = ResponseParser(client.api_config)

        # Progress tracking
        self.current_progress: Optional[ScrapingProgress] = None
        self.video_sequence_counter = 1  # Global counter for video sequential naming

        self.logger.info("Course scraper initialized")

    def scrape_course(self, course_identifier: str) -> Optional[Course]:
        """Main method to scrape a complete course."""
        try:
            self.logger.info(f"Starting to scrape course: {course_identifier}")

            # Step 1: Create course structure using working API approach
            with self.console.status("[blue]Setting up course structure...[/blue]"):
                course = self._create_course_from_working_api(course_identifier)

            if not course:
                self.console.print(f"[red]Unable to create course structure: {course_identifier}[/red]")
                return None

            self.console.print(f"[green]SUCCESS: Set up course: {course.name}[/green]")

            # Check if course already exists
            existing_path = self.file_manager.get_existing_course_path(course.name)
            if existing_path:
                self.console.print(f"[yellow]Course directory already exists: {existing_path}[/yellow]")
                # Load existing progress if available
                progress_data = self.file_manager.load_progress(existing_path)
                if progress_data and not progress_data.get('is_complete', False):
                    self.console.print("[blue]Resuming incomplete scraping...[/blue]")

            # Initialize progress tracking
            self.current_progress = ScrapingProgress(
                course_id=course.id,
                course_name=course.name
            )

            # Reset video sequence counter for this course
            self.video_sequence_counter = 1

            # Step 2: Create course directory structure
            course_paths = self.file_manager.create_course_directory(course)

            # Step 3: Scrape modules with progress tracking
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                console=self.console,
                transient=False
            ) as progress:

                main_task = progress.add_task(
                    f"Scraping course: {course.name}",
                    total=len(course.modules) if course.modules else 1
                )

                for i, module in enumerate(course.modules or []):
                    progress.update(main_task, description=f"Processing module: {module.name}")

                    # Create module directory and scrape content
                    module_path = self.file_manager.create_module_directory(module, course_paths)
                    self._scrape_module(module, progress, main_task)

                    # Update progress
                    progress.advance(main_task)
                    self.current_progress.completed_modules += 1
                    # Save progress with datetime handling
                    progress_dict = self.current_progress.dict()
                    progress_dict['start_time'] = progress_dict['start_time'].isoformat()
                    progress_dict['last_update'] = progress_dict['last_update'].isoformat()
                    self.file_manager.save_progress(progress_dict, course_paths)

                progress.update(main_task, description="COMPLETE: Course scraping completed")

            # Step 4: Create complete file structure
            self.file_manager.create_full_structure(course)

            # Mark as complete
            self.current_progress.is_complete = True
            self.current_progress.last_update = datetime.now()
            # Save final progress with datetime handling
            progress_dict = self.current_progress.dict()
            progress_dict['start_time'] = progress_dict['start_time'].isoformat()
            progress_dict['last_update'] = progress_dict['last_update'].isoformat()
            self.file_manager.save_progress(progress_dict, course_paths)

            self.logger.info(f"Successfully scraped course: {course.name}")
            return course

        except CourseNotFoundError as e:
            self.console.print(f"[red]Course not found: {e}[/red]")
            return None

        except Exception as e:
            self.logger.exception(f"Failed to scrape course {course_identifier}")
            self.console.print(f"[red]Error scraping course: {e}[/red]")
            return None

    def _discover_course_dynamically(self, course_identifier: str) -> Optional[Dict]:
        """Dynamically discover course structure for any course name."""
        try:
            self.console.print(f"[blue]Discovering course structure for: {course_identifier}[/blue]")

            # Get authentication headers and cookies
            headers = self.client.auth.get_headers(include_csrf=False)
            # Convert to standard headers format for requests
            request_headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'User-Agent': headers.get('User-Agent', ''),
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            cookies = self.client.auth.get_cookies()

            # Try different possible course URL patterns
            possible_urls = [
                f"https://www.coursera.org/learn/{course_identifier}",
                f"https://www.coursera.org/learn/{course_identifier}-intro",
                f"https://www.coursera.org/learn/{course_identifier}-course",
                f"https://www.coursera.org/learn/{course_identifier.replace('-', '_')}"
            ]

            course_id = None
            found_course_url = None
            html_content = None

            # Try to find the course
            for course_url in possible_urls:
                try:
                    self.console.print(f"  Trying: {course_url}")
                    response = requests.get(course_url, headers=request_headers, cookies=cookies)

                    if response.status_code == 200:
                        self.console.print(f"  SUCCESS: Found course at {course_url}")
                        found_course_url = course_url
                        html_content = response.text

                        # Extract course ID from HTML
                        course_id_patterns = [
                            r'course["\']:\s*["\']([\w~-]+)["\']',
                            r'courseId["\']:\s*["\']([\w~-]+)["\']',
                            r'"id":\s*"([\w~-]{20,})"',
                        ]

                        for pattern in course_id_patterns:
                            matches = re.findall(pattern, html_content)
                            for match in matches:
                                if len(match) > 15:  # Course IDs are typically long
                                    course_id = match
                                    self.console.print(f"  Found course ID: {course_id}")
                                    break
                            if course_id:
                                break

                        if course_id:
                            break
                    elif response.status_code == 404:
                        self.console.print(f"  Course not found at this URL")
                    else:
                        self.console.print(f"  HTTP {response.status_code}")

                except Exception as e:
                    self.console.print(f"  Error accessing {course_url}: {e}")
                    continue

            if not found_course_url or not course_id:
                self.console.print(f"[red]Could not find course: {course_identifier}[/red]")
                return None

            if not html_content:
                self.console.print("[red]No HTML content retrieved[/red]")
                return None

            # Extract content IDs with smart filtering - prioritize video content
            self.console.print("[blue]Extracting content IDs with smart filtering...[/blue]")

            # Primary patterns for video content (most reliable)
            video_patterns = [
                r'lectureId["\']:\s*["\']([\w_]+)["\']',
                r'onDemandLectureVideos["\']:\s*["\']([\w_]+)["\']',
                r'"id":\s*"([\w_]{5,8})"',
            ]

            # Extract video content IDs first (highest success rate)
            video_content_ids = set()
            for pattern in video_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    if 5 <= len(match) <= 8 and match.replace('_', '').isalnum():
                        video_content_ids.add(match)

            # Also look for other content types but limit extraction
            other_patterns = [
                r'readingId["\']:\s*["\']([\w_]+)["\']',
                r'supplementId["\']:\s*["\']([\w_]+)["\']',
            ]
            other_content_ids = set()
            for pattern in other_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)[:10]  # Limit to first 10 matches
                for match in matches:
                    if 4 <= len(match) <= 8 and match.replace('_', '').isalnum():
                        other_content_ids.add(match)

            total_content_ids = len(video_content_ids) + len(other_content_ids)
            self.console.print(f"  Found {len(video_content_ids)} video IDs, {len(other_content_ids)} other content IDs")

            # Test content efficiently - prioritize videos
            self.console.print("[blue]Testing content with smart prioritization...[/blue]")
            api_headers = self.client.auth.get_headers(include_csrf=False)
            api_cookies = self.client.auth.get_cookies()

            valid_content_items = []
            course_name = None

            # Optimized API testing strategy
            def test_video_content(content_ids: set) -> List[Dict]:
                """Test video content IDs efficiently."""
                video_results = []
                video_url_template = "https://www.coursera.org/api/onDemandLectureVideos.v1/{course_id}~{item_id}?includes=video&fields=onDemandVideos.v1(sources%2Csubtitles%2CsubtitlesVtt%2CsubtitlesTxt%2CsubtitlesAssetTags%2CdubbedSources%2CdubbedSubtitlesVtt%2CaudioDescriptionVideoSources)%2CdisableSkippingForward%2CstartMs%2CendMs"

                for i, item_id in enumerate(sorted(content_ids), 1):
                    print(f"  [{i:3d}/{len(content_ids)}] Testing video {item_id}...", end=' ')

                    try:
                        test_url = video_url_template.format(course_id=course_id, item_id=item_id)
                        response = requests.get(test_url, headers=api_headers, cookies=api_cookies)

                        if response.status_code == 200:
                            try:
                                data = response.json()
                                if self._is_valid_video_content(data):
                                    video_results.append({
                                        'item_id': item_id,
                                        'content_type': ContentType.VIDEO,
                                        'endpoint': 'video',
                                        'data': data,
                                        'url': test_url
                                    })
                                    print(f"SUCCESS! VIDEO")
                                else:
                                    print("No video data")
                            except ValueError:  # JSON decode error
                                print("Invalid JSON")
                        elif response.status_code == 404:
                            print("Not found")
                        else:
                            print(f"HTTP {response.status_code}")

                    except Exception as e:
                        print(f"Error: {e}")

                return video_results

            def test_other_content(content_ids: set) -> List[Dict]:
                """Test other content types but limit scope."""
                other_results = []

                # Only test reading endpoint for other content (most likely to succeed)
                reading_url_template = "https://www.coursera.org/api/onDemandLectureReadings.v1/{course_id}~{item_id}?includes=reading&fields=onDemandReadings.v1(url%2Ctitle%2Cdescription%2CreadingType)"

                # Limit to first 10 to avoid excessive API calls
                limited_ids = sorted(content_ids)[:10]
                for i, item_id in enumerate(limited_ids, 1):
                    print(f"  [R{i:2d}/{len(limited_ids)}] Testing reading {item_id}...", end=' ')

                    try:
                        test_url = reading_url_template.format(course_id=course_id, item_id=item_id)
                        response = requests.get(test_url, headers=api_headers, cookies=api_cookies)

                        if response.status_code == 200:
                            try:
                                data = response.json()
                                if self._is_valid_reading_content(data):
                                    other_results.append({
                                        'item_id': item_id,
                                        'content_type': ContentType.READING,
                                        'endpoint': 'reading',
                                        'data': data,
                                        'url': test_url
                                    })
                                    print(f"SUCCESS! READING")
                                else:
                                    print("No reading data")
                            except ValueError:
                                print("Invalid JSON")
                        elif response.status_code == 404:
                            print("Not found")
                        else:
                            print(f"HTTP {response.status_code}")

                    except Exception as e:
                        print(f"Error: {e}")

                return other_results

            # Test video content first (highest priority)
            video_items = test_video_content(video_content_ids)
            valid_content_items.extend(video_items)

            # Extract course name from first successful video response
            if video_items and not course_name:
                course_name = self._extract_course_name(video_items[0]['data'], course_identifier)

            # Test other content types if we found videos (indicates active course)
            if video_items and other_content_ids:
                other_items = test_other_content(other_content_ids)
                valid_content_items.extend(other_items)

            if not valid_content_items:
                self.console.print(f"[red]No valid content found for course: {course_identifier}[/red]")
                return None

            self.console.print(f"[green]Successfully discovered {len(valid_content_items)} content items[/green]")

            # Group content items by type for reporting
            content_by_type = {}
            for item in valid_content_items:
                content_type = item['content_type']
                if content_type not in content_by_type:
                    content_by_type[content_type] = []
                content_by_type[content_type].append(item)

            for content_type, items in content_by_type.items():
                self.console.print(f"  - {len(items)} {content_type} items")

            # Infer course name if not found
            if not course_name:
                course_name = course_identifier.replace('-', ' ').title()

            return {
                'course_id': course_id,
                'course_name': course_name,
                'course_url': found_course_url,
                'valid_content_items': valid_content_items,
                'content_by_type': content_by_type
            }

        except Exception as e:
            self.logger.error(f"Failed to discover course dynamically: {e}")
            return None

    def _is_valid_video_content(self, data: Dict) -> bool:
        """Check if response contains valid video content."""
        try:
            if 'linked' not in data or 'onDemandVideos.v1' not in data['linked']:
                return False
            video_data = data['linked']['onDemandVideos.v1']
            return len(video_data) > 0 and 'sources' in video_data[0]
        except Exception:
            return False

    def _is_valid_reading_content(self, data: Dict) -> bool:
        """Check if response contains valid reading content."""
        try:
            if 'linked' not in data or 'onDemandReadings.v1' not in data['linked']:
                return False
            reading_data = data['linked']['onDemandReadings.v1']
            return len(reading_data) > 0 and 'url' in reading_data[0]
        except Exception:
            return False

    def _extract_course_name(self, data: Dict, fallback_name: str) -> str:
        """Extract course name from API response."""
        try:
            # Try various places where course name might be stored
            if 'elements' in data and data['elements']:
                element = data['elements'][0]
                if 'course' in element and isinstance(element['course'], dict):
                    return element['course'].get('name', fallback_name.replace('-', ' ').title())

            return fallback_name.replace('-', ' ').title()
        except Exception:
            return fallback_name.replace('-', ' ').title()

        except Exception as e:
            self.logger.error(f"Failed to discover course dynamically: {e}")
            return None

    def _create_course_from_comprehensive_api(self, course_slug: str) -> Optional[Course]:
        """Create course structure using the comprehensive course materials API."""
        try:
            self.console.print(f"[blue]Trying comprehensive course materials API for: {course_slug}[/blue]")

            # Make API call using the configured endpoint
            response_data = self.client.get_course_materials(course_slug)

            if not response_data:
                self.console.print("[yellow]No response from comprehensive API[/yellow]")
                return None

            # Parse the response structure
            if 'elements' not in response_data or not response_data['elements']:
                self.console.print("[yellow]No course elements found in API response[/yellow]")
                return None

            main_element = response_data['elements'][0]
            linked_data = response_data.get('linked', {})

            # Extract basic course info
            course_id = main_element.get('id')
            module_ids = main_element.get('moduleIds', [])

            if not course_id:
                self.console.print("[red]No course ID found in response[/red]")
                return None

            # Parse linked data into enhanced models
            modules_data = linked_data.get('onDemandCourseMaterialModules.v1', [])
            lessons_data = linked_data.get('onDemandCourseMaterialLessons.v1', [])
            items_data = linked_data.get('onDemandCourseMaterialItems.v2', [])

            self.console.print(f"[green]Found {len(modules_data)} modules, {len(lessons_data)} lessons, {len(items_data)} items[/green]")

            # Convert to enhanced models
            modules = []
            for module_data in modules_data:
                try:
                    module = CourseraModule(**module_data)
                    modules.append(module)
                except Exception as e:
                    self.logger.warning(f"Failed to parse module {module_data.get('id', 'unknown')}: {e}")

            lessons = []
            for lesson_data in lessons_data:
                try:
                    lesson = CourseraLesson(**lesson_data)
                    lessons.append(lesson)
                except Exception as e:
                    self.logger.warning(f"Failed to parse lesson {lesson_data.get('id', 'unknown')}: {e}")

            items = []
            for item_data in items_data:
                try:
                    # Parse content summary if present
                    if 'contentSummary' in item_data and item_data['contentSummary']:
                        content_summary = ContentSummary(**item_data['contentSummary'])
                        item_data['contentSummary'] = content_summary

                    item = CourseraContentItem(**item_data)
                    items.append(item)
                except Exception as e:
                    self.logger.warning(f"Failed to parse item {item_data.get('id', 'unknown')}: {e}")

            # Create comprehensive course data with all linked sections
            comprehensive_data = ComprehensiveCourseData(
                course_id=course_id,
                module_ids=module_ids,
                modules=modules,
                lessons=lessons,
                items=items,
                tracks=linked_data.get('onDemandCourseMaterialTracks.v1'),
                grading_parameters=linked_data.get('onDemandGradingParameters.v1'),
                passable_lesson_elements=linked_data.get('onDemandCourseMaterialPassableLessonElements.v1'),
                passable_item_groups=linked_data.get('onDemandCourseMaterialPassableItemGroups.v1'),
                passable_item_group_choices=linked_data.get('onDemandCourseMaterialPassableItemGroupChoices.v1'),
                content_atom_relations=linked_data.get('contentAtomRelations.v1'),
                grade_policy=linked_data.get('onDemandCourseMaterialGradePolicy.v1')
            )

            # Log comprehensive data statistics
            self.logger.info(f"Parsed comprehensive data: "
                           f"modules={len(comprehensive_data.modules)}, "
                           f"lessons={len(comprehensive_data.lessons)}, "
                           f"items={len(comprehensive_data.items)}, "
                           f"videos={comprehensive_data.video_count}, "
                           f"accessible_items={comprehensive_data.accessible_items_count}")

            # Log content types breakdown
            content_types = comprehensive_data.total_items_by_type
            if content_types:
                self.logger.info(f"Content types breakdown: {content_types}")

            # Infer course name from modules or use slug
            course_name = course_slug.replace('-', ' ').title()
            if modules:
                # Try to infer from first module or overall structure
                if len(modules) > 1:
                    course_name = f"{modules[0].name.split(':')[0].strip()} Course"
                else:
                    course_name = modules[0].name

            # Convert to standard Course model
            course = ComprehensiveCourseConverter.to_course(
                comprehensive_data,
                course_name,
                course_slug
            )

            # Update lessons and modules with proper references
            self._enrich_course_with_api_data(course, comprehensive_data)

            self.console.print(f"[green]Successfully created course: {course.name}[/green]")
            self.console.print(f"  - {len(course.modules)} modules")
            self.console.print(f"  - {course.total_lessons} lessons")
            self.console.print(f"  - {course.total_assets} content items")

            return course

        except Exception as e:
            self.logger.error(f"Failed to create course from comprehensive API: {e}")
            self.console.print(f"[red]Error with comprehensive API: {e}[/red]")
            return None

    def _enrich_course_with_api_data(self, course: Course, comprehensive_data: ComprehensiveCourseData) -> None:
        """Enrich the course with additional API data for content extraction."""
        try:
            # Add comprehensive data to course metadata for later use
            course.metadata['comprehensive_api_data'] = {
                'course_id': comprehensive_data.course_id,
                'total_duration_minutes': comprehensive_data.total_duration_minutes,
                'video_count': comprehensive_data.video_count,
                'accessible_items': comprehensive_data.accessible_items_count
            }

            # Enrich each lesson with item details for content extraction
            for module in course.modules:
                coursera_module = comprehensive_data.get_module_by_id(module.id)
                if coursera_module:
                    module.metadata['coursera_lesson_ids'] = coursera_module.lessonIds

                for lesson in module.lessons:
                    coursera_lesson = comprehensive_data.get_lesson_by_id(lesson.id)
                    if coursera_lesson:
                        lesson.metadata['coursera_item_ids'] = coursera_lesson.itemIds
                        lesson.metadata['course_id'] = comprehensive_data.course_id

                        # Add comprehensive API data reference for URL extraction
                        lesson.metadata['comprehensive_api_data'] = {
                            'course_id': comprehensive_data.course_id,
                            'lesson_data': {
                                'id': coursera_lesson.id,
                                'item_ids': coursera_lesson.itemIds,
                                'track_id': coursera_lesson.trackId
                            },
                            'items': {}  # Will store item names and metadata
                        }

                        # Add item names and metadata for URL extraction
                        for item_id in coursera_lesson.itemIds:
                            coursera_item = comprehensive_data.get_item_by_id(item_id)
                            if coursera_item:
                                lesson.metadata['comprehensive_api_data']['items'][item_id] = {
                                    'name': coursera_item.name,
                                    'slug': coursera_item.slug,
                                    'content_type': coursera_item.contentSummary.typeName if coursera_item.contentSummary else None,
                                    'is_video': coursera_item.contentSummary.is_video if coursera_item.contentSummary else False
                                }

                        # Enrich each asset with item details and comprehensive data
                        for asset in lesson.assets:
                            item_id = asset.name.split('_')[1] if '_' in asset.name else None
                            if item_id:
                                coursera_item = comprehensive_data.get_item_by_id(item_id)
                                if coursera_item:
                                    asset.metadata['coursera_item'] = {
                                        'id': coursera_item.id,
                                        'slug': coursera_item.slug,
                                        'content_type': coursera_item.content_type,
                                        'is_video': coursera_item.contentSummary.is_video if coursera_item.contentSummary else False,
                                        'duration': coursera_item.contentSummary.duration if coursera_item.contentSummary else None,
                                        'track_id': coursera_item.trackId
                                    }

                                    # Pass comprehensive API data for efficient URL extraction
                                    asset.metadata['comprehensive_api_data'] = {
                                        'course_id': comprehensive_data.course_id,
                                        'items': {item_id: coursera_item.model_dump() if hasattr(coursera_item, 'model_dump') else coursera_item.__dict__}  # Pass item data safely
                                    }

        except Exception as e:
            self.logger.warning(f"Failed to enrich course with API data: {e}")

    def _create_course_from_working_api(self, course_identifier: str) -> Optional[Course]:
        """Create course structure using comprehensive API first, then fallback to dynamic discovery."""
        try:
            # First, try the comprehensive course materials API
            course = self._create_course_from_comprehensive_api(course_identifier)
            if course:
                return course

            # Fallback to existing dynamic discovery method
            self.console.print(f"[yellow]Comprehensive API failed, falling back to dynamic discovery[/yellow]")
            return self._create_course_from_dynamic_discovery(course_identifier)

        except Exception as e:
            self.logger.error(f"Failed to create course from working API: {e}")
            return None

    def _create_course_from_dynamic_discovery(self, course_identifier: str) -> Optional[Course]:
        """Create course structure using dynamic discovery (original method)."""
        try:
            # This is the original implementation renamed for clarity
            # First try dynamic discovery
            self.console.print(f"[blue]Attempting dynamic discovery for: {course_identifier}[/blue]")
            course_config = self._discover_course_dynamically(course_identifier)

            if not course_config:
                self.console.print(f"[red]Could not discover course structure for: {course_identifier}[/red]")
                return None

            # Create course object
            course = Course(
                id=course_config['course_id'],
                name=course_config['course_name'],
                slug=course_identifier,
                description=f"Dynamically discovered content from {course_config['course_name']} course"
            )

            # Organize content items into logical modules
            self.console.print("[blue]Organizing content into lessons and modules...[/blue]")
            modules = self._organize_content_into_modules(course_config['valid_content_items'])
            course.modules = modules

            # Process all content items for each lesson
            self.console.print("[blue]Processing content items for each lesson...[/blue]")
            total_content = len(course_config['valid_content_items'])
            for i, content_item in enumerate(course_config['valid_content_items'], 1):
                self.console.print(f"  Processing content {i}/{total_content}: {content_item['content_type']} - {content_item['item_id']}")

                try:
                    # Find the lesson that contains this content item
                    target_lesson = self._find_lesson_for_content(course.modules, content_item['item_id'])

                    if target_lesson:
                        # Extract content assets based on content type
                        new_assets = self._extract_content_assets_by_type(content_item)

                        # Add to existing content assets
                        if not target_lesson.assets:
                            target_lesson.assets = []
                        target_lesson.assets.extend(new_assets)

                        # Add to lesson metadata
                        if 'content_items' not in target_lesson.metadata:
                            target_lesson.metadata['content_items'] = []

                        target_lesson.metadata['content_items'].append({
                            'item_id': content_item['item_id'],
                            'content_type': content_item['content_type'],
                            'title': self._get_content_title(content_item)
                        })

                except Exception as e:
                    self.logger.warning(f"Failed to process content item {content_item['item_id']}: {e}")
                    continue

            self.console.print(f"[green]Successfully created course structure with {len(course.modules)} modules[/green]")
            return course

        except Exception as e:
            self.logger.error(f"Failed to create course from dynamic discovery: {e}")
            return None

    def _organize_content_into_modules(self, valid_content_items: List[Dict]) -> List[Module]:
        """Automatically organize content items into logical lessons and modules."""
        try:
            # Group content items to estimate lesson count
            # Videos typically represent distinct lessons, so count video items primarily
            video_items = [item for item in valid_content_items if item['content_type'] == 'video']
            total_lessons = max(len(video_items), len(valid_content_items) // 3)  # Estimate lessons

            # Use better module sizing logic to avoid uneven distribution
            # Aim for 6-8 lessons per module with more even distribution
            if total_lessons <= 12:
                module_size = max(4, total_lessons // 2)  # 2 modules for small courses
            elif total_lessons <= 24:
                module_size = 6  # Fixed 6 for medium courses
            else:
                # For larger courses, aim for 5-7 lessons per module
                # Calculate optimal size to avoid having just 1-2 lessons in last module
                target_modules = (total_lessons + 5) // 6  # Aim for ~6 lessons per module
                module_size = (total_lessons + target_modules - 1) // target_modules
                module_size = max(5, min(8, module_size))  # Clamp between 5-8

            modules = []
            current_module = 1

            # Group content items by estimated lessons
            content_groups = []
            if video_items:
                # Use videos as primary lesson indicators
                for i in range(0, len(video_items), 1):  # Each video = potential lesson
                    lesson_content = [video_items[i]]

                    # Find related non-video content for this lesson
                    # This is a heuristic - items discovered close to each other likely belong together
                    video_index_in_all = valid_content_items.index(video_items[i])
                    for j in range(max(0, video_index_in_all-2), min(len(valid_content_items), video_index_in_all+3)):
                        item = valid_content_items[j]
                        if item['content_type'] != 'video' and item not in lesson_content:
                            lesson_content.append(item)

                    content_groups.append(lesson_content)
            else:
                # No videos found, group by content type and position
                for i in range(0, len(valid_content_items), 2):  # Assume 2 items per lesson
                    lesson_content = valid_content_items[i:i+2]
                    content_groups.append(lesson_content)

            # Organize content groups into modules
            for i in range(0, len(content_groups), module_size):
                module_lessons = content_groups[i:i + module_size]

                # Create meaningful module names
                if current_module == 1:
                    module_name = "Course Introduction and Fundamentals"
                elif current_module == 2:
                    module_name = "Core Concepts and Skills"
                elif i + module_size >= len(content_groups):
                    module_name = "Advanced Topics and Conclusion"
                else:
                    module_name = f"Module {current_module}: Extended Learning"

                # Create module
                module = Module(
                    id=f"module-{current_module:02d}",
                    name=module_name,
                    order=current_module,
                    lessons=[]
                )

                # Create lessons within the module
                for j, lesson_content in enumerate(module_lessons, 1):
                    # Use the main content item (typically video) as lesson identifier
                    main_item = lesson_content[0]

                    lesson = Lesson(
                        id=main_item['item_id'],
                        name=f"Lesson {j}: {self._get_content_title(main_item)}",
                        order=j,
                        metadata={'content_items': lesson_content}
                    )
                    module.lessons.append(lesson)

                modules.append(module)
                current_module += 1

            return modules

        except Exception as e:
            self.logger.error(f"Failed to organize content into modules: {e}")
            # Fallback: single module with all content
            module = Module(
                id="module-01",
                name="Course Content",
                order=1,
                lessons=[]
            )

            for i, content_item in enumerate(valid_content_items, 1):
                lesson = Lesson(
                    id=content_item['item_id'],
                    name=f"Lesson {i}: {self._get_content_title(content_item)}",
                    order=i,
                    metadata={'content_items': [content_item]}
                )
                module.lessons.append(lesson)

            return [module]

    def _find_lesson_for_content(self, modules: List[Module], content_item_id: str) -> Optional[Lesson]:
        """Find the lesson that should contain the given content item."""
        for module in modules:
            for lesson in module.lessons:
                # Check if this content item is the primary lesson identifier
                if lesson.id == content_item_id:
                    return lesson

                # Check if this content item is in lesson metadata
                if hasattr(lesson, 'metadata') and lesson.metadata:
                    content_items = lesson.metadata.get('content_items', [])
                    for item in content_items:
                        if item['item_id'] == content_item_id:
                            return lesson
        return None

    def _get_content_title(self, content_item: Dict) -> str:
        """Extract a meaningful title from content item data."""
        try:
            data = content_item.get('data', {})

            # Try to get title from linked data
            if 'linked' in data:
                for data_key in data['linked'].keys():
                    items = data['linked'][data_key]
                    if items and len(items) > 0:
                        first_item = items[0]
                        if 'title' in first_item:
                            return first_item['title']
                        if 'name' in first_item:
                            return first_item['name']

            # Fallback to content type and ID
            return f"{content_item['content_type'].title()} {content_item['item_id']}"

        except Exception:
            return f"{content_item['content_type'].title()} Content"

    def _extract_content_assets_by_type(self, content_item: Dict) -> List[ContentAsset]:
        """Extract downloadable assets based on content type."""
        assets = []
        content_type = content_item['content_type']
        data = content_item.get('data', {})

        try:
            if content_type == ContentType.VIDEO:
                # Use existing video extraction logic with item_id and video name
                video_name = self._get_content_title(content_item)
                assets.extend(self._extract_video_content_assets(data, content_item.get('item_id'), video_name))

            elif content_type == ContentType.READING:
                assets.extend(self._extract_generic_content_assets(
                    data, content_item['item_id'], 'onDemandReadings.v1', ContentType.READING
                ))

            elif content_type == ContentType.SUPPLEMENT:
                assets.extend(self._extract_generic_content_assets(
                    data, content_item['item_id'], 'onDemandSupplements.v1', ContentType.SUPPLEMENT
                ))

            elif content_type == ContentType.ASSIGNMENT:
                assets.extend(self._extract_generic_content_assets(
                    data, content_item['item_id'], 'onDemandLearnerAssignments.v1', ContentType.ASSIGNMENT
                ))

            self.logger.info(f"Extracted {len(assets)} assets from {content_type} content")
            return assets

        except Exception as e:
            self.logger.error(f"Failed to extract assets from {content_type} content: {e}")
            return assets

    def _extract_generic_content_assets(self, data: Dict, item_id: str, data_key: str, asset_type: str) -> List[ContentAsset]:
        """Consolidated method for extracting assets from different content types."""
        assets = []
        try:
            if 'linked' not in data or data_key not in data['linked']:
                return assets

            items = data['linked'][data_key]
            for i, item in enumerate(items):
                url = item.get('url')
                if not url:
                    continue

                # Get title and type information
                title = item.get('title', f'{asset_type.title()} {i+1}')
                item_type = item.get('type', item.get('readingType', item.get('supplementType', asset_type)))

                # Use existing utility for file extension
                file_ext = get_file_extension(url, item_type)

                assets.append(ContentAsset(
                    name=f"{asset_type}_{item_id}_{i+1}.{file_ext}",
                    url=url,
                    file_type=asset_type,
                    metadata={
                        'title': title,
                        'type': item_type,
                        'description': item.get('description', ''),
                        'index': i
                    }
                ))

        except Exception as e:
            self.logger.error(f"Failed to extract {asset_type} assets: {e}")

        return assets

    def _extract_video_content_assets(self, video_data: Dict[str, Any], item_id: str = None, video_name: str = None) -> List[ContentAsset]:
        """Extract downloadable assets from video content API response."""
        assets = []

        try:
            if 'linked' not in video_data or 'onDemandVideos.v1' not in video_data['linked']:
                self.logger.warning("No video data found in API response")
                return assets

            video_info = video_data['linked']['onDemandVideos.v1'][0]

            # Extract video URLs by resolution - ONLY 720p MP4 as requested
            if 'sources' in video_info and 'byResolution' in video_info['sources']:
                # Only extract 720p MP4 format
                if '720p' in video_info['sources']['byResolution']:
                    source_data = video_info['sources']['byResolution']['720p']
                    if 'mp4VideoUrl' in source_data:
                        # Use actual video name if provided, otherwise fallback to item_id
                        if video_name:
                            # Sanitize the video name for filesystem
                            from ..utils.sanitizer import sanitize_file_name
                            safe_name = sanitize_file_name(video_name)
                            filename = f"{safe_name}_720p.mp4"
                        else:
                            filename = f"video_{item_id}_720p.mp4" if item_id else "video_720p.mp4"

                        assets.append(ContentAsset(
                            name=filename,
                            url=source_data['mp4VideoUrl'],
                            file_type="video",
                            metadata={
                                'resolution': '720p',
                                'format': 'mp4',
                                'item_id': item_id,
                                'original_name': video_name,
                                # Note: course_id will be added by the comprehensive API extraction
                                'course_id': None  # Will be set later in comprehensive API processing
                            }
                        ))
                        self.logger.info(f"Extracted 720p MP4 video: {filename}")
                    else:
                        self.logger.warning(f"No 720p MP4 URL found for item {item_id}")
                else:
                    self.logger.warning(f"No 720p resolution available for item {item_id}")

            # Extract audio URLs
            if 'sources' in video_info and 'audio' in video_info['sources']:
                for i, audio_data in enumerate(video_info['sources']['audio']):
                    audio_format = audio_data.get('audioFormat', 'audio')
                    bitrate = audio_data.get('bitrate', 'unknown')
                    if 'url' in audio_data:
                        assets.append(ContentAsset(
                            name=f"audio_{bitrate}kbps.{audio_format.lower()}",
                            url=audio_data['url'],
                            file_type="audio",
                            metadata={'bitrate': bitrate, 'format': audio_format}
                        ))

            # Extract subtitle URLs (.srt format) - DISABLED: User doesn't want subtitles
            # if 'subtitles' in video_info:
            #     for lang_code, subtitle_url in video_info['subtitles'].items():
            #         assets.append(ContentAsset(
            #             name=f"subtitles_{lang_code}.srt",
            #             url=subtitle_url,
            #             file_type="subtitles",
            #             metadata={'language': lang_code, 'format': 'srt'}
            #         ))

            # Extract transcript URLs (.txt format) - DISABLED: User doesn't want subtitles/transcripts
            # if 'subtitlesTxt' in video_info:
            #     for lang_code, transcript_url in video_info['subtitlesTxt'].items():
            #         assets.append(ContentAsset(
            #             name=f"transcript_{lang_code}.txt",
            #             url=transcript_url,
            #             file_type="transcript",
            #             metadata={'language': lang_code, 'format': 'txt'}
            #         ))

            self.logger.info(f"Extracted {len(assets)} content assets from video data")
            return assets

        except Exception as e:
            self.logger.error(f"Failed to extract video content assets: {e}")
            return assets

    def _scrape_module(self, module: Module, progress: Progress, parent_task: TaskID) -> None:
        """Scrape a single module and its lessons."""
        if not module.lessons:
            return

        # Create subtask for lessons
        lesson_task = progress.add_task(
            f"  Lessons in {module.name}",
            total=len(module.lessons)
        )

        for lesson in module.lessons:
            progress.update(lesson_task, description=f"  Processing: {lesson.name}")

            # Create lesson directory
            lesson_path = self.file_manager.create_lesson_directory(lesson, module.local_path)

            # Save lesson metadata
            self.file_manager.save_lesson_metadata(lesson)

            # Process lesson assets if download is enabled
            if self.config.download_settings.download_files and lesson.assets:
                self._download_lesson_assets(lesson, progress)

            # Update progress
            progress.advance(lesson_task)
            self.current_progress.completed_lessons += 1

        progress.remove_task(lesson_task)

    def _extract_content_assets_from_comprehensive_api(self, lesson: Lesson) -> None:
        """Extract downloadable content assets using item IDs from comprehensive API."""
        try:
            if 'coursera_item_ids' not in lesson.metadata:
                return

            item_ids = lesson.metadata['coursera_item_ids']
            course_id = lesson.metadata.get('course_id')

            if not course_id:
                # Try to get course_id from course metadata
                course_id = lesson.metadata.get('comprehensive_api_data', {}).get('course_id')

            if not course_id:
                self.logger.warning(f"No course ID found for lesson {lesson.id}")
                return

            extracted_assets = []

            for item_id in item_ids:
                try:
                    # Find the asset for this item_id
                    target_asset = None
                    for asset in lesson.assets:
                        if item_id in asset.name:
                            target_asset = asset
                            break

                    if not target_asset:
                        continue

                    # Get item metadata
                    item_metadata = target_asset.metadata.get('coursera_item', {})
                    content_type = item_metadata.get('content_type', 'unknown')

                    # Check if we should skip this content type
                    if ContentTypeMapper.should_skip(content_type):
                        self.logger.info(f"Skipping {content_type} content: {item_id}")
                        lesson.assets.remove(target_asset)
                        continue

                    # Check if content is downloadable
                    if not ContentTypeMapper.is_downloadable(content_type):
                        self.logger.info(f"Content type {content_type} is not downloadable: {item_id}")
                        lesson.assets.remove(target_asset)
                        continue

                    # Enhanced: Try to get URLs directly from comprehensive API data first
                    content_urls = self._extract_urls_from_comprehensive_data(item_id, content_type, target_asset.metadata)

                    # If no URLs from comprehensive data, fallback to individual API calls
                    if not content_urls:
                        # Try to get comprehensive data to extract video names
                        comprehensive_data = lesson.metadata.get('comprehensive_api_data', {})
                        content_urls = self._extract_urls_via_individual_api_calls(course_id, item_id, content_type, comprehensive_data)

                    # Create assets from URLs
                    for url_data in content_urls:
                        asset = ContentAsset(
                            name=url_data['name'],
                            url=url_data['url'],
                            file_type=url_data.get('file_type'),
                            metadata={
                                'source': url_data.get('source', 'comprehensive_api'),
                                'resolution': url_data.get('resolution'),
                                'quality': url_data.get('quality'),
                                'original_item_id': item_id,
                                'content_type': content_type,
                                # Add course_id and item_id for enhanced downloader compatibility
                                'course_id': course_id,
                                'item_id': item_id
                            }
                        )
                        extracted_assets.append(asset)
                        self.logger.debug(f"Created asset: {asset.name} from {url_data.get('source', 'API')}")

                    # Remove the placeholder asset
                    if target_asset in lesson.assets:
                        lesson.assets.remove(target_asset)

                except Exception as e:
                    self.logger.warning(f"Failed to extract assets for item {item_id}: {e}")

            # Add all extracted assets to the lesson
            lesson.assets.extend(extracted_assets)

            # Add sequential numbering to video assets for better ordering
            self._add_sequential_numbering_to_videos(lesson)

            self.logger.info(f"Extracted {len(extracted_assets)} total assets for lesson {lesson.name}")

        except Exception as e:
            self.logger.error(f"Failed to extract assets from comprehensive API for lesson {lesson.id}: {e}")

    def _add_sequential_numbering_to_videos(self, lesson: Lesson) -> None:
        """Add sequential numbering to video assets based on lesson item order."""
        try:
            # Get the ordered item IDs from lesson metadata
            item_ids = lesson.metadata.get('coursera_item_ids', [])
            if not item_ids:
                return

            # Find video assets and match them to their position in the lesson
            video_assets = [asset for asset in lesson.assets if asset.file_type == 'video']
            if not video_assets:
                return

            video_sequence_map = {}
            video_counter = 1

            # Map video assets to their sequential position
            for item_id in item_ids:
                # Find the video asset for this item_id
                for asset in video_assets:
                    if item_id in asset.metadata.get('original_item_id', '') or item_id in asset.name:
                        video_sequence_map[asset] = video_counter
                        video_counter += 1
                        break

            # Rename video assets with sequential numbering
            for asset in video_assets:
                if asset in video_sequence_map:
                    sequence_num = video_sequence_map[asset]
                    # Extract the base name without any existing numbers
                    base_name = asset.name

                    # Add sequential number prefix (001_, 002_, etc.)
                    new_name = f"{sequence_num:03d}_{base_name}"

                    self.logger.debug(f"Renaming video: {asset.name} -> {new_name}")
                    asset.name = new_name

        except Exception as e:
            self.logger.warning(f"Failed to add sequential numbering to videos in lesson {lesson.id}: {e}")

    def _extract_urls_from_comprehensive_data(self, item_id: str, content_type: str, asset_metadata: Dict) -> List[Dict]:
        """Extract URLs directly from comprehensive API data if available."""
        try:
            urls = []

            # Check if we have comprehensive API data cached
            comprehensive_data = asset_metadata.get('comprehensive_api_data')
            if not comprehensive_data:
                return urls

            # For videos, look for direct video URL patterns
            if ContentTypeMapper.is_video(content_type):
                # This would be enhanced to extract video URLs from the comprehensive API response
                # For now, we'll use the individual API call method as fallback
                pass

            # For other content types, check for direct asset URLs
            item_data = comprehensive_data.get('items', {}).get(item_id, {})
            if item_data and 'asset_urls' in item_data:
                for url_info in item_data['asset_urls']:
                    urls.append({
                        'name': f"{content_type}_{item_id}",
                        'url': url_info['url'],
                        'file_type': url_info.get('type', content_type),
                        'source': 'comprehensive_api',
                        'resolution': url_info.get('resolution'),
                        'quality': url_info.get('quality')
                    })

            return urls

        except Exception as e:
            self.logger.warning(f"Failed to extract URLs from comprehensive data for {item_id}: {e}")
            return []

    def _extract_urls_via_individual_api_calls(self, course_id: str, item_id: str, content_type: str, comprehensive_data: Dict = None) -> List[Dict]:
        """Fallback method to extract URLs using individual API calls."""
        try:
            urls = []

            # Extract video name from comprehensive data if available
            video_name = None
            if comprehensive_data and ContentTypeMapper.is_video(content_type):
                items_data = comprehensive_data.get('items', {})
                item_data = items_data.get(item_id, {})
                video_name = item_data.get('name')

            # Extract assets based on type using individual API calls
            if ContentTypeMapper.is_video(content_type):
                video_assets = self._extract_video_assets_by_item_id(course_id, item_id, video_name)
                for asset in video_assets:
                    if asset.url:
                        urls.append({
                            'name': asset.name,
                            'url': asset.url,
                            'file_type': asset.file_type,
                            'source': 'video_api',
                            'resolution': asset.metadata.get('resolution'),
                            'quality': asset.metadata.get('quality')
                        })

            elif ContentTypeMapper.is_reading(content_type):
                reading_assets = self._extract_reading_assets_by_item_id(course_id, item_id)
                for asset in reading_assets:
                    if asset.url:
                        urls.append({
                            'name': asset.name,
                            'url': asset.url,
                            'file_type': asset.file_type,
                            'source': 'reading_api'
                        })

            elif ContentTypeMapper.is_assignment(content_type):
                assignment_assets = self._extract_assignment_assets_by_item_id(course_id, item_id, content_type)
                for asset in assignment_assets:
                    if asset.url:
                        urls.append({
                            'name': asset.name,
                            'url': asset.url,
                            'file_type': asset.file_type,
                            'source': 'assignment_api'
                        })

            return urls

        except Exception as e:
            self.logger.warning(f"Failed to extract URLs via individual API calls for {item_id}: {e}")
            return []

    def _extract_assignment_assets_by_item_id(self, course_id: str, item_id: str, content_type: str) -> List[ContentAsset]:
        """Extract assignment assets (may have instructions, submissions, etc.)."""
        try:
            # For assignments, try different API endpoints
            possible_endpoints = [
                f"https://www.coursera.org/api/onDemandLearnerAssignments.v1/{course_id}~{item_id}",
                f"https://www.coursera.org/api/onDemandLectureReadings.v1/{course_id}~{item_id}?includes=reading&fields=onDemandReadings.v1(url%2Ctitle%2Cdescription%2CreadingType)"
            ]

            headers = self.client.auth.get_headers(include_csrf=False)
            cookies = self.client.auth.get_cookies()

            for endpoint_url in possible_endpoints:
                try:
                    response = self.client.session.get(endpoint_url, headers=headers, cookies=cookies)
                    if response.status_code == 200:
                        data = response.json()

                        # Try different data keys based on endpoint
                        for data_key in ['onDemandLearnerAssignments.v1', 'onDemandReadings.v1']:
                            assets = self._extract_generic_content_assets(data, item_id, data_key, 'assignment')
                            if assets:
                                return assets

                except Exception as e:
                    self.logger.debug(f"Assignment extraction failed for endpoint {endpoint_url}: {e}")
                    continue

        except Exception as e:
            self.logger.warning(f"Failed to extract assignment for {item_id}: {e}")

        return []

    def _extract_video_assets_by_item_id(self, course_id: str, item_id: str, video_name: str = None) -> List[ContentAsset]:
        """Extract video assets using the video API."""
        try:
            response_data = self.client.get_lecture_video(course_id, item_id)
            if response_data:
                return self._extract_video_content_assets(response_data, item_id, video_name)
        except Exception as e:
            self.logger.warning(f"Failed to extract video for {item_id}: {e}")
        return []

    def _extract_reading_assets_by_item_id(self, course_id: str, item_id: str) -> List[ContentAsset]:
        """Extract reading/supplement assets using individual API calls."""
        try:
            # Try the reading API endpoint
            reading_url = f"https://www.coursera.org/api/onDemandLectureReadings.v1/{course_id}~{item_id}?includes=reading&fields=onDemandReadings.v1(url%2Ctitle%2Cdescription%2CreadingType)"

            headers = self.client.auth.get_headers(include_csrf=False)
            cookies = self.client.auth.get_cookies()

            response = self.client.session.get(reading_url, headers=headers, cookies=cookies)

            if response.status_code == 200:
                data = response.json()
                return self._extract_generic_content_assets(data, item_id, 'onDemandReadings.v1', 'reading')

        except Exception as e:
            self.logger.warning(f"Failed to extract reading for {item_id}: {e}")
        return []

    def _download_lesson_assets(self, lesson: Lesson, progress: Progress) -> None:
        """Download assets for a lesson, extracting URLs if needed."""
        try:
            # First, try to extract actual content URLs if we have comprehensive API data
            if 'coursera_item_ids' in lesson.metadata:
                self._extract_content_assets_from_comprehensive_api(lesson)

            # Now proceed with downloading if assets have URLs
            if not lesson.assets:
                return

            # Filter assets that have URLs
            downloadable_assets = [asset for asset in lesson.assets if asset.url]

            if not downloadable_assets:
                self.logger.info(f"No downloadable assets found for lesson: {lesson.name}")
                return

            # Create download progress for this lesson
            download_task = progress.add_task(
                f"    Downloading {lesson.name}",
                total=len(downloadable_assets)
            )

            for asset in downloadable_assets:
                try:
                    progress.update(download_task, description=f"    Downloading: {asset.name}")

                    # Check if this is a video asset and pass sequence number
                    if asset.file_type == 'video':
                        success = self.file_manager.download_asset(
                            asset,
                            lesson.local_path,
                            sequence_number=self.video_sequence_counter
                        )

                        if success:
                            self.logger.info(f"Downloaded video {self.video_sequence_counter}: {asset.name}")
                            self.video_sequence_counter += 1
                    else:
                        # For non-video assets, use regular download
                        success = self.file_manager.download_asset(asset, lesson.local_path)

                    if success:
                        asset.downloaded = True
                        self.current_progress.downloaded_assets += 1
                    else:
                        self.current_progress.failed_downloads.append(f"{lesson.name}/{asset.name}")

                    progress.advance(download_task)

                    # Add small delay to avoid overwhelming the server
                    time.sleep(0.1)

                except Exception as e:
                    self.logger.error(f"Failed to download asset {asset.name}: {e}")
                    self.current_progress.failed_downloads.append(f"{lesson.name}/{asset.name}")
                    progress.advance(download_task)

            progress.remove_task(download_task)

        except Exception as e:
            self.logger.error(f"Failed to download lesson assets for {lesson.name}: {e}")
