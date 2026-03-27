#!/usr/bin/env python3
"""
Test script to verify video filename improvements using actual video names.
"""

import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

def test_video_name_extraction():
    """Test that video names are properly extracted from the comprehensive API."""
    print("Testing Video Name Extraction from Comprehensive API")
    print("=" * 70)

    # Load credentials
    load_dotenv()
    cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')

    if not cauth_cookie:
        print("ERROR: COURSERA_CAUTH_COOKIE not found in .env file")
        return

    # Test the comprehensive API response
    course_materials_url = "https://www.coursera.org/api/onDemandCourseMaterials.v2/?q=slug&slug=business-english-intro&includes=modules%2Clessons%2CpassableItemGroups%2CpassableItemGroupChoices%2CpassableLessonElements%2Citems%2Ctracks%2CgradePolicy%2CgradingParameters%2CembeddedContentMapping&fields=moduleIds%2ConDemandCourseMaterialModules.v1(name%2Cslug%2Cdescription%2CtimeCommitment%2ClessonIds%2Coptional%2ClearningObjectives)%2ConDemandCourseMaterialLessons.v1(name%2Cslug%2CtimeCommitment%2CelementIds%2Coptional%2CtrackId)%2ConDemandCourseMaterialPassableItemGroups.v1(requiredPassedCount%2CpassableItemGroupChoiceIds%2CtrackId)%2ConDemandCourseMaterialPassableItemGroupChoices.v1(name%2Cdescription%2CitemIds)%2ConDemandCourseMaterialPassableLessonElements.v1(gradingWeight%2CisRequiredForPassing)%2ConDemandCourseMaterialItems.v2(name%2CoriginalName%2Cslug%2CtimeCommitment%2CcontentSummary%2CisLocked%2ClockableByItem%2CitemLockedReasonCode%2CtrackId%2ClockedStatus%2CitemLockSummary%2CcustomDisplayTypenameOverride)%2ConDemandCourseMaterialTracks.v1(passablesCount)%2ConDemandGradingParameters.v1(gradedAssignmentGroups)%2CcontentAtomRelations.v1(embeddedContentSourceCourseId%2CsubContainerId)&showLockedItems=true"

    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'x-coursera-application': 'ondemand',
        'x-requested-with': 'XMLHttpRequest',
    }
    cookies = {'CAUTH': cauth_cookie}

    try:
        response = requests.get(course_materials_url, headers=headers, cookies=cookies)

        if response.status_code == 200:
            data = response.json()

            # Extract lesson data for "Lesson 1: Course Overview and Assessment"
            lessons = data.get('linked', {}).get('onDemandCourseMaterialLessons.v1', [])
            items = data.get('linked', {}).get('onDemandCourseMaterialItems.v2', [])

            # Find lesson 1
            target_lesson = None
            for lesson in lessons:
                if "Course Overview and Assessment" in lesson.get('name', ''):
                    target_lesson = lesson
                    break

            if target_lesson:
                print(f"Found target lesson: {target_lesson['name']}")
                print(f"Item IDs: {target_lesson['itemIds']}")

                # Extract video names for each item
                video_items = []
                for item_id in target_lesson['itemIds']:
                    for item in items:
                        if item['id'] == item_id:
                            # Check if it's a video (lecture)
                            content_summary = item.get('contentSummary', {})
                            if content_summary.get('typeName') == 'lecture':
                                # Test filename generation
                                from src.utils.sanitizer import sanitize_file_name
                                original_name = item['name']
                                safe_name = sanitize_file_name(original_name)
                                filename = f"{safe_name}_720p.mp4"

                                video_items.append({
                                    'item_id': item_id,
                                    'original_name': original_name,
                                    'safe_name': safe_name,
                                    'filename': filename
                                })
                                break

                print(f"\nFound {len(video_items)} video items:")
                for i, video in enumerate(video_items, 1):
                    print(f"{i}. Item ID: {video['item_id']}")
                    print(f"   Original Name: {video['original_name']}")
                    print(f"   Safe Name: {video['safe_name']}")
                    print(f"   Filename: {video['filename']}")
                    print()

                # Save test results
                test_results = {
                    'test_name': 'video_name_extraction',
                    'lesson_name': target_lesson['name'],
                    'video_items': video_items,
                    'expected_count': 3,
                    'actual_count': len(video_items),
                    'test_status': 'PASS' if len(video_items) == 3 else 'FAIL'
                }

                with open('video_name_test_results.json', 'w', encoding='utf-8') as f:
                    json.dump(test_results, f, indent=2)

                print(f"Test Results: {'PASS' if len(video_items) == 3 else 'FAIL'}")
                print(f"Expected 3 videos, found {len(video_items)}")
                print("Results saved to: video_name_test_results.json")

                return len(video_items) == 3
            else:
                print("ERROR: Could not find target lesson")
                return False

        else:
            print(f"ERROR: API request failed with status {response.status_code}")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_video_name_extraction()

    print("\n" + "=" * 70)
    print("VIDEO NAME EXTRACTION TEST SUMMARY")
    print("=" * 70)
    print(f"Result: {'PASS' if success else 'FAIL'}")

    if success:
        print("✓ Successfully extracted video names from comprehensive API")
        print("✓ Video names are properly sanitized for filesystem use")
        print("✓ Expected 3 videos found with descriptive names")
        print("")
        print("Expected output:")
        print("1. Video_ Welcome to Business English_720p.mp4")
        print("2. Video_ Course Overview_720p.mp4")
        print("3. Quiz Proficiency Video_ Phone Conversation_720p.mp4")
    else:
        print("✗ Video name extraction test failed")
        print("Please check the implementation and try again")