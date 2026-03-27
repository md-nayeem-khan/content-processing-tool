#!/usr/bin/env python3
"""
Reorganize Course Using Actual Coursera API Structure

Based on the onDemandCourseMaterials.v2 API response provided,
reorganize videos to match the TRUE Coursera structure:
- 5 Modules (not 6)
- 16 Lessons (not 33)
- Multiple videos per lesson (where applicable)
"""

import json
import shutil
from pathlib import Path
from datetime import datetime


def get_proper_course_structure():
    """Return the proper course structure based on the API response."""
    return {
        "course_id": "46b4tHEkEeWbbw5cIAKQrw",
        "course_slug": "business-english-intro",
        "modules": [
            {
                "id": "kShsa",
                "name": "Introduction to Business English Communication",
                "slug": "introduction-to-business-english-communication",
                "order": 1,
                "lessons": [
                    {
                        "id": "6tymr",
                        "name": "Lesson 1: Course Overview and Assessment",
                        "slug": "lesson-1-course-overview-and-assessment",
                        "order": 1,
                        "video_ids": ["DKbsC", "2Zis7", "6AM0l"]
                    },
                    {
                        "id": "UH8Ib",
                        "name": "Lesson 2: Introducing Yourself in Business Settings",
                        "slug": "lesson-2-introducing-yourself-in-business-settings",
                        "order": 2,
                        "video_ids": ["bH0qh", "QiPZC", "wJTyA", "7gTSM"]
                    },
                    {
                        "id": "75JFA",
                        "name": "Lesson 3: Making Contact - 38 mins",
                        "slug": "lesson-3-making-contact-38-mins",
                        "order": 3,
                        "video_ids": ["pLuLp", "5zSSJ", "NSjd8"]
                    }
                ]
            },
            {
                "id": "IydAU",
                "name": "Introductions",
                "slug": "introductions",
                "order": 2,
                "lessons": [
                    {
                        "id": "ayqrn",
                        "name": "Lesson 4: Case Study: Seattle",
                        "slug": "lesson-4-case-study-seattle",
                        "order": 4,
                        "video_ids": ["eIPPs", "fCQQo", "klTB2"]
                    },
                    {
                        "id": "n7Ivq",
                        "name": "Lesson 5: My Job",
                        "slug": "lesson-5-my-job",
                        "order": 5,
                        "video_ids": ["jYE3B", "sVCxj"]
                    },
                    {
                        "id": "ZOAdj",
                        "name": "Lesson 6: Describing A Company",
                        "slug": "lesson-6-describing-a-company",
                        "order": 6,
                        "video_ids": ["PTixY", "Wkvsz"]
                    }
                ]
            },
            {
                "id": "Wp2Wp",
                "name": "Emails",
                "slug": "emails",
                "order": 3,
                "lessons": [
                    {
                        "id": "JjUvs",
                        "name": "Lesson 7: Email Etiquette: Part 1",
                        "slug": "lesson-7-email-etiquette-part-1",
                        "order": 7,
                        "video_ids": ["sf1NL", "XAr7X", "bnqX2", "xH3Nv"]
                    },
                    {
                        "id": "ugJ8A",
                        "name": "Lesson 8: Email Etiquette: Part 2",
                        "slug": "lesson-8-email-etiquette-part-2",
                        "order": 8,
                        "video_ids": ["FEaDM", "j0ADX", "NwLNC", "x172v"]
                    },
                    {
                        "id": "HhcLS",
                        "name": "Lesson 9: Email Etiquette: Part 3",
                        "slug": "lesson-9-email-etiquette-part-3",
                        "order": 9,
                        "video_ids": ["DvkSK", "Z0yEA"]
                    },
                    {
                        "id": "mn0E3",
                        "name": "Activities",
                        "slug": "activities",
                        "order": 10,
                        "video_ids": []  # No videos, just assignments
                    }
                ]
            },
            {
                "id": "ICmov",
                "name": "Meeting Arrangements on the Telephone",
                "slug": "meeting-arrangements-on-the-telephone",
                "order": 4,
                "lessons": [
                    {
                        "id": "qIj7v",
                        "name": "Lesson 10: Beginning and Ending a Telephone Call",
                        "slug": "lesson-10-beginning-and-ending-a-telephone-call",
                        "order": 11,  # Global lesson order
                        "video_ids": ["MpV97"]
                    },
                    {
                        "id": "I16Hh",
                        "name": "Lesson 11: Making Arrangements",
                        "slug": "lesson-11-making-arrangements",
                        "order": 12,
                        "video_ids": ["5rKWY"]
                    },
                    {
                        "id": "c04ZD",
                        "name": "Lesson 12: Leaving Messages",
                        "slug": "lesson-12-leaving-messages",
                        "order": 13,
                        "video_ids": ["XeAJa"]
                    }
                ]
            },
            {
                "id": "1PNv2",
                "name": "Meeting Arrangements (Email)",
                "slug": "meeting-arrangements-email",
                "order": 5,
                "lessons": [
                    {
                        "id": "bHpPe",
                        "name": "Lesson 13: Text Messages in Meeting Arrangements",
                        "slug": "lesson-13-text-messages-in-meeting-arrangements",
                        "order": 14,
                        "video_ids": ["wBcVr"]
                    },
                    {
                        "id": "WqILh",
                        "name": "Lesson 14: Invitation in Email",
                        "slug": "lesson-14-invitation-in-email",
                        "order": 15,
                        "video_ids": ["NBpj7"]
                    },
                    {
                        "id": "eJS5q",
                        "name": "Lesson 15: Replying to Invitation Emails",
                        "slug": "lesson-15-replying-to-invitation-emails",
                        "order": 16,
                        "video_ids": []  # No videos
                    },
                    {
                        "id": "24DuO",
                        "name": "Lesson 16: Follow-Up Email",
                        "slug": "lesson-16-follow-up-email",
                        "order": 17,
                        "video_ids": ["HmpP1"]
                    }
                ]
            }
        ]
    }


def find_existing_videos(course_path):
    """Find all existing video files and map them by video ID."""
    existing_videos = {}

    for video_file in course_path.rglob("*.mp4"):
        # Extract video ID from folder name
        folder_name = video_file.parent.name
        if '-video-' in folder_name:
            video_id = folder_name.split('-video-')[1].lower()
            existing_videos[video_id] = video_file

    return existing_videos


def reorganize_to_proper_structure(course_name="business-english-intro"):
    """Reorganize course to match proper Coursera structure."""
    print("=" * 100)
    print("REORGANIZING TO PROPER COURSERA STRUCTURE")
    print("=" * 100)
    print()

    course_path = Path("courses") / course_name
    if not course_path.exists():
        print(f"ERROR: Course not found: {course_path}")
        return False

    # Get proper structure
    structure = get_proper_course_structure()
    print(f"Target structure:")
    print(f"  Course: {structure['course_slug']}")
    print(f"  Modules: {len(structure['modules'])}")
    total_lessons = sum(len(m['lessons']) for m in structure['modules'])
    total_videos = sum(len(lesson['video_ids'])
                      for module in structure['modules']
                      for lesson in module['lessons'])
    print(f"  Lessons: {total_lessons}")
    print(f"  Videos: {total_videos}")
    print()

    # Find existing videos
    existing_videos = find_existing_videos(course_path)
    print(f"Found {len(existing_videos)} existing video files")
    print()

    # Create backup
    backup_path = Path("courses") / f"{course_name}_old"
    if backup_path.exists():
        shutil.rmtree(backup_path)
    print(f"Creating backup: {backup_path}")
    shutil.copytree(course_path, backup_path)
    print()

    # Create new structure
    new_path = Path("courses") / f"{course_name}_proper"
    if new_path.exists():
        shutil.rmtree(new_path)
    new_path.mkdir(parents=True)

    # Copy course-level files
    for item in course_path.iterdir():
        if item.is_file():
            shutil.copy2(item, new_path / item.name)

    # Create proper module structure
    missing_videos = []
    success_count = 0

    for module in structure['modules']:
        print(f"Creating Module {module['order']}: {module['name']}")

        # Create module directory
        module_dir_name = f"module-{module['order']:02d}-{module['slug']}"
        module_dir = new_path / module_dir_name
        module_dir.mkdir(parents=True)

        # Module metadata
        module_metadata = {
            'id': module['id'],
            'name': module['name'],
            'slug': module['slug'],
            'order': module['order'],
            'lesson_count': len(module['lessons'])
        }
        with open(module_dir / "module_metadata.json", 'w') as f:
            json.dump(module_metadata, f, indent=2)

        for lesson in module['lessons']:
            lesson_order_in_module = lesson['order'] - (module['order'] - 1) * 4  # Approximate
            lesson_dir_name = f"lesson-{lesson_order_in_module:02d}-{lesson['slug']}"
            lesson_dir = module_dir / lesson_dir_name
            lesson_dir.mkdir(parents=True)

            print(f"  Lesson {lesson['order']}: {lesson['name']} ({len(lesson['video_ids'])} videos)")

            # Lesson metadata
            lesson_metadata = {
                'id': lesson['id'],
                'name': lesson['name'],
                'slug': lesson['slug'],
                'order': lesson['order'],
                'module_id': module['id'],
                'video_count': len(lesson['video_ids'])
            }
            with open(lesson_dir / "lesson_metadata.json", 'w') as f:
                json.dump(lesson_metadata, f, indent=2)

            # Copy videos for this lesson
            videos_copied = 0
            for video_idx, video_id in enumerate(lesson['video_ids'], 1):
                video_id_lower = video_id.lower()
                if video_id_lower in existing_videos:
                    source_path = existing_videos[video_id_lower]
                    target_name = f"video_{video_idx}_{video_id_lower}.mp4"
                    target_path = lesson_dir / target_name

                    # Copy video file
                    shutil.copy2(source_path, target_path)
                    videos_copied += 1
                    success_count += 1

                    # Copy associated files from source lesson directory
                    source_dir = source_path.parent
                    for associated_file in source_dir.glob("*"):
                        if associated_file != source_path and associated_file.is_file():
                            target_file = lesson_dir / f"{video_id_lower}_{associated_file.name}"
                            shutil.copy2(associated_file, target_file)

                    print(f"    ✓ Copied: {video_id}")
                else:
                    missing_videos.append(video_id)
                    print(f"    ✗ Missing: {video_id}")

            if len(lesson['video_ids']) == 0:
                print(f"    ℹ No videos (assignments/activities only)")

        print()

    # Save complete structure
    with open(new_path / "proper_structure.json", 'w') as f:
        json.dump(structure, f, indent=2)

    print("=" * 100)
    print("REORGANIZATION COMPLETE")
    print("=" * 100)
    print()
    print(f"Videos successfully copied: {success_count}/{total_videos}")
    if missing_videos:
        print(f"Missing videos: {missing_videos}")
    print()
    print(f"New structure: {new_path}")
    print(f"Old structure backed up: {backup_path}")
    print()
    print("To activate new structure:")
    print(f"  1. Review: {new_path}")
    print(f"  2. If satisfied: rm -rf {course_path} && mv {new_path} {course_path}")

    return success_count == total_videos


def main():
    """Main execution."""
    print("COURSERA PROPER STRUCTURE REORGANIZER")
    print("Based on onDemandCourseMaterials.v2 API")
    print()

    success = reorganize_to_proper_structure("business-english-intro")

    if success:
        print("\n🎉 SUCCESS: All videos reorganized to proper Coursera structure!")
    else:
        print("\n⚠️ WARNING: Some videos may be missing")

    return success


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()