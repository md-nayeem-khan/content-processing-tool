#!/usr/bin/env python3
"""
Test script to identify and fix the multiple videos per lesson issue.
"""

import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

def test_multiple_videos_per_lesson():
    """Test video extraction for the lesson with multiple videos."""
    print("Testing Multiple Videos Per Lesson")
    print("=" * 60)

    # Load credentials
    load_dotenv()
    cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')

    if not cauth_cookie:
        print("ERROR: COURSERA_CAUTH_COOKIE not found in .env file")
        return

    # API headers
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'x-coursera-application': 'ondemand',
        'x-requested-with': 'XMLHttpRequest',
        'authority': 'www.coursera.org'
    }
    cookies = {'CAUTH': cauth_cookie}

    # Test lesson data from the user
    lesson_data = {
        "course_id": "46b4tHEkEeWbbw5cIAKQrw",
        "lesson_name": "Lesson 1: Course Overview and Assessment",
        "video_item_ids": ["DKbsC", "2Zis7", "6AM0l"]  # The 3 videos in this lesson
    }

    print(f"Course ID: {lesson_data['course_id']}")
    print(f"Lesson: {lesson_data['lesson_name']}")
    print(f"Expected Videos: {len(lesson_data['video_item_ids'])}")
    print()

    # Test each video individually
    video_results = []

    for i, item_id in enumerate(lesson_data['video_item_ids'], 1):
        print(f"[{i}/{len(lesson_data['video_item_ids'])}] Testing video {item_id}...")

        # Construct API URL
        video_url = f"https://www.coursera.org/api/onDemandLectureVideos.v1/{lesson_data['course_id']}~{item_id}"
        video_url += "?includes=video&fields=onDemandVideos.v1(sources%2Csubtitles%2CsubtitlesVtt%2CsubtitlesTxt%2CsubtitlesAssetTags%2CdubbedSources%2CdubbedSubtitlesVtt%2CaudioDescriptionVideoSources)%2CdisableSkippingForward%2CstartMs%2CendMs"

        try:
            response = requests.get(video_url, headers=headers, cookies=cookies)

            if response.status_code == 200:
                data = response.json()

                # Check if video data is valid
                if ('linked' in data and
                    'onDemandVideos.v1' in data['linked'] and
                    len(data['linked']['onDemandVideos.v1']) > 0):

                    video_info = data['linked']['onDemandVideos.v1'][0]

                    # Extract video URLs for different resolutions
                    video_urls = {}
                    if 'sources' in video_info and 'byResolution' in video_info['sources']:
                        for resolution, source_data in video_info['sources']['byResolution'].items():
                            if 'mp4VideoUrl' in source_data:
                                video_urls[f"{resolution}_mp4"] = source_data['mp4VideoUrl']
                            if 'webMVideoUrl' in source_data:
                                video_urls[f"{resolution}_webm"] = source_data['webMVideoUrl']

                    video_results.append({
                        'item_id': item_id,
                        'video_id': video_info.get('id', 'N/A'),
                        'success': True,
                        'available_formats': list(video_urls.keys()),
                        'video_urls': video_urls,
                        'has_720p_mp4': '720p_mp4' in video_urls
                    })

                    print(f"   SUCCESS! Video ID: {video_info.get('id')}")
                    print(f"   Available formats: {list(video_urls.keys())}")
                    print(f"   Has 720p MP4: {'YES' if '720p_mp4' in video_urls else 'NO'}")

                else:
                    print(f"   ERROR: No valid video data in response")
                    video_results.append({
                        'item_id': item_id,
                        'success': False,
                        'error': 'No valid video data'
                    })

            else:
                print(f"   ERROR: HTTP {response.status_code}")
                video_results.append({
                    'item_id': item_id,
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                })

        except Exception as e:
            print(f"   ERROR: {e}")
            video_results.append({
                'item_id': item_id,
                'success': False,
                'error': str(e)
            })

    print()
    print("="*60)
    print("SUMMARY:")
    print(f"Total Videos Expected: {len(lesson_data['video_item_ids'])}")

    successful_videos = [v for v in video_results if v.get('success', False)]
    print(f"Successful Extractions: {len(successful_videos)}")

    videos_with_720p = [v for v in successful_videos if v.get('has_720p_mp4', False)]
    print(f"Videos with 720p MP4: {len(videos_with_720p)}")

    print()
    print("Detailed Results:")
    for result in video_results:
        if result.get('success', False):
            print(f"[OK] {result['item_id']}: 720p MP4 {'Available' if result.get('has_720p_mp4') else 'Missing'}")
        else:
            print(f"[FAIL] {result['item_id']}: {result.get('error', 'Unknown error')}")

    # Save results for analysis
    with open('multiple_videos_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'lesson_data': lesson_data,
            'video_results': video_results,
            'summary': {
                'total_expected': len(lesson_data['video_item_ids']),
                'successful_extractions': len(successful_videos),
                'videos_with_720p': len(videos_with_720p),
                'test_status': 'PASS' if len(videos_with_720p) == len(lesson_data['video_item_ids']) else 'FAIL'
            }
        }, f, indent=2)

    print(f"\nResults saved to: multiple_videos_test_results.json")

    # This test confirms that all videos can be individually extracted
    # Now let's check the current implementation to see where it might be failing
    return video_results

if __name__ == "__main__":
    test_multiple_videos_per_lesson()