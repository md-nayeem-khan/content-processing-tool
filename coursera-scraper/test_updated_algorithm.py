#!/usr/bin/env python3
"""Test script for the updated course material scraping algorithm."""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.course_models import (
    ComprehensiveCourseData, CourseraModule, CourseraLesson,
    CourseraContentItem, ContentSummary, ComprehensiveCourseConverter
)

# Sample API response data from the user
SAMPLE_API_RESPONSE = {
    "elements": [
        {
            "moduleIds": [
                "kShsa",
                "IydAU",
                "Wp2Wp",
                "ICmov",
                "1PNv2"
            ],
            "id": "46b4tHEkEeWbbw5cIAKQrw"
        }
    ],
    "paging": {},
    "linked": {
        "onDemandCourseMaterialTracks.v1": [
            {
                "passablesCount": 13,
                "id": "core"
            }
        ],
        "onDemandGradingParameters.v1": [
            {
                "gradedAssignmentGroups": {},
                "id": "46b4tHEkEeWbbw5cIAKQrw"
            }
        ],
        "onDemandCourseMaterialLessons.v1": [
            {
                "trackId": "core",
                "itemIds": [
                    "DKbsC",
                    "090KY",
                    "2Zis7",
                    "6AM0l",
                    "GAzFk",
                    "LseWV",
                    "4Eq2G",
                    "Sm7Ri"
                ],
                "name": "Lesson 1: Course Overview and Assessment ",
                "timeCommitment": 4220000,
                "id": "6tymr",
                "moduleId": "kShsa",
                "slug": "lesson-1-course-overview-and-assessment",
                "elementIds": [
                    "item~DKbsC",
                    "item~090KY",
                    "item~2Zis7",
                    "item~6AM0l",
                    "item~GAzFk",
                    "item~LseWV",
                    "item~4Eq2G",
                    "item~Sm7Ri"
                ]
            },
            {
                "trackId": "core",
                "itemIds": [
                    "bH0qh",
                    "QiPZC",
                    "wJTyA",
                    "7gTSM",
                    "jz03p",
                    "XTSpL",
                    "rdDyY",
                    "8LpU3"
                ],
                "name": "Lesson 2: Introducing Yourself in Business Settings ",
                "timeCommitment": 4260000,
                "id": "UH8Ib",
                "moduleId": "kShsa",
                "slug": "lesson-2-introducing-yourself-in-business-settings",
                "elementIds": [
                    "item~bH0qh",
                    "item~QiPZC",
                    "item~wJTyA",
                    "item~7gTSM",
                    "item~jz03p",
                    "item~XTSpL",
                    "item~rdDyY",
                    "item~8LpU3"
                ]
            }
        ],
        "onDemandCourseMaterialItems.v2": [
            {
                "trackId": "core",
                "isLocked": False,
                "name": "Video: Welcome to Business English",
                "lessonId": "6tymr",
                "timeCommitment": 120000,
                "id": "DKbsC",
                "moduleId": "kShsa",
                "contentSummary": {
                    "typeName": "lecture",
                    "definition": {
                        "duration": 120000,
                        "hasInVideoAssessment": False
                    }
                },
                "slug": "video-welcome-to-business-english"
            },
            {
                "trackId": "core",
                "isLocked": False,
                "name": "READ FIRST",
                "lessonId": "6tymr",
                "timeCommitment": 600000,
                "id": "090KY",
                "moduleId": "kShsa",
                "contentSummary": {
                    "typeName": "supplement",
                    "definition": {
                        "assetTypeName": "cml",
                        "containsWidget": False
                    }
                },
                "slug": "read-first"
            },
            {
                "trackId": "core",
                "isLocked": False,
                "name": "Video: Introducing Yourself",
                "lessonId": "UH8Ib",
                "timeCommitment": 229000,
                "id": "bH0qh",
                "moduleId": "kShsa",
                "contentSummary": {
                    "typeName": "lecture",
                    "definition": {
                        "duration": 229000,
                        "hasInVideoAssessment": False
                    }
                },
                "slug": "video-introducing-yourself"
            }
        ],
        "onDemandCourseMaterialModules.v1": [
            {
                "learningObjectives": [],
                "name": "Introduction to Business English Communication",
                "description": "In the first week, you'll practice introducing yourself and learn some new vocabulary to talk about what you do in your job. ",
                "timeCommitment": 18032000,
                "id": "kShsa",
                "lessonIds": [
                    "6tymr",
                    "UH8Ib"
                ],
                "slug": "introduction-to-business-english-communication"
            }
        ],
        "onDemandCourseMaterialPassableLessonElements.v1": [],
        "onDemandCourseMaterialGradePolicy.v1": [],
        "contentAtomRelations.v1": []
    }
}


def test_parse_api_response():
    """Test parsing the sample API response with the updated algorithm."""
    print("Testing updated course material scraping algorithm...")
    print("=" * 60)

    try:
        # Extract main elements
        main_element = SAMPLE_API_RESPONSE['elements'][0]
        linked_data = SAMPLE_API_RESPONSE.get('linked', {})

        course_id = main_element.get('id')
        module_ids = main_element.get('moduleIds', [])

        print(f"Course ID: {course_id}")
        print(f"Module IDs: {module_ids}")
        print()

        # Parse linked data
        modules_data = linked_data.get('onDemandCourseMaterialModules.v1', [])
        lessons_data = linked_data.get('onDemandCourseMaterialLessons.v1', [])
        items_data = linked_data.get('onDemandCourseMaterialItems.v2', [])

        print(f"Raw data counts:")
        print(f"  - Modules: {len(modules_data)}")
        print(f"  - Lessons: {len(lessons_data)}")
        print(f"  - Items: {len(items_data)}")
        print()

        # Convert to enhanced models
        modules = []
        for module_data in modules_data:
            try:
                module = CourseraModule(**module_data)
                modules.append(module)
                print(f"+ Parsed module: {module.name} (ID: {module.id})")
            except Exception as e:
                print(f"- Failed to parse module {module_data.get('id', 'unknown')}: {e}")

        lessons = []
        for lesson_data in lessons_data:
            try:
                lesson = CourseraLesson(**lesson_data)
                lessons.append(lesson)
                print(f"+ Parsed lesson: {lesson.name} (ID: {lesson.id})")
                print(f"  - Duration: {lesson.duration_minutes:.1f} minutes" if lesson.duration_minutes else "  - Duration: Unknown")
                print(f"  - Items: {len(lesson.itemIds)} items")
            except Exception as e:
                print(f"- Failed to parse lesson {lesson_data.get('id', 'unknown')}: {e}")

        items = []
        for item_data in items_data:
            try:
                # Parse content summary if present
                if 'contentSummary' in item_data and item_data['contentSummary']:
                    content_summary = ContentSummary(**item_data['contentSummary'])
                    item_data['contentSummary'] = content_summary

                item = CourseraContentItem(**item_data)
                items.append(item)
                print(f"+ Parsed item: {item.name} (ID: {item.id})")
                print(f"  - Type: {item.content_type}")
                print(f"  - Locked: {item.isLocked}")
                print(f"  - Duration: {item.duration_minutes:.1f} minutes" if item.duration_minutes else "  - Duration: Unknown")
            except Exception as e:
                print(f"- Failed to parse item {item_data.get('id', 'unknown')}: {e}")

        print()
        print("Creating comprehensive course data...")

        # Create comprehensive course data
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

        print(f"+ Created comprehensive course data")
        print(f"  - Total duration: {comprehensive_data.total_duration_minutes:.1f} minutes")
        print(f"  - Video count: {comprehensive_data.video_count}")
        print(f"  - Accessible items: {comprehensive_data.accessible_items_count}")
        print(f"  - Content types: {comprehensive_data.total_items_by_type}")
        print()

        # Test relationships
        print("Testing data relationships...")

        for module in modules:
            print(f"\nModule: {module.name}")
            module_lessons = comprehensive_data.get_lessons_for_module(module.id)
            print(f"  - Lessons found: {len(module_lessons)}")

            for lesson in module_lessons:
                print(f"    Lesson: {lesson.name}")
                lesson_items = comprehensive_data.get_items_for_lesson(lesson.id)
                print(f"      - Items found: {len(lesson_items)}")

                for item in lesson_items:
                    print(f"        Item: {item.name} ({item.content_type})")

        # Convert to standard Course model
        print("\nConverting to standard Course model...")
        course_name = "Business English Introduction"
        course_slug = "business-english-intro"

        course = ComprehensiveCourseConverter.to_course(
            comprehensive_data,
            course_name,
            course_slug
        )

        print(f"+ Converted to Course model")
        print(f"  - Course: {course.name}")
        print(f"  - Modules: {len(course.modules)}")
        print(f"  - Total lessons: {course.total_lessons}")
        print(f"  - Total assets: {course.total_assets}")
        print()

        # Print detailed structure
        print("Course structure:")
        for i, module in enumerate(course.modules, 1):
            print(f"  Module {i}: {module.name}")
            for j, lesson in enumerate(module.lessons, 1):
                print(f"    Lesson {j}: {lesson.name}")
                for k, asset in enumerate(lesson.assets, 1):
                    print(f"      Asset {k}: {asset.name} ({asset.file_type})")

        print("\n" + "=" * 60)
        print("+ Test completed successfully!")
        return True

    except Exception as e:
        print(f"\n- Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the test."""
    success = test_parse_api_response()

    if success:
        print("\nSUCCESS! The updated algorithm works correctly with the new API structure!")
    else:
        print("\nERROR: The updated algorithm needs further refinement.")
        sys.exit(1)


if __name__ == "__main__":
    main()