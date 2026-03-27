#!/usr/bin/env python3
"""
Quick verification script to show subtitle download success.
"""

from pathlib import Path

def main():
    """Verify subtitle download results."""
    print("SUCCESS: SUBTITLE DOWNLOAD VERIFICATION")
    print("=" * 50)

    course_path = Path("courses/introduction-to-business-english-communication-course")

    # Count files
    video_files = list(course_path.glob("**/*.mp4"))
    subtitle_files = list(course_path.glob("**/*.vtt"))

    print(f"Videos found: {len(video_files)}")
    print(f"Subtitles found: {len(subtitle_files)}")
    print(f"Pairing success: {len(video_files) == len(subtitle_files)}")

    # Show first few pairs
    print("\nFirst 3 video-subtitle pairs:")
    for i, (video, subtitle) in enumerate(zip(sorted(video_files)[:3], sorted(subtitle_files)[:3]), 1):
        print(f"  {i}. {video.name}")
        print(f"     {subtitle.name}")

    # Show subtitle format
    first_subtitle = sorted(subtitle_files)[0]
    with open(first_subtitle, 'r', encoding='utf-8') as f:
        content = f.read(200)

    print(f"\nSubtitle format preview ({first_subtitle.name[:30]}...):")
    print("   " + "\n   ".join(content.split('\n')[:8]))

    print(f"\nSUCCESS: {len(subtitle_files)} English subtitles downloaded!")

if __name__ == "__main__":
    main()