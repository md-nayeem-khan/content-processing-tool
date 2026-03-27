# Enhanced Coursera Video and Subtitle Downloader

This enhanced version of the Coursera scraper now downloads **both 720p videos AND their corresponding English subtitles (.vtt)** with proper sequential naming and video names.

## ✨ New Features

- **📹 Video Downloads**: 720p MP4 videos with sequential naming
- **📝 Subtitle Downloads**: English VTT subtitles with matching names
- **🔢 Sequential Naming**: Files are named with proper sequencing (1_video_name.mp4, 1_video_name.vtt)
- **🔄 API Integration**: Automatically fetches subtitle URLs from Coursera's API
- **📊 Progress Tracking**: Rich console output with download progress
- **🛡️ Error Handling**: Robust error handling and retry mechanisms

## 📁 File Naming Convention

The enhanced downloader creates files with the following naming pattern:

```
1_video_welcome_to_business_english.mp4    (720p video)
1_video_welcome_to_business_english.vtt    (English subtitle)
2_introduction_to_course.mp4               (next video)
2_introduction_to_course.vtt               (matching subtitle)
3_email_writing_guidelines.mp4
3_email_writing_guidelines.vtt
...
```

## 🚀 Usage Options

### Option 1: Standalone Downloader (Recommended)

Use the standalone enhanced downloader:

```bash
python enhanced_video_subtitle_downloader.py
```

This script:
- Downloads 720p videos with sequential naming
- Downloads English subtitles with matching names
- Uses the existing lesson metadata from your scraped course
- Shows progress with rich console output

### Option 2: Integrated with Core Architecture

Use the integrated version with the main codebase:

```bash
python demo_enhanced_downloader.py
```

### Option 3: Use the Core Enhanced Downloader Class

```python
from src.api.auth import CourseraAuth
from src.api.enhanced_downloader import EnhancedVideoDownloader
from src.core.file_manager import FileManager

# Initialize components
auth = CourseraAuth()
auth.cauth_cookie = "your_cauth_cookie"
file_manager = FileManager("./courses")

# Create enhanced downloader
downloader = EnhancedVideoDownloader(
    auth=auth,
    file_manager=file_manager,
    max_concurrent=3,           # Download 3 files simultaneously
    download_subtitles=True,    # Enable subtitle downloading
    subtitle_language='en'      # Download English subtitles
)

# Download videos and subtitles
result = downloader.download_course_videos_and_subtitles(
    course_path=Path("courses/business-english-intro"),
    target_resolution="720p"
)
```

## 🔧 Setup Requirements

1. **Environment File**: Make sure your `.env` file contains:
   ```
   COURSERA_CAUTH_COOKIE=your_cauth_cookie_here
   ```

2. **Course Structure**: Run the course scraper first to extract the course structure:
   ```bash
   python src/main.py  # or your existing scraper
   ```

3. **Dependencies**: Install required packages:
   ```bash
   pip install aiohttp aiofiles rich pathvalidate python-dotenv
   ```

## 📊 How It Works

### Video Processing
1. **Discovery**: Scans lesson metadata for 720p MP4 videos
2. **Naming**: Creates sequential filenames (1_video_name.mp4, 2_video_name.mp4)
3. **Download**: Downloads videos with progress tracking

### Subtitle Processing
1. **API Fetch**: Calls Coursera's `onDemandLectureVideos.v1` API endpoint
2. **URL Extraction**: Extracts English subtitle URLs from `subtitlesVtt.en`
3. **Download**: Downloads VTT files with matching video names
4. **Naming**: Creates matching filenames (1_video_name.vtt, 2_video_name.vtt)

### API Integration
The enhanced downloader automatically fetches subtitle information using:
```
https://www.coursera.org/api/onDemandLectureVideos.v1/{course_id}~{lecture_id}?includes=video&fields=onDemandVideos.v1(subtitlesVtt,...)
```

## 🧪 Testing

Run the test suite to verify functionality:

```bash
python test_enhanced_downloader.py
```

This tests:
- ✅ Sequential naming functionality
- ✅ API URL construction
- ✅ File structure verification

## 📋 Example API Response

The enhanced downloader processes API responses like this:

```json
{
  "linked": {
    "onDemandVideos.v1": [
      {
        "subtitlesVtt": {
          "en": "/api/subtitleAssetProxy.v1/Wrba1WUsR_a22tVlLKf2Iw?expiry=1774569600000&hmac=YDnZRtQm8ZY-pmJjepZe3MZLEHBPJIOj3F0oL6DUGvk&fileExtension=vtt"
        }
      }
    ]
  }
}
```

## 🎯 Key Features

- **Sequential Naming**: Files are numbered in the order they appear in the course
- **Resolution Handling**: Automatically removes resolution suffixes (_720p) from names
- **Unicode Support**: Properly handles international characters in video names
- **Error Recovery**: Skips failed downloads and continues with others
- **Progress Tracking**: Real-time progress bars and statistics
- **Resume Support**: Can resume interrupted downloads

## 📝 File Structure

```
courses/
├── business-english-intro/
    ├── module-01-getting-started/
    │   ├── lesson-01-welcome/
    │   │   ├── 1_video_welcome_to_business_english.mp4
    │   │   ├── 1_video_welcome_to_business_english.vtt
    │   │   └── lesson_metadata.json
    │   ├── lesson-02-introduction/
    │   │   ├── 2_introduction_to_course.mp4
    │   │   ├── 2_introduction_to_course.vtt
    │   │   └── lesson_metadata.json
    ├── module-02-email-writing/
    │   ├── lesson-03-guidelines/
    │   │   ├── 3_email_writing_guidelines.mp4
    │   │   ├── 3_email_writing_guidelines.vtt
    │   │   └── lesson_metadata.json
```

## 🔍 Troubleshooting

1. **No Subtitles Downloaded**:
   - Check if the course has English subtitles available
   - Verify your authentication cookie is valid
   - Check API rate limits

2. **Unicode Errors**:
   - The system handles Unicode characters automatically
   - Files are sanitized for filesystem compatibility

3. **Network Issues**:
   - The downloader includes retry logic
   - Use `resume=True` to continue interrupted downloads

## 🎉 Success!

You now have a complete system that downloads both videos and subtitles with proper sequential naming:

- Videos: `1_video_name.mp4`, `2_video_name.mp4`, etc.
- Subtitles: `1_video_name.vtt`, `2_video_name.vtt`, etc.

The system maintains the relationship between videos and their subtitles while providing proper sequencing based on course structure!