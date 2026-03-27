#!/usr/bin/env python3
"""
Simple Video Lister - Shows all 33 videos clearly
"""

from pathlib import Path

course_path = Path("courses/business-english-intro")

print()
print("=" * 80)
print("ALL VIDEOS IN COURSE")
print("=" * 80)
print()

video_count = 0
for module_dir in sorted(course_path.glob("module-*")):
    if not module_dir.is_dir():
        continue

    module_num = int(module_dir.name.split('-')[1])
    print(f"\nModule {module_num}: {module_dir.name}")
    print("-" * 80)

    for lesson_dir in sorted([d for d in module_dir.glob("lesson-*") if d.is_dir()]):
        lesson_num = int(lesson_dir.name.split('-')[1])
        lecture_id = lesson_dir.name.split('-video-')[1].upper()

        video_file = lesson_dir / "video_720p.mp4"
        if video_file.exists():
            video_count += 1
            size_mb = video_file.stat().st_size / 1024 / 1024
            print(f"  {video_count:2d}. Lesson {lesson_num} ({lecture_id}): video_720p.mp4 [{size_mb:.1f} MB]")
        else:
            print(f"  XX. Lesson {lesson_num} ({lecture_id}): MISSING")

print()
print("=" * 80)
print(f"TOTAL: {video_count} videos found")
print("=" * 80)
print()

if video_count == 33:
    print("SUCCESS: All 33 videos are present!")
else:
    print(f"WARNING: Expected 33 videos, found {video_count}")
