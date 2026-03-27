
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import os
from dotenv import load_dotenv
from api.auth import CourseraAuth
from api.coursera_client import CourseraClient
from core.scraper import CourseScraper
from core.file_manager import FileManager
from config.settings import ConfigManager

def main():
    load_dotenv()
    cauth_cookie = os.getenv("COURSERA_CAUTH_COOKIE")

    if not cauth_cookie:
        print("ERROR: COURSERA_CAUTH_COOKIE not found")
        return False

    try:
        # Initialize components
        auth = CourseraAuth(cauth_cookie=cauth_cookie)
        client = CourseraClient.from_config_file("config/api_endpoints.json", auth)
        config = ConfigManager()
        file_manager = FileManager(base_path=Path("test_courses"))
        scraper = CourseScraper(client, file_manager, config)

        # Use the comprehensive API approach
        print("Testing comprehensive API course creation...")
        course = scraper._create_course_from_comprehensive_api("business-english-intro")

        if course:
            print(f"SUCCESS: Created course: {course.name}")
            print(f"Modules: {len(course.modules)}")

            # Find the first lesson with videos
            video_lessons = []
            for module in course.modules:
                for lesson in module.lessons:
                    if lesson.assets:
                        video_assets = [asset for asset in lesson.assets if asset.file_type == "video"]
                        if video_assets:
                            video_lessons.append((lesson, video_assets))

            print(f"Found {len(video_lessons)} lessons with videos")

            # Test video extraction for first lesson
            if video_lessons:
                test_lesson, test_assets = video_lessons[0]
                print(f"\nTesting lesson: {test_lesson.name}")

                # Extract content assets to get actual URLs and names
                scraper._extract_content_assets_from_comprehensive_api(test_lesson)

                video_assets = [asset for asset in test_lesson.assets if asset.file_type == "video" and "720p.mp4" in asset.name]
                print(f"Found {len(video_assets)} video assets:")

                for i, asset in enumerate(video_assets, 1):
                    print(f"  {i}. {asset.name}")
                    print(f"     Original: {asset.metadata.get('original_name', 'N/A')}")
                    print(f"     URL: {bool(asset.url)}")

                return len(video_assets) > 0
            else:
                print("No video lessons found")
                return False
        else:
            print("ERROR: Could not create course from comprehensive API")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nTest result: {'PASS' if success else 'FAIL'}")
