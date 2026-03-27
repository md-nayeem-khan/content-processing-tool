#!/usr/bin/env python3
"""
Explore the full course structure for business-english-intro.
Try to discover all modules and lessons.
"""

import os
import json
import requests
from dotenv import load_dotenv

def explore_course_structure():
    """Explore the complete course structure."""
    print("Exploring Business English Course Structure")
    print("="*50)

    # Load credentials
    load_dotenv()
    cauth_cookie = os.getenv('COURSERA_CAUTH_COOKIE')

    if not cauth_cookie:
        print("ERROR: COURSERA_CAUTH_COOKIE not found in .env file")
        return False

    # Setup request
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'x-coursera-application': 'ondemand',
        'x-requested-with': 'XMLHttpRequest',
        'authority': 'www.coursera.org'
    }
    cookies = {'CAUTH': cauth_cookie}

    course_id = "46b4tHEkEeWbbw5cIAKQrw"  # business-english-intro

    # Try different API endpoints to discover course structure
    endpoints_to_try = [
        {
            'name': 'Course Modules',
            'url': f'https://www.coursera.org/api/onDemandCourseModules.v1/course/{course_id}/modules'
        },
        {
            'name': 'Course Details',
            'url': f'https://www.coursera.org/api/courses.v1/courses/{course_id}'
        },
        {
            'name': 'Course by Slug',
            'url': f'https://www.coursera.org/api/courses.v1/courses?q=slug&slug=business-english-intro'
        },
        {
            'name': 'On Demand Course',
            'url': f'https://www.coursera.org/api/onDemandCourses.v1/course/{course_id}'
        },
        {
            'name': 'Course Syllabus',
            'url': f'https://www.coursera.org/api/onDemandCourseMaterials.v2/course/{course_id}/items?includes=moduleIds,lessonIds'
        }
    ]

    successful_endpoints = []

    for endpoint in endpoints_to_try:
        try:
            print(f"\nTrying: {endpoint['name']}")
            print(f"URL: {endpoint['url']}")

            response = requests.get(endpoint['url'], headers=headers, cookies=cookies)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"SUCCESS! Keys: {list(data.keys())}")

                # Save successful response for analysis
                filename = f"course_structure_{endpoint['name'].lower().replace(' ', '_')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                print(f"Response saved to: {filename}")

                successful_endpoints.append(endpoint['name'])

                # Try to extract module/lesson structure
                print("Analyzing structure...")
                if 'elements' in data:
                    print(f"  - {len(data['elements'])} elements")
                    if data['elements']:
                        first_element = data['elements'][0]
                        print(f"  - First element keys: {list(first_element.keys())}")

                        # Look for module/lesson related fields
                        for key in first_element.keys():
                            if 'module' in key.lower() or 'lesson' in key.lower():
                                print(f"    - Found {key}: {first_element[key]}")

            else:
                print(f"Failed: {response.status_code}")
                if response.status_code == 404:
                    print("  - Endpoint not found")
                elif response.status_code == 401:
                    print("  - Authentication issue")
                elif response.status_code == 403:
                    print("  - Access forbidden")

        except Exception as e:
            print(f"Error: {e}")

    print(f"\n\nSUMMARY:")
    print(f"Successful endpoints: {len(successful_endpoints)}")
    for endpoint in successful_endpoints:
        print(f"  - {endpoint}")

    return len(successful_endpoints) > 0

if __name__ == "__main__":
    explore_course_structure()