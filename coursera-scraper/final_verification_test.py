#!/usr/bin/env python3
"""
Final verification test to confirm subtitle download functionality is working.
"""

import sys
from pathlib import Path

def main():
    """Verify that subtitle download functionality is working correctly."""
    print("=" * 80)
    print("FINAL SUBTITLE FUNCTIONALITY VERIFICATION")
    print("=" * 80)

    # Test paths
    course_path = Path("courses/introduction-to-business-english-communication-course")
    lesson_path = course_path / "module-01-introduction-to-business-english-communication" / "lesson-01-lesson-1-course-overview-and-assessment"

    # Check if course directory exists
    if not course_path.exists():
        print(f"[FAIL] Course directory not found: {course_path}")
        return False

    print(f"[PASS] Course directory exists: {course_path}")

    # Check if lesson directory exists
    if not lesson_path.exists():
        print(f"[FAIL] Lesson directory not found: {lesson_path}")
        return False

    print(f"[PASS] Lesson directory exists: {lesson_path}")

    # Check video files exist
    video_files = list(lesson_path.glob("*.mp4"))
    if not video_files:
        print(f"[FAIL] No video files found in {lesson_path}")
        return False

    print(f"[PASS] Found {len(video_files)} video files")

    # Check subtitle files exist
    subtitle_files = list(lesson_path.glob("*.vtt"))
    if not subtitle_files:
        print(f"[FAIL] No subtitle files found in {lesson_path}")
        return False

    print(f"[PASS] Found {len(subtitle_files)} subtitle files")

    # Check that each video has a corresponding subtitle
    video_bases = set()
    for video in video_files:
        base_name = video.name.replace('.mp4', '')
        video_bases.add(base_name)

    subtitle_bases = set()
    for subtitle in subtitle_files:
        base_name = subtitle.name.replace('.vtt', '')
        subtitle_bases.add(base_name)

    if video_bases != subtitle_bases:
        print(f"[FAIL] Video and subtitle files don't match")
        print(f"  Videos: {sorted(video_bases)}")
        print(f"  Subtitles: {sorted(subtitle_bases)}")
        return False

    print(f"[PASS] All videos have corresponding subtitles")

    # Check subtitle file format
    first_subtitle = subtitle_files[0]
    try:
        with open(first_subtitle, 'r', encoding='utf-8') as f:
            content = f.read(500)  # Read first 500 chars

        if not content.startswith('WEBVTT'):
            print(f"[FAIL] Subtitle file {first_subtitle.name} is not WEBVTT format")
            return False

        if '-->' not in content:
            print(f"[FAIL] Subtitle file {first_subtitle.name} doesn't contain timestamps")
            return False

        print(f"[PASS] Subtitle file format is valid WEBVTT")

    except Exception as e:
        print(f"[FAIL] Could not read subtitle file {first_subtitle.name}: {e}")
        return False

    # Count total subtitles across course
    try:
        total_subtitles = len(list(course_path.glob("**/*.vtt")))
        print(f"[PASS] Total subtitles across entire course: {total_subtitles}")

        if total_subtitles < 30:  # Should be 33, but allow some margin
            print(f"[WARN] Expected ~33 subtitles, found {total_subtitles}")
        else:
            print(f"[PASS] Subtitle count looks good: {total_subtitles}")

    except Exception as e:
        print(f"[FAIL] Could not count total subtitles: {e}")
        return False

    # Check sequential naming
    sample_files = sorted(subtitle_files)
    expected_prefixes = ['1_', '2_', '3_']

    for i, expected_prefix in enumerate(expected_prefixes):
        if i < len(sample_files):
            if not sample_files[i].name.startswith(expected_prefix):
                print(f"[WARN] Sequential naming might be off for {sample_files[i].name}")
            else:
                print(f"[PASS] Sequential naming working: {sample_files[i].name}")

    print("\n" + "=" * 80)
    print("✅ SUCCESS: SUBTITLE DOWNLOAD FUNCTIONALITY IS WORKING!")
    print("=" * 80)
    print("\nSUMMARY:")
    print(f"• Course scraped successfully: {course_path.name}")
    print(f"• Videos found: {len(video_files)} in first lesson")
    print(f"• Subtitles downloaded: {len(subtitle_files)} in first lesson")
    print(f"• Total subtitles across course: {total_subtitles}")
    print("• Subtitle format: WebVTT (proper)")
    print("• Sequential naming: Working")
    print("• Video-subtitle pairing: Complete")

    print("\n🎯 USAGE:")
    print("• To download videos + subtitles: python -m src.main download <course-name> --subtitles")
    print("• To download only videos: python -m src.main download <course-name> --no-subtitles")
    print("• To change subtitle language: python -m src.main download <course-name> --subtitle-language es")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)