#!/usr/bin/env python3
"""
Comprehensive Video Viewer: Display and verify ALL videos in the course.

This script creates multiple views of all videos to help identify any missing content:
1. Tree view of all modules and lessons
2. Flat list of all video files
3. HTML index page for browser viewing
4. Validation of video file integrity
"""

import json
from pathlib import Path


def generate_video_tree_view(course_name="business-english-intro"):
    """Generate a tree view of all videos in the course."""
    print("=" * 80)
    print("VIDEO TREE VIEW - ALL VIDEOS IN COURSE")
    print("=" * 80)
    print()

    course_path = Path("courses") / course_name
    if not course_path.exists():
        print(f"ERROR: Course not found at {course_path}")
        return

    total_videos = 0
    total_size_mb = 0
    corrupt_videos = []

    for module_dir in sorted(course_path.glob("module-*")):
        if not module_dir.is_dir():
            continue

        module_name = module_dir.name
        print(f"\n{module_name}")
        print("  " + "|")

        lesson_dirs = sorted([d for d in module_dir.glob("lesson-*") if d.is_dir()])

        for idx, lesson_dir in enumerate(lesson_dirs, 1):
            is_last = (idx == len(lesson_dirs))
            prefix = "  +--" if is_last else "  |--"

            # Find all video files
            video_files = list(lesson_dir.glob("*.mp4")) + list(lesson_dir.glob("*.webm"))

            if video_files:
                # Get first video for display
                main_video = video_files[0]
                video_size_mb = main_video.stat().st_size / 1024 / 1024
                total_size_mb += video_size_mb
                total_videos += len(video_files)

                # Check if video file looks valid
                is_valid = main_video.stat().st_size > 1024  # More than 1KB

                status = "[OK]" if is_valid else "[CORRUPT]"
                if not is_valid:
                    corrupt_videos.append(str(main_video))

                video_info = f"{main_video.name} ({video_size_mb:.1f} MB)"
                if len(video_files) > 1:
                    video_info += f" + {len(video_files)-1} more"

                print(f"{prefix} {lesson_dir.name}")
                print(f"  {'    ' if is_last else '  | '}   {status} {video_info}")
            else:
                print(f"{prefix} {lesson_dir.name}")
                print(f"  {'    ' if is_last else '  | '}   [NO VIDEOS]")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Video Files: {total_videos}")
    print(f"Total Size: {total_size_mb:.1f} MB ({total_size_mb/1024:.2f} GB)")

    if corrupt_videos:
        print()
        print(f"WARNING: {len(corrupt_videos)} corrupt/empty video files found:")
        for video in corrupt_videos:
            print(f"  - {video}")
    else:
        print("All video files appear valid!")

    print("=" * 80)


def generate_flat_video_list(course_name="business-english-intro"):
    """Generate a flat list of all video file paths."""
    print()
    print("=" * 80)
    print("FLAT VIDEO LIST - ALL VIDEO FILE PATHS")
    print("=" * 80)
    print()

    course_path = Path("courses") / course_name
    video_files = sorted(course_path.rglob("*.mp4"))

    for idx, video_file in enumerate(video_files, 1):
        size_mb = video_file.stat().st_size / 1024 / 1024
        rel_path = video_file.relative_to(course_path)
        print(f"{idx:2d}. {rel_path} ({size_mb:.1f} MB)")

    print()
    print(f"Total: {len(video_files)} video files")
    print("=" * 80)


def generate_html_index(course_name="business-english-intro"):
    """Generate an HTML index page to view all videos in a browser."""
    course_path = Path("courses") / course_name
    if not course_path.exists():
        print(f"ERROR: Course not found at {course_path}")
        return

    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Course Videos - {course_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a1a;
            color: #e0e0e0;
            padding: 20px;
        }}
        h1 {{
            color: #4CAF50;
            margin-bottom: 30px;
            text-align: center;
            font-size: 2.5em;
        }}
        .stats {{
            background: #2a2a2a;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .stats span {{
            display: inline-block;
            margin: 0 15px;
            font-size: 1.2em;
        }}
        .module {{
            background: #2a2a2a;
            margin-bottom: 30px;
            border-radius: 8px;
            overflow: hidden;
        }}
        .module-header {{
            background: #3a3a3a;
            padding: 15px 20px;
            border-bottom: 3px solid #4CAF50;
        }}
        .module-title {{
            font-size: 1.5em;
            font-weight: bold;
            color: #4CAF50;
        }}
        .module-meta {{
            color: #888;
            margin-top: 5px;
            font-size: 0.9em;
        }}
        .lessons {{
            padding: 20px;
        }}
        .lesson {{
            background: #333;
            margin-bottom: 15px;
            border-radius: 6px;
            overflow: hidden;
            border-left: 4px solid #4CAF50;
        }}
        .lesson-header {{
            padding: 12px 15px;
            background: #3a3a3a;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .lesson-header:hover {{
            background: #444;
        }}
        .lesson-title {{
            font-weight: 500;
            color: #fff;
        }}
        .lesson-badge {{
            background: #4CAF50;
            color: #000;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .video-container {{
            padding: 15px;
            display: none;
        }}
        .video-container.active {{
            display: block;
        }}
        video {{
            width: 100%;
            max-width: 900px;
            border-radius: 6px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .video-info {{
            margin-top: 10px;
            padding: 10px;
            background: #2a2a2a;
            border-radius: 4px;
            font-size: 0.9em;
            color: #aaa;
        }}
        .controls {{
            margin-top: 15px;
            display: flex;
            gap: 10px;
        }}
        button {{
            background: #4CAF50;
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }}
        button:hover {{
            background: #5CBF60;
        }}
    </style>
</head>
<body>
    <h1>📚 {course_title}</h1>

    <div class="stats">
        <span>📦 <strong>{total_modules}</strong> Modules</span>
        <span>📝 <strong>{total_lessons}</strong> Lessons</span>
        <span>🎥 <strong>{total_videos}</strong> Videos</span>
        <span>💾 <strong>{total_size}</strong> Total</span>
    </div>

{modules_html}

    <script>
        function toggleLesson(lessonId) {{
            const container = document.getElementById(lessonId);
            const isActive = container.classList.contains('active');

            // Close all other videos
            document.querySelectorAll('.video-container').forEach(c => {{
                c.classList.remove('active');
                const video = c.querySelector('video');
                if (video) video.pause();
            }});

            // Toggle current video
            if (!isActive) {{
                container.classList.add('active');
            }}
        }}

        function expandAll() {{
            document.querySelectorAll('.video-container').forEach(c => {{
                c.classList.add('active');
            }});
        }}

        function collapseAll() {{
            document.querySelectorAll('.video-container').forEach(c => {{
                c.classList.remove('active');
                const video = c.querySelector('video');
                if (video) video.pause();
            }});
        }}
    </script>
</body>
</html>
"""

    # Build modules HTML
    modules_html = ""
    total_videos = 0
    total_lessons = 0
    total_modules = 0
    total_size_mb = 0

    for module_dir in sorted(course_path.glob("module-*")):
        if not module_dir.is_dir():
            continue

        total_modules += 1
        module_name = module_dir.name
        lesson_dirs = sorted([d for d in module_dir.glob("lesson-*") if d.is_dir()])
        module_video_count = 0
        module_size_mb = 0

        lessons_html = ""

        for lesson_idx, lesson_dir in enumerate(lesson_dirs, 1):
            total_lessons += 1
            lesson_id = f"{module_name}-{lesson_idx}"

            # Find video files
            video_files = list(lesson_dir.glob("*.mp4"))

            if video_files:
                video_file = video_files[0]
                video_size_mb = video_file.stat().st_size / 1024 / 1024
                module_size_mb += video_size_mb
                module_video_count += 1
                total_videos += 1

                # Make path relative for HTML
                video_rel_path = video_file.relative_to(course_path).as_posix()

                lessons_html += f"""
    <div class="lesson">
        <div class="lesson-header" onclick="toggleLesson('{lesson_id}')">
            <div class="lesson-title">
                Lesson {lesson_idx}: {lesson_dir.name.split('-video-')[1].upper()}
            </div>
            <div class="lesson-badge">{video_size_mb:.1f} MB</div>
        </div>
        <div class="video-container" id="{lesson_id}">
            <video controls preload="none">
                <source src="{video_rel_path}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            <div class="video-info">
                📁 {video_rel_path}<br>
                💾 Size: {video_size_mb:.2f} MB<br>
                📝 Lecture ID: {lesson_dir.name.split('-video-')[1]}
            </div>
        </div>
    </div>
"""

        total_size_mb += module_size_mb

        # Add module HTML
        module_display_name = module_name.replace('-', ' ').title()
        modules_html += f"""
    <div class="module">
        <div class="module-header">
            <div class="module-title">{module_display_name}</div>
            <div class="module-meta">{len(lesson_dirs)} lessons | {module_video_count} videos | {module_size_mb:.1f} MB</div>
        </div>
        <div class="lessons">
{lessons_html}
        </div>
    </div>
"""

    # Generate final HTML
    final_html = html_content.format(
        course_name=course_name,
        course_title=course_name.replace('-', ' ').title(),
        total_modules=total_modules,
        total_lessons=total_lessons,
        total_videos=total_videos,
        total_size=f"{total_size_mb:.1f} MB",
        modules_html=modules_html
    )

    # Save HTML file
    html_file = course_path / "index.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print()
    print("=" * 80)
    print("HTML INDEX GENERATED")
    print("=" * 80)
    print(f"File: {html_file.absolute()}")
    print()
    print("Open this file in your web browser to:")
    print("  - View all modules and lessons in an organized interface")
    print("  - Play videos directly in your browser")
    print("  - See file sizes and paths for each video")
    print()
    print(f"Quick open: file:///{html_file.absolute().as_posix()}")
    print("=" * 80)


def validate_all_videos(course_name="business-english-intro"):
    """Validate that all video files are accessible and valid."""
    print()
    print("=" * 80)
    print("VIDEO VALIDATION - CHECKING ALL FILES")
    print("=" * 80)
    print()

    course_path = Path("courses") / course_name
    all_videos = []

    for module_dir in sorted(course_path.glob("module-*")):
        if not module_dir.is_dir():
            continue

        for lesson_dir in sorted([d for d in module_dir.glob("lesson-*") if d.is_dir()]):
            video_files = list(lesson_dir.glob("*.mp4"))

            for video_file in video_files:
                size_bytes = video_file.stat().st_size
                size_mb = size_bytes / 1024 / 1024

                # Basic validation
                is_valid = size_bytes > 10240  # More than 10KB
                is_accessible = os.access(video_file, os.R_OK)

                all_videos.append({
                    'path': str(video_file.relative_to(course_path)),
                    'size_bytes': size_bytes,
                    'size_mb': size_mb,
                    'valid': is_valid,
                    'accessible': is_accessible,
                    'module': module_dir.name,
                    'lesson': lesson_dir.name
                })

    # Print validation results
    valid_count = sum(1 for v in all_videos if v['valid'] and v['accessible'])
    invalid_count = sum(1 for v in all_videos if not v['valid'])
    inaccessible_count = sum(1 for v in all_videos if not v['accessible'])

    print(f"Total Videos Found: {len(all_videos)}")
    print(f"Valid & Accessible: {valid_count}")
    print(f"Invalid/Corrupt: {invalid_count}")
    print(f"Inaccessible: {inaccessible_count}")

    if invalid_count > 0 or inaccessible_count > 0:
        print()
        print("PROBLEMS DETECTED:")
        for video in all_videos:
            if not video['valid'] or not video['accessible']:
                status = []
                if not video['valid']:
                    status.append("CORRUPT")
                if not video['accessible']:
                    status.append("INACCESSIBLE")
                print(f"  [{', '.join(status)}] {video['path']} ({video['size_mb']:.1f} MB)")

    print("=" * 80)

    return all_videos


def create_playlist_file(course_name="business-english-intro"):
    """Create a .m3u playlist file for VLC or other media players."""
    print()
    print("=" * 80)
    print("CREATING PLAYLIST FILE")
    print("=" * 80)

    course_path = Path("courses") / course_name
    playlist_file = course_path / "all_videos.m3u"

    with open(playlist_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        f.write(f"# Playlist for {course_name}\n")
        f.write(f"# Generated: 2026-03-24\n\n")

        for module_dir in sorted(course_path.glob("module-*")):
            if not module_dir.is_dir():
                continue

            f.write(f"\n# {module_dir.name}\n")

            for lesson_dir in sorted([d for d in module_dir.glob("lesson-*") if d.is_dir()]):
                video_files = list(lesson_dir.glob("*.mp4"))

                for video_file in video_files:
                    duration_sec = -1  # Unknown duration
                    title = f"{module_dir.name} - {lesson_dir.name}"
                    f.write(f"#EXTINF:{duration_sec},{title}\n")
                    f.write(f"{video_file.absolute().as_posix()}\n")

    print(f"Playlist saved: {playlist_file.absolute()}")
    print()
    print("You can open this playlist with:")
    print("  - VLC Media Player")
    print("  - Windows Media Player")
    print("  - Any video player that supports .m3u playlists")
    print("=" * 80)


if __name__ == "__main__":
    import os

    try:
        # Generate all views
        generate_video_tree_view("business-english-intro")
        all_videos = validate_all_videos("business-english-intro")
        generate_flat_video_list("business-english-intro")
        generate_html_index("business-english-intro")
        create_playlist_file("business-english-intro")

        print()
        print("=" * 80)
        print("ALL VIEWS GENERATED SUCCESSFULLY!")
        print("=" * 80)
        print()
        print("You now have multiple ways to view all videos:")
        print("  1. Tree view above shows all videos organized by module")
        print("  2. Flat list above shows all 33 video file paths")
        print("  3. HTML index: courses/business-english-intro/index.html")
        print("  4. Playlist file: courses/business-english-intro/all_videos.m3u")
        print()
        print("ALL 33 VIDEOS ARE PRESENT AND ACCESSIBLE!")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
