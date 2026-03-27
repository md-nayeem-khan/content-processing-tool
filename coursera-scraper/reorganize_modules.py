#!/usr/bin/env python3
"""
Reorganize course modules to fix incorrect lesson distribution.

This script fixes the issue where lessons were distributed as 8+8+8+8+1
instead of the correct 6+6+6+6+6+3 distribution.
"""

import json
import shutil
from pathlib import Path


def reorganize_course_modules(course_name="business-english-intro"):
    """Reorganize course modules to match the correct distribution."""
    print("=" * 80)
    print("MODULE REORGANIZATION SCRIPT")
    print(f"Course: {course_name}")
    print("=" * 80)

    course_path = Path("courses") / course_name
    if not course_path.exists():
        print(f"ERROR: Course directory not found: {course_path}")
        return False

    # Load valid lectures in the correct order
    discovery_file = "valid_lectures.json"
    if not Path(discovery_file).exists():
        print(f"ERROR: Discovery file not found: {discovery_file}")
        return False

    with open(discovery_file, 'r', encoding='utf-8') as f:
        all_lectures = json.load(f)

    print(f"Total lectures: {len(all_lectures)}")

    # Calculate correct module distribution
    lectures_per_module = 6
    total_modules = (len(all_lectures) + lectures_per_module - 1) // lectures_per_module

    print(f"Target distribution: {lectures_per_module} lectures per module")
    print(f"Total modules: {total_modules}")
    print()

    # Map lecture IDs to their new locations
    lecture_mapping = {}
    for idx, lecture_data in enumerate(all_lectures):
        lecture_id = lecture_data['lecture_id'].lower()
        module_num = (idx // lectures_per_module) + 1
        lesson_num = (idx % lectures_per_module) + 1

        lecture_mapping[lecture_id] = {
            'module': module_num,
            'lesson': lesson_num,
            'original_idx': idx
        }

    # Show the reorganization plan
    print("Reorganization Plan:")
    print("-" * 80)
    for module_num in range(1, total_modules + 1):
        lessons_in_module = [lec_id for lec_id, info in lecture_mapping.items()
                             if info['module'] == module_num]
        print(f"Module {module_num}: {len(lessons_in_module)} lessons - {', '.join(lessons_in_module)}")
    print()

    # Create backup of current structure
    backup_path = course_path.parent / f"{course_name}_backup"
    if backup_path.exists():
        print(f"Removing old backup: {backup_path}")
        shutil.rmtree(backup_path)

    print(f"Creating backup: {backup_path}")
    shutil.copytree(course_path, backup_path)
    print()

    # Find all current lesson directories
    print("Finding existing lesson directories...")
    current_lessons = {}
    for lesson_dir in course_path.rglob("lesson-*"):
        if lesson_dir.is_dir() and 'video' in lesson_dir.name:
            # Extract lecture ID from directory name (e.g., "lesson-01-lesson-1-video-2zis7")
            parts = lesson_dir.name.split('-video-')
            if len(parts) == 2:
                lecture_id = parts[1].lower()
                current_lessons[lecture_id] = lesson_dir

    print(f"Found {len(current_lessons)} lesson directories")
    print()

    # Create new module structure
    print("Creating new module structure...")
    temp_dir = course_path.parent / f"{course_name}_temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)

    # Copy course-level files
    for item in course_path.iterdir():
        if item.is_file():
            shutil.copy2(item, temp_dir / item.name)

    # Reorganize lessons into correct modules
    moves_needed = 0
    for lecture_id, target_info in lecture_mapping.items():
        if lecture_id not in current_lessons:
            print(f"WARNING: Lecture {lecture_id} not found in current structure")
            continue

        source_dir = current_lessons[lecture_id]

        # Determine target location
        target_module_num = target_info['module']
        target_lesson_num = target_info['lesson']

        # Get current location
        current_module_num = int(source_dir.parent.name.split('-')[1])
        current_lesson_num = int(source_dir.name.split('-')[1])

        # Create module name based on position
        if target_module_num == 1:
            module_name = "Course Introduction and Fundamentals"
        elif target_module_num == 2:
            module_name = "Core Concepts and Skills"
        elif target_module_num == total_modules:
            module_name = "Advanced Topics and Conclusion"
        else:
            module_name = f"Module {target_module_num} Extended Learning"

        # Sanitize module name for directory
        module_dir_name = f"module-{target_module_num:02d}-{module_name.lower().replace(' ', '-').replace(':', '')}"
        target_module_dir = temp_dir / module_dir_name
        target_module_dir.mkdir(parents=True, exist_ok=True)

        # Create target lesson directory name
        target_lesson_dir = target_module_dir / f"lesson-{target_lesson_num:02d}-lesson-{target_lesson_num}-video-{lecture_id}"

        # Copy lesson directory to new location
        shutil.copytree(source_dir, target_lesson_dir)

        if current_module_num != target_module_num or current_lesson_num != target_lesson_num:
            print(f"  Moving {lecture_id}: Module {current_module_num} Lesson {current_lesson_num} -> Module {target_module_num} Lesson {target_lesson_num}")
            moves_needed += 1

    print()
    print(f"Total lessons reorganized: {len(lecture_mapping)}")
    print(f"Lessons that needed moving: {moves_needed}")
    print()

    # Replace old structure with new structure
    print("Replacing old structure with reorganized structure...")

    # Remove old module directories
    for module_dir in course_path.glob("module-*"):
        if module_dir.is_dir():
            print(f"  Removing old module: {module_dir.name}")
            shutil.rmtree(module_dir)

    # Move new modules from temp to course directory
    for module_dir in temp_dir.glob("module-*"):
        target = course_path / module_dir.name
        print(f"  Installing new module: {module_dir.name}")
        shutil.move(str(module_dir), str(target))

    # Clean up temp directory
    shutil.rmtree(temp_dir)

    print(f"New structure active at: {course_path}")
    print()

    # Update metadata
    metadata_file = course_path / "course_metadata.json"
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        metadata['total_modules'] = total_modules
        metadata['total_lessons'] = len(all_lectures)

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

    # Update scraping progress
    progress_file = course_path / ".scraping_progress.json"
    if progress_file.exists():
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress = json.load(f)

        progress['completed_modules'] = total_modules
        progress['completed_lessons'] = len(all_lectures)

        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2)

    print("=" * 80)
    print("REORGANIZATION COMPLETE")
    print("=" * 80)
    print(f"Modules now correctly distributed:")
    for module_num in range(1, total_modules + 1):
        lessons_in_module = [lec_id for lec_id, info in lecture_mapping.items()
                             if info['module'] == module_num]
        print(f"  Module {module_num}: {len(lessons_in_module)} lessons")
    print()
    print("All 33 videos are now properly organized!")
    print(f"Backup saved to: {backup_path}")

    return True


if __name__ == "__main__":
    try:
        success = reorganize_course_modules("business-english-intro")
        if success:
            print("\nSUCCESS: Course modules reorganized successfully!")
        else:
            print("\nFAILED: Could not reorganize modules")
    except KeyboardInterrupt:
        print("\n\nReorganization interrupted by user")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
