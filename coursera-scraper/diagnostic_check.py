#!/usr/bin/env python3
"""
Comprehensive Diagnostic Tool for Coursera Scraper

This script performs a deep analysis of the course structure and identifies any issues:
- Missing videos or metadata files
- Incorrect module distribution
- File integrity problems
- Accessibility issues
"""

import json
from pathlib import Path
from datetime import datetime


def diagnostic_report(course_name="business-english-intro"):
    """Generate comprehensive diagnostic report."""
    print("=" * 100)
    print(" " * 30 + "COURSERA SCRAPER DIAGNOSTIC REPORT")
    print("=" * 100)
    print(f"Course: {course_name}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    print()

    course_path = Path("courses") / course_name
    if not course_path.exists():
        print(f"[FATAL] Course directory not found: {course_path}")
        return False

    # === SECTION 1: MODULE STRUCTURE ANALYSIS ===
    print("1. MODULE STRUCTURE ANALYSIS")
    print("-" * 100)

    modules = sorted([d for d in course_path.glob("module-*") if d.is_dir()])
    print(f"   Total Modules: {len(modules)}")
    print()

    module_data = []
    for module_dir in modules:
        module_num = int(module_dir.name.split('-')[1])
        lesson_dirs = sorted([d for d in module_dir.glob("lesson-*") if d.is_dir()])

        module_info = {
            'num': module_num,
            'name': module_dir.name,
            'lesson_count': len(lesson_dirs),
            'lessons': []
        }

        for lesson_dir in lesson_dirs:
            lesson_num = int(lesson_dir.name.split('-')[1])
            lecture_id = lesson_dir.name.split('-video-')[1] if '-video-' in lesson_dir.name else 'UNKNOWN'

            video_files = list(lesson_dir.glob("*.mp4"))
            has_metadata = (lesson_dir / "lesson_metadata.json").exists()
            has_urls = (lesson_dir / "content_urls.txt").exists()

            module_info['lessons'].append({
                'num': lesson_num,
                'id': lecture_id,
                'path': lesson_dir.name,
                'has_video': len(video_files) > 0,
                'video_count': len(video_files),
                'has_metadata': has_metadata,
                'has_urls': has_urls
            })

        module_data.append(module_info)

        # Print module summary
        videos_in_module = sum(1 for l in module_info['lessons'] if l['has_video'])
        print(f"   Module {module_num:2d}: {len(lesson_dirs)} lessons, {videos_in_module} videos")

    print()

    # === SECTION 2: LESSON INTEGRITY CHECK ===
    print("2. LESSON INTEGRITY CHECK")
    print("-" * 100)

    total_lessons = sum(len(m['lessons']) for m in module_data)
    lessons_with_videos = sum(1 for m in module_data for l in m['lessons'] if l['has_video'])
    lessons_with_metadata = sum(1 for m in module_data for l in m['lessons'] if l['has_metadata'])
    lessons_with_urls = sum(1 for m in module_data for l in m['lessons'] if l['has_urls'])

    print(f"   Total Lessons: {total_lessons}")
    print(f"   Lessons with Videos: {lessons_with_videos}/{total_lessons}")
    print(f"   Lessons with Metadata: {lessons_with_metadata}/{total_lessons}")
    print(f"   Lessons with URLs: {lessons_with_urls}/{total_lessons}")
    print()

    # Check for problems
    problems = []
    for module in module_data:
        for lesson in module['lessons']:
            issues = []
            if not lesson['has_video']:
                issues.append("NO VIDEO")
            if not lesson['has_metadata']:
                issues.append("NO METADATA")
            if not lesson['has_urls']:
                issues.append("NO URLS")

            if issues:
                problems.append({
                    'module': module['num'],
                    'lesson': lesson['num'],
                    'id': lesson['id'],
                    'issues': issues
                })

    if problems:
        print(f"   [WARNING] {len(problems)} lessons have issues:")
        for p in problems[:10]:  # Show first 10
            print(f"      Module {p['module']}, Lesson {p['lesson']} ({p['id']}): {', '.join(p['issues'])}")
        if len(problems) > 10:
            print(f"      ... and {len(problems) - 10} more")
    else:
        print("   [OK] All lessons have complete data!")

    print()

    # === SECTION 3: VIDEO FILE ANALYSIS ===
    print("3. VIDEO FILE ANALYSIS")
    print("-" * 100)

    all_videos = list(course_path.glob("**/*.mp4"))
    total_size_bytes = sum(v.stat().st_size for v in all_videos)
    total_size_mb = total_size_bytes / 1024 / 1024

    print(f"   Total Video Files: {len(all_videos)}")
    print(f"   Total Size: {total_size_mb:.1f} MB ({total_size_mb/1024:.2f} GB)")
    print()

    # Check for corrupted or tiny files
    suspicious_videos = [v for v in all_videos if v.stat().st_size < 10240]  # Less than 10KB

    if suspicious_videos:
        print(f"   [WARNING] {len(suspicious_videos)} videos are suspiciously small (<10KB):")
        for v in suspicious_videos:
            size_kb = v.stat().st_size / 1024
            print(f"      {v.relative_to(course_path)} ({size_kb:.1f} KB)")
    else:
        print("   [OK] All video files have reasonable sizes!")

    print()

    # === SECTION 4: EXPECTED VS ACTUAL COMPARISON ===
    print("4. EXPECTED VS ACTUAL CONTENT")
    print("-" * 100)

    # Load expected content from discovery file
    discovery_files = {
        "business-english-intro": "valid_lectures.json",
        "business-english-meetings": "meetings_valid_lectures.json"
    }

    expected_lectures = []
    if course_name in discovery_files:
        discovery_file = discovery_files[course_name]
        if Path(discovery_file).exists():
            with open(discovery_file, 'r', encoding='utf-8') as f:
                expected_lectures = json.load(f)

    if expected_lectures:
        expected_ids = set(lec['lecture_id'].lower() for lec in expected_lectures)
        actual_ids = set(lesson['id'].lower() for m in module_data for lesson in m['lessons'])

        print(f"   Expected Lectures (from discovery): {len(expected_ids)}")
        print(f"   Actual Lessons (downloaded): {len(actual_ids)}")
        print()

        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids

        if missing:
            print(f"   [ERROR] {len(missing)} lectures are MISSING:")
            for lec_id in sorted(list(missing)[:10]):
                print(f"      - {lec_id}")
            if len(missing) > 10:
                print(f"      ... and {len(missing) - 10} more")
            print()
        else:
            print("   [OK] All expected lectures are present!")
            print()

        if extra:
            print(f"   [WARNING] {len(extra)} unexpected lectures found:")
            for lec_id in sorted(list(extra)[:10]):
                print(f"      - {lec_id}")
            if len(extra) > 10:
                print(f"      ... and {len(extra) - 10} more")
            print()
        else:
            print("   [OK] No unexpected lectures found!")
            print()

        if not missing and not extra:
            print("   [PERFECT MATCH] All expected content is present and correct!")
            print()
    else:
        print("   [INFO] No discovery file available for comparison")
        print()

    # === SECTION 5: FILE SYSTEM CHECK ===
    print("5. FILE SYSTEM & ACCESSIBILITY")
    print("-" * 100)

    import os

    accessible_count = 0
    inaccessible_files = []

    for video in all_videos:
        if os.access(video, os.R_OK):
            accessible_count += 1
        else:
            inaccessible_files.append(video)

    print(f"   Total Video Files: {len(all_videos)}")
    print(f"   Accessible Videos: {accessible_count}/{len(all_videos)}")

    if inaccessible_files:
        print(f"   [ERROR] {len(inaccessible_files)} videos are not accessible:")
        for v in inaccessible_files[:10]:
            print(f"      {v.relative_to(course_path)}")
        if len(inaccessible_files) > 10:
            print(f"      ... and {len(inaccessible_files) - 10} more")
    else:
        print("   [OK] All videos are accessible!")

    print()

    # === SECTION 6: MODULE DISTRIBUTION CHECK ===
    print("6. MODULE DISTRIBUTION ANALYSIS")
    print("-" * 100)

    # Check if distribution is reasonable
    lessons_per_module = [m['lesson_count'] for m in module_data]
    avg_lessons = sum(lessons_per_module) / len(lessons_per_module) if module_data else 0
    min_lessons = min(lessons_per_module) if lessons_per_module else 0
    max_lessons = max(lessons_per_module) if lessons_per_module else 0

    print(f"   Average lessons per module: {avg_lessons:.1f}")
    print(f"   Range: {min_lessons} - {max_lessons} lessons")
    print()

    # Check if distribution is too uneven
    if max_lessons > 2 * min_lessons and len(modules) > 2:
        print(f"   [WARNING] Uneven distribution detected!")
        print(f"   Some modules have {max_lessons} lessons while others have only {min_lessons}")
        print(f"   Consider re-running the scraper with the fixed algorithm.")
    else:
        print("   [OK] Module distribution is reasonable!")

    print()

    # === FINAL SUMMARY ===
    print("=" * 100)
    print(" " * 40 + "DIAGNOSTIC SUMMARY")
    print("=" * 100)

    all_checks_passed = (
        len(modules) > 0 and
        lessons_with_videos == total_lessons and
        lessons_with_metadata == total_lessons and
        len(suspicious_videos) == 0 and
        len(inaccessible_files) == 0 and
        (not expected_lectures or len(missing) == 0)
    )

    if all_checks_passed:
        print()
        print("   >>> ALL CHECKS PASSED <<<")
        print()
        print(f"   Course: {course_name}")
        print(f"   Modules: {len(modules)}")
        print(f"   Lessons: {total_lessons}")
        print(f"   Videos: {len(all_videos)} (all valid & accessible)")
        print(f"   Total Size: {total_size_mb:.1f} MB")
        print()
        print("   All videos are present, accessible, and properly organized!")
        print()
    else:
        print()
        print("   !!! ISSUES DETECTED !!!")
        print()
        if lessons_with_videos < total_lessons:
            print(f"   * {total_lessons - lessons_with_videos} lessons are missing videos")
        if len(suspicious_videos) > 0:
            print(f"   * {len(suspicious_videos)} videos may be corrupt")
        if len(inaccessible_files) > 0:
            print(f"   * {len(inaccessible_files)} videos are not accessible")
        if expected_lectures and len(missing) > 0:
            print(f"   * {len(missing)} expected lectures are missing")
        print()

    print("=" * 100)

    return all_checks_passed


if __name__ == "__main__":
    try:
        result = diagnostic_report("business-english-intro")
        exit(0 if result else 1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(2)
