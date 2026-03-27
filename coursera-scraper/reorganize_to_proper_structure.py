#!/usr/bin/env python3
"""
Reorganize Course Using Proper Coursera API Structure

This script fetches the proper course structure from the onDemandCourseMaterials.v2 API
and reorganizes the existing videos to match the real Coursera hierarchy:
- 5 Modules (not 6)
- 17 Lessons (not 33)
- Each lesson contains multiple videos + other materials
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List
from datetime import datetime


def fetch_proper_course_structure(course_slug: str = "business-english-intro"):
    """Fetch proper course structure from Coursera API."""
    print("=" * 100)
    print("FETCHING PROPER COURSE STRUCTURE FROM COURSERA API")
    print("=" * 100)
    print()

    # Import API client
    from src.config.settings import ConfigManager
    from src.api.auth import CourseraAuth
    from src.api.coursera_client import CourseraClient

    # Setup authentication and client
    auth = CourseraAuth()
    if not auth.is_authenticated():
        print("ERROR: Authentication failed. Check your COURSERA_CAUTH_COOKIE in .env")
        return None

    client = CourseraClient.from_config_file("config/api_endpoints.json", auth)

    # Fetch course materials
    print(f"Fetching course materials for: {course_slug}")
    materials = client.get_course_materials(course_slug)

    if not materials or 'elements' not in materials:
        print("ERROR: Failed to fetch course materials")
        return None

    # Parse the structure
    course_id = materials['elements'][0]['id']
    module_ids = materials['elements'][0]['moduleIds']

    modules_data = materials['linked']['onDemandCourseMaterialModules.v1']
    lessons_data = materials['linked']['onDemandCourseMaterialLessons.v1']
    items_data = materials['linked']['onDemandCourseMaterialItems.v2']

    # Build lookup dictionaries
    lessons_by_id = {lesson['id']: lesson for lesson in lessons_data}
    items_by_id = {item['id']: item for item in items_data}

    # Organize structure
    structure = {
        'course_id': course_id,
        'course_slug': course_slug,
        'modules': []
    }

    for module_idx, module_id in enumerate(module_ids, 1):
        # Find module data
        module = next((m for m in modules_data if m['id'] == module_id), None)
        if not module:
            continue

        module_info = {
            'id': module['id'],
            'name': module['name'],
            'slug': module['slug'],
            'order': module_idx,
            'lessons': []
        }

        # Add lessons to module
        for lesson_idx, lesson_id in enumerate(module['lessonIds'], 1):
            lesson = lessons_by_id.get(lesson_id)
            if not lesson:
                continue

            # Get items for this lesson
            lesson_items = []
            for item_id in lesson.get('itemIds', []):
                item = items_by_id.get(item_id)
                if item:
                    item_type = item.get('contentSummary', {}).get('typeName', 'unknown')
                    lesson_items.append({
                        'id': item_id,
                        'name': item.get('name', ''),
                        'type': item_type,
                        'slug': item.get('slug', ''),
                        'is_video': item_type == 'lecture'
                    })

            lesson_info = {
                'id': lesson['id'],
                'name': lesson['name'],
                'slug': lesson['slug'],
                'order': lesson_idx,
                'items': lesson_items,
                'video_count': sum(1 for item in lesson_items if item['is_video'])
            }

            module_info['lessons'].append(lesson_info)

        structure['modules'].append(module_info)

    return structure


def map_videos_to_structure(structure: Dict, current_course_path: Path) -> Dict[str, List[str]]:
    """Map existing video files to their proper locations in the new structure."""
    print()
    print("=" * 100)
    print("MAPPING EXISTING VIDEOS TO PROPER STRUCTURE")
    print("=" * 100)
    print()

    video_mapping = {}  # video_id -> list of paths where it should be

    # Find all existing video files
    existing_videos = {}
    for video_file in current_course_path.rglob("*.mp4"):
        # Extract video ID from folder name (e.g., "lesson-01-video-2zis7" -> "2zis7")
        folder_name = video_file.parent.name
        if '-video-' in folder_name:
            video_id = folder_name.split('-video-')[1].lower()
            existing_videos[video_id] = video_file

    print(f"Found {len(existing_videos)} existing video files")
    print()

    # For each module and lesson in proper structure, note which videos should be there
    videos_found = 0
    videos_missing = 0

    for module in structure['modules']:
        for lesson in module['lessons']:
            lesson_videos = [item for item in lesson['items'] if item['is_video']]

            if lesson_videos:
                print(f"Module {module['order']}, Lesson {lesson['order']}: {lesson['name']}")
                print(f"  Should contain {len(lesson_videos)} videos:")

                for item in lesson_videos:
                    video_id = item['id'].lower()
                    if video_id in existing_videos:
                        print(f"    ✓ Found: {video_id} ({item['name']})")
                        videos_found += 1

                        # Record where this video should go
                        if video_id not in video_mapping:
                            video_mapping[video_id] = []
                        video_mapping[video_id].append({
                            'module': module,
                            'lesson': lesson,
                            'item': item,
                            'source_path': existing_videos[video_id]
                        })
                    else:
                        print(f"    ✗ Missing: {video_id} ({item['name']})")
                        videos_missing += 1

                print()

    print(f"Summary: {videos_found} videos found, {videos_missing} videos missing")
    print()

    return video_mapping


def reorganize_course(structure: Dict, video_mapping: Dict, course_name: str = "business-english-intro"):
    """Reorganize course to match proper Coursera structure."""
    print("=" * 100)
    print("REORGANIZING COURSE TO PROPER STRUCTURE")
    print("=" * 100)
    print()

    course_path = Path("courses") / course_name
    backup_path = Path("courses") / f"{course_name}_old_structure"

    # Create backup
    if backup_path.exists():
        print(f"Removing old backup: {backup_path}")
        shutil.rmtree(backup_path)

    print(f"Creating backup: {backup_path}")
    shutil.copytree(course_path, backup_path)
    print()

    # Create new structure
    new_course_path = Path("courses") / f"{course_name}_proper_structure"
    if new_course_path.exists():
        shutil.rmtree(new_course_path)
    new_course_path.mkdir(parents=True)

    # Copy course-level files
    for item in course_path.iterdir():
        if item.is_file():
            shutil.copy2(item, new_course_path / item.name)

    # Create proper module and lesson structure
    for module in structure['modules']:
        # Create module directory
        module_dir_name = f"module-{module['order']:02d}-{module['slug']}"
        module_dir = new_course_path / module_dir_name
        module_dir.mkdir(parents=True)

        # Save module metadata
        module_metadata = {
            'id': module['id'],
            'name': module['name'],
            'order': module['order'],
            'lesson_count': len(module['lessons'])
        }
        with open(module_dir / "module_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(module_metadata, f, indent=2)

        print(f"Module {module['order']}: {module['name']}")

        for lesson in module['lessons']:
            # Create lesson directory
            lesson_dir_name = f"lesson-{lesson['order']:02d}-{lesson['slug']}"
            lesson_dir = module_dir / lesson_dir_name
            lesson_dir.mkdir(parents=True)

            # Save lesson metadata
            lesson_metadata = {
                'id': lesson['id'],
                'name': lesson['name'],
                'order': lesson['order'],
                'module_id': module['id'],
                'video_count': lesson['video_count'],
                'total_items': len(lesson['items'])
            }
            with open(lesson_dir / "lesson_metadata.json", 'w', encoding='utf-8') as f:
                json.dump(lesson_metadata, f, indent=2)

            # Copy all videos for this lesson
            lesson_videos = [item for item in lesson['items'] if item['is_video']]
            videos_copied = 0

            for item in lesson_videos:
                video_id = item['id'].lower()
                if video_id in video_mapping:
                    mappings = video_mapping[video_id]
                    for mapping in mappings:
                        if (mapping['module']['id'] == module['id'] and
                            mapping['lesson']['id'] == lesson['id']):

                            source_path = mapping['source_path']
                            if source_path.exists():
                                # Copy video file
                                target_name = f"video_{videos_copied + 1}_{video_id}.mp4"
                                target_path = lesson_dir / target_name
                                shutil.copy2(source_path, target_path)
                                videos_copied += 1

                                # Copy associated files (metadata, URLs, etc.)
                                source_dir = source_path.parent
                                for associated_file in source_dir.glob("*"):
                                    if associated_file != source_path and associated_file.is_file():
                                        assoc_target = lesson_dir / f"{video_id}_{associated_file.name}"
                                        shutil.copy2(associated_file, assoc_target)

            print(f"  Lesson {lesson['order']}: {lesson['name']} - {videos_copied} videos copied")

        print()

    # Save full structure metadata
    structure_file = new_course_path / "proper_structure.json"
    with open(structure_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2)

    print("=" * 100)
    print("REORGANIZATION COMPLETE")
    print("=" * 100)
    print()
    print(f"New structure created at: {new_course_path}")
    print(f"Old structure backed up at: {backup_path}")
    print()
    print("To use the new structure:")
    print(f"  1. Review the new structure in: {new_course_path}")
    print(f"  2. If satisfied, rename:")
    print(f"     mv {new_course_path} {course_path}")
    print()


def main():
    """Main execution."""
    course_slug = "business-english-intro"

    # Step 1: Fetch proper structure from API
    structure = fetch_proper_course_structure(course_slug)
    if not structure:
        print("Failed to fetch course structure")
        return False

    # Print structure summary
    print()
    print("PROPER COURSERA STRUCTURE:")
    print("-" * 100)
    print(f"Course: {structure['course_slug']} (ID: {structure['course_id']})")
    print(f"Modules: {len(structure['modules'])}")
    total_lessons = sum(len(m['lessons']) for m in structure['modules'])
    total_videos = sum(lesson['video_count']
                      for module in structure['modules']
                      for lesson in module['lessons'])
    print(f"Lessons: {total_lessons}")
    print(f"Total Videos: {total_videos}")
    print()

    for module in structure['modules']:
        lesson_count = len(module['lessons'])
        video_count = sum(lesson['video_count'] for lesson in module['lessons'])
        print(f"  Module {module['order']}: {module['name']} ({lesson_count} lessons, {video_count} videos)")

    # Step 2: Map existing videos
    course_path = Path("courses") / course_slug
    if not course_path.exists():
        print(f"\nERROR: Course directory not found: {course_path}")
        return False

    video_mapping = map_videos_to_structure(structure, course_path)

    # Step 3: Reorganize
    reorganize_course(structure, video_mapping, course_slug)

    return True


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\nSUCCESS: Course reorganized to proper Coursera structure!")
        else:
            print("\nFAILED: Could not reorganize course")
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
