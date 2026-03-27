"""Data models for Coursera course content."""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from pathlib import Path
from enum import Enum


class ContentAsset(BaseModel):
    """Represents a downloadable asset (video, PDF, etc.)."""
    name: str
    url: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None  # in bytes
    local_path: Optional[Path] = None
    downloaded: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Additional metadata

    @validator('file_type', pre=True, always=True)
    def extract_file_type_from_url(cls, v, values):
        """Extract file type from URL if not provided."""
        if v is None and 'url' in values and values['url']:
            url = values['url'].lower()
            if '.mp4' in url or 'video' in url:
                return 'video'
            elif '.pdf' in url:
                return 'pdf'
            elif '.pptx' in url or '.ppt' in url:
                return 'presentation'
            elif '.docx' in url or '.doc' in url:
                return 'document'
            elif '.txt' in url:
                return 'text'
        return v

    def __hash__(self) -> int:
        """Make ContentAsset hashable so it can be used as dict keys."""
        # Use name and file_type as the basis for hashing since these identify the asset
        return hash((self.name, self.file_type, self.url))

    def __eq__(self, other) -> bool:
        """Define equality for ContentAsset objects."""
        if not isinstance(other, ContentAsset):
            return False
        return (
            self.name == other.name and
            self.file_type == other.file_type and
            self.url == other.url
        )


class Lesson(BaseModel):
    """Represents a single lesson within a module."""
    id: str
    name: str
    description: Optional[str] = None
    order: int = 0
    duration_minutes: Optional[int] = None
    assets: List[ContentAsset] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    local_path: Optional[Path] = None

    @validator('name')
    def sanitize_name(cls, v):
        """Sanitize lesson name for file system."""
        import re
        # Remove invalid characters for file names
        return re.sub(r'[<>:"/\\|?*]', '_', v).strip()


class Module(BaseModel):
    """Represents a module containing multiple lessons."""
    id: str
    name: str
    description: Optional[str] = None
    order: int = 0
    lessons: List[Lesson] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    local_path: Optional[Path] = None

    @validator('name')
    def sanitize_name(cls, v):
        """Sanitize module name for file system."""
        import re
        return re.sub(r'[<>:"/\\|?*]', '_', v).strip()


class Course(BaseModel):
    """Represents a complete course with modules and lessons."""
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    instructor: Optional[str] = None
    university: Optional[str] = None
    language: Optional[str] = None
    estimated_hours: Optional[float] = None
    modules: List[Module] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    local_path: Optional[Path] = None
    scraped_at: datetime = Field(default_factory=datetime.now)

    @validator('name')
    def sanitize_name(cls, v):
        """Sanitize course name for file system."""
        import re
        return re.sub(r'[<>:"/\\|?*]', '_', v).strip()

    @property
    def total_lessons(self) -> int:
        """Calculate total number of lessons across all modules."""
        return sum(len(module.lessons) for module in self.modules)

    @property
    def total_assets(self) -> int:
        """Calculate total number of assets across all lessons."""
        return sum(
            len(lesson.assets)
            for module in self.modules
            for lesson in module.lessons
        )


class ScrapingProgress(BaseModel):
    """Tracks the progress of a scraping session."""
    course_id: str
    course_name: str
    total_modules: int = 0
    completed_modules: int = 0
    total_lessons: int = 0
    completed_lessons: int = 0
    total_assets: int = 0
    downloaded_assets: int = 0
    failed_downloads: List[str] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=datetime.now)
    last_update: datetime = Field(default_factory=datetime.now)
    is_complete: bool = False

    @property
    def module_progress_percent(self) -> float:
        """Get module completion percentage."""
        if self.total_modules == 0:
            return 0.0
        return (self.completed_modules / self.total_modules) * 100

    @property
    def lesson_progress_percent(self) -> float:
        """Get lesson completion percentage."""
        if self.total_lessons == 0:
            return 0.0
        return (self.completed_lessons / self.total_lessons) * 100

    @property
    def download_progress_percent(self) -> float:
        """Get download completion percentage."""
        if self.total_assets == 0:
            return 0.0
        return (self.downloaded_assets / self.total_assets) * 100

    @property
    def overall_progress_percent(self) -> float:
        """Get overall completion percentage."""
        if not self.total_lessons:
            return 0.0
        # Weight lessons more heavily than downloads
        return (self.lesson_progress_percent * 0.7) + (self.download_progress_percent * 0.3)


class APIEndpointConfig(BaseModel):
    """Configuration for a single API endpoint."""
    path: str
    method: str = "GET"
    response_mapping: Dict[str, str] = Field(default_factory=dict)
    headers: Dict[str, str] = Field(default_factory=dict)

    def get_mapped_value(self, response_data: Dict[str, Any], field_name: str) -> Any:
        """Extract a value from API response using the mapping."""
        if field_name not in self.response_mapping:
            return None

        path = self.response_mapping[field_name]
        value = response_data

        # Navigate nested dictionary using dot notation
        for key in path.split('.'):
            if '[' in key and ']' in key:
                # Handle array indexing like "elements[0]"
                array_key, index = key.split('[')
                index = int(index.rstrip(']'))
                value = value.get(array_key, [])
                if isinstance(value, list) and len(value) > index:
                    value = value[index]
                else:
                    return None
            else:
                value = value.get(key)
                if value is None:
                    return None

        return value


class APIConfig(BaseModel):
    """Complete API configuration."""
    base_url: str
    endpoints: Dict[str, APIEndpointConfig]

    def get_endpoint_url(self, endpoint_name: str, **kwargs) -> str:
        """Get formatted endpoint URL."""
        if endpoint_name not in self.endpoints:
            raise ValueError(f"Unknown endpoint: {endpoint_name}")

        endpoint = self.endpoints[endpoint_name]
        path = endpoint.path.format(**kwargs)
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"


# Enhanced models for comprehensive course materials API

class CourseraContentType(str, Enum):
    """Enumeration of content types from Coursera API."""
    LECTURE = "lecture"
    SUPPLEMENT = "supplement"
    UNGRADED_ASSIGNMENT = "ungradedAssignment"
    DISCUSSION_PROMPT = "discussionPrompt"
    PHASED_PEER = "phasedPeer"
    STAFF_GRADED = "staffGraded"
    GRADED_LTI = "gradedLti"
    QUIZ = "quiz"
    EXAM = "exam"
    PEER_REVIEW = "peerReview"


class ContentSummary(BaseModel):
    """Content summary from the comprehensive API."""
    typeName: str
    definition: Dict[str, Any] = Field(default_factory=dict)

    @property
    def is_video(self) -> bool:
        """Check if this content is a video/lecture."""
        return self.typeName == "lecture"

    @property
    def is_downloadable(self) -> bool:
        """Check if this content type is typically downloadable."""
        return self.typeName in [
            "lecture", "supplement", "ungradedAssignment",
            "staffGraded", "phasedPeer"
        ]

    @property
    def duration(self) -> Optional[int]:
        """Get video duration if available."""
        if self.typeName == "lecture" and "duration" in self.definition:
            return self.definition["duration"]
        return None

    @property
    def has_video_assessment(self) -> bool:
        """Check if video has in-video assessment."""
        if self.typeName == "lecture" and "hasInVideoAssessment" in self.definition:
            return self.definition["hasInVideoAssessment"]
        return False


class CourseraContentItem(BaseModel):
    """Enhanced content item from onDemandCourseMaterialItems.v2."""
    id: str
    name: str
    originalName: Optional[str] = None
    slug: str
    timeCommitment: Optional[int] = None  # in milliseconds
    contentSummary: Optional[ContentSummary] = None
    isLocked: bool = False
    lockableByItem: Optional[bool] = None
    itemLockedReasonCode: Optional[str] = None
    trackId: Optional[str] = None
    lockedStatus: Optional[str] = None
    itemLockSummary: Optional[Dict[str, Any]] = None
    customDisplayTypenameOverride: Optional[str] = None
    moduleId: Optional[str] = None
    lessonId: Optional[str] = None

    @property
    def duration_minutes(self) -> Optional[float]:
        """Get duration in minutes."""
        if self.timeCommitment:
            return self.timeCommitment / 60000  # Convert from milliseconds
        return None

    @property
    def content_type(self) -> str:
        """Get simplified content type."""
        if self.contentSummary:
            return self.contentSummary.typeName
        return "unknown"

    @property
    def is_accessible(self) -> bool:
        """Check if content is accessible (not locked)."""
        return not self.isLocked


class CourseraLesson(BaseModel):
    """Enhanced lesson from onDemandCourseMaterialLessons.v1."""
    id: str
    name: str
    slug: str
    timeCommitment: Optional[int] = None  # in milliseconds
    elementIds: List[str] = Field(default_factory=list)
    itemIds: List[str] = Field(default_factory=list)  # Direct item references
    optional: Optional[bool] = None
    trackId: Optional[str] = None
    moduleId: Optional[str] = None

    @property
    def duration_minutes(self) -> Optional[float]:
        """Get duration in minutes."""
        if self.timeCommitment:
            return self.timeCommitment / 60000  # Convert from milliseconds
        return None


class CourseraModule(BaseModel):
    """Enhanced module from onDemandCourseMaterialModules.v1."""
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    timeCommitment: Optional[int] = None  # in milliseconds
    lessonIds: List[str] = Field(default_factory=list)
    optional: Optional[bool] = None
    learningObjectives: List[str] = Field(default_factory=list)

    @property
    def duration_minutes(self) -> Optional[float]:
        """Get duration in minutes."""
        if self.timeCommitment:
            return self.timeCommitment / 60000  # Convert from milliseconds
        return None


class ComprehensiveCourseData(BaseModel):
    """Complete course data from the comprehensive materials API."""
    course_id: str
    module_ids: List[str] = Field(default_factory=list)
    modules: List[CourseraModule] = Field(default_factory=list)
    lessons: List[CourseraLesson] = Field(default_factory=list)
    items: List[CourseraContentItem] = Field(default_factory=list)
    tracks: Optional[List[Dict[str, Any]]] = None
    grading_parameters: Optional[List[Dict[str, Any]]] = None  # Updated to handle list format
    passable_lesson_elements: Optional[List[Dict[str, Any]]] = None
    passable_item_groups: Optional[List[Dict[str, Any]]] = None
    passable_item_group_choices: Optional[List[Dict[str, Any]]] = None
    content_atom_relations: Optional[List[Dict[str, Any]]] = None
    grade_policy: Optional[List[Dict[str, Any]]] = None

    def get_module_by_id(self, module_id: str) -> Optional[CourseraModule]:
        """Get module by ID."""
        for module in self.modules:
            if module.id == module_id:
                return module
        return None

    def get_lesson_by_id(self, lesson_id: str) -> Optional[CourseraLesson]:
        """Get lesson by ID."""
        for lesson in self.lessons:
            if lesson.id == lesson_id:
                return lesson
        return None

    def get_item_by_id(self, item_id: str) -> Optional[CourseraContentItem]:
        """Get item by ID."""
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def get_lessons_for_module(self, module_id: str) -> List[CourseraLesson]:
        """Get all lessons for a specific module."""
        module = self.get_module_by_id(module_id)
        if not module:
            return []

        # First try to get lessons by lesson IDs in the module
        lessons_by_ids = [lesson for lesson in self.lessons if lesson.id in module.lessonIds]

        # If no lessons found by IDs, try to match by moduleId in lesson (fallback)
        if not lessons_by_ids:
            lessons_by_module_ref = [lesson for lesson in self.lessons
                                   if hasattr(lesson, 'moduleId') and lesson.moduleId == module_id]
            return lessons_by_module_ref

        return lessons_by_ids

    def get_items_for_lesson(self, lesson_id: str) -> List[CourseraContentItem]:
        """Get all items for a specific lesson."""
        lesson = self.get_lesson_by_id(lesson_id)
        if not lesson:
            return []

        # Use itemIds if available (direct item references)
        if lesson.itemIds:
            items_by_ids = [item for item in self.items if item.id in lesson.itemIds]
            # Set lesson reference for items
            for item in items_by_ids:
                if not item.lessonId:
                    item.lessonId = lesson_id
            return items_by_ids

        # Fallback to matching by lessonId in item
        return [item for item in self.items
                if hasattr(item, 'lessonId') and item.lessonId == lesson_id]

    @property
    def total_duration_minutes(self) -> float:
        """Calculate total course duration in minutes."""
        total = 0
        for module in self.modules:
            if module.timeCommitment:
                total += module.timeCommitment
        return total / 60000  # Convert from milliseconds

    @property
    def video_count(self) -> int:
        """Count total number of videos."""
        return len([item for item in self.items if item.content_type == "lecture"])

    @property
    def accessible_items_count(self) -> int:
        """Count accessible (unlocked) items."""
        return len([item for item in self.items if item.is_accessible])

    @property
    def total_items_by_type(self) -> Dict[str, int]:
        """Get count of items by content type."""
        type_counts = {}
        for item in self.items:
            content_type = item.content_type
            type_counts[content_type] = type_counts.get(content_type, 0) + 1
        return type_counts


class ComprehensiveCourseConverter:
    """Helper class to convert comprehensive API data to standard Course model."""

    @staticmethod
    def to_course(comprehensive_data: ComprehensiveCourseData, course_name: str, course_slug: str) -> Course:
        """Convert comprehensive API data to standard Course model."""
        course = Course(
            id=comprehensive_data.course_id,
            name=course_name,
            slug=course_slug,
            estimated_hours=comprehensive_data.total_duration_minutes / 60 if comprehensive_data.total_duration_minutes else None,
            metadata={
                "total_modules": len(comprehensive_data.modules),
                "total_lessons": len(comprehensive_data.lessons),
                "total_items": len(comprehensive_data.items),
                "video_count": comprehensive_data.video_count,
                "accessible_items": comprehensive_data.accessible_items_count,
                "api_source": "comprehensive_course_materials"
            }
        )

        # Convert modules
        for i, module_id in enumerate(comprehensive_data.module_ids):
            coursera_module = comprehensive_data.get_module_by_id(module_id)
            if not coursera_module:
                continue

            std_module = Module(
                id=coursera_module.id,
                name=coursera_module.name,
                description=coursera_module.description,
                order=i + 1,
                metadata={
                    "slug": coursera_module.slug,
                    "learning_objectives": coursera_module.learningObjectives,
                    "duration_minutes": coursera_module.duration_minutes,
                    "optional": coursera_module.optional
                }
            )

            # Convert lessons for this module
            coursera_lessons = comprehensive_data.get_lessons_for_module(module_id)
            for j, coursera_lesson in enumerate(coursera_lessons):
                std_lesson = Lesson(
                    id=coursera_lesson.id,
                    name=coursera_lesson.name,
                    order=j + 1,
                    duration_minutes=int(coursera_lesson.duration_minutes) if coursera_lesson.duration_minutes else None,
                    metadata={
                        "slug": coursera_lesson.slug,
                        "track_id": coursera_lesson.trackId,
                        "optional": coursera_lesson.optional,
                        "element_ids": coursera_lesson.elementIds,
                        "item_ids": coursera_lesson.itemIds
                    }
                )

                # Convert items for this lesson
                coursera_items = comprehensive_data.get_items_for_lesson(coursera_lesson.id)
                for k, coursera_item in enumerate(coursera_items):
                    # Only include accessible items
                    if not coursera_item.is_accessible:
                        continue

                    # Skip non-downloadable content types
                    content_type = coursera_item.content_type
                    if content_type in ['discussionPrompt', 'quiz', 'exam']:
                        continue

                    # Map to internal content type
                    internal_type = 'video' if content_type == 'lecture' else content_type

                    asset = ContentAsset(
                        name=f"{internal_type}_{coursera_item.id}",
                        file_type=internal_type,
                        metadata={
                            "original_name": coursera_item.originalName,
                            "slug": coursera_item.slug,
                            "content_summary": coursera_item.contentSummary.dict() if coursera_item.contentSummary else None,
                            "duration_minutes": coursera_item.duration_minutes,
                            "track_id": coursera_item.trackId,
                            "item_index": k,
                            "is_video": coursera_item.contentSummary.is_video if coursera_item.contentSummary else False,
                            "is_downloadable": coursera_item.contentSummary.is_downloadable if coursera_item.contentSummary else False,
                            "coursera_content_type": content_type,
                            "coursera_item": {
                                'id': coursera_item.id,
                                'slug': coursera_item.slug,
                                'content_type': content_type,
                                'is_video': coursera_item.contentSummary.is_video if coursera_item.contentSummary else False,
                                'duration': coursera_item.contentSummary.duration if coursera_item.contentSummary else None
                            }
                        }
                    )
                    std_lesson.assets.append(asset)

                std_module.lessons.append(std_lesson)

            course.modules.append(std_module)

        return course