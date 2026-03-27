# Supplement Download Feature

## Overview
The Coursera scraper now supports downloading supplement materials (reading materials, PDFs, vocabulary lists, summaries, etc.) in addition to videos and subtitles.

## What's New
- **New CLI Flag**: `--supplements/--no-supplements` (default: disabled)
- **New Content Type**: Supplement materials saved as HTML files
- **Sequential Naming**: Supplements follow the same naming convention as videos
- **Full Statistics**: Download statistics now include supplements

## Usage

### Basic Usage
Download videos, subtitles, and supplements:
```bash
python -m src.main download <course-name> --supplements
```

### Download Only Supplements (no videos)
```bash
python -m src.main download <course-name> --no-subtitles --supplements
```

### Download Everything
```bash
python -m src.main download <course-name> --subtitles --supplements
```

### Traditional Download (videos + subtitles only)
```bash
python -m src.main download <course-name>
```

## Command Options
```
--supplements/--no-supplements  Download supplement materials (.html) (default: disabled)
```

All other options remain the same:
- `--resolution, -r`: Video resolution (default: 720p)
- `--max-concurrent, -c`: Maximum concurrent downloads (default: 3)
- `--resume`: Resume incomplete downloads
- `--subtitles/--no-subtitles`: Download subtitles (default: enabled)
- `--subtitle-language`: Subtitle language (default: en)

## File Structure
Supplements are saved in the same lesson directories as videos:
```
courses/
  course-name/
    module-01-name/
      lesson-01-name/
        1_video_name.mp4
        1_video_name.vtt
        1_supplement_name.html
        2_another_video.mp4
        2_another_video.vtt
        2_another_supplement.html
```

## What Are Supplements?
Supplements include various types of course materials:
- 📚 **Reading Materials**: Additional text content, articles, guides
- 📝 **Vocabulary Lists**: Key terms and definitions
- 📄 **Summary Pages**: Lesson summaries and key takeaways
- 📋 **Resources**: Additional references and materials
- 📑 **PDFs**: Embedded or linked PDF documents (saved as HTML with download links)

## How It Works

### API Integration
The downloader uses Coursera's supplement API:
```
GET /api/onDemandSupplements.v1/{courseId}~{itemId}
```

This returns HTML content which is saved directly as `.html` files.

### Discovery Process
1. Reads lesson metadata from scraped course structure
2. Identifies items with `contentSummary.typeName == "supplement"`
3. Extracts course_id and item_id for each supplement
4. Downloads HTML content via the supplement API
5. Saves with sequential naming: `{seq}_{name}.html`

### File Naming
- Uses the same sanitization as videos
- Sequential numbering within each lesson
- Safe filenames (no special characters)
- Example: `1_Vocabulary_List.html`

## Statistics Output
The download command now shows three categories:
```
SUCCESS: Downloaded content
Videos: 15 downloaded | 0 skipped | 0 failed
Subtitles: 15 downloaded | 0 skipped | 0 failed
Supplements: 23 downloaded | 5 skipped | 1 failed
```

## Error Handling
- Gracefully handles supplements without content
- Skips already downloaded supplements
- Continues downloading even if some supplements fail
- Logs warnings for failed downloads

## Backward Compatibility
- Supplement download is **opt-in** (disabled by default)
- Existing commands work exactly as before
- No changes to video/subtitle download behavior
- No breaking changes to CLI or APIs

## Technical Details

### Code Changes
1. **API Endpoint**: Added `supplement_content` endpoint to `config/api_endpoints.json`
2. **Downloader**: Extended `EnhancedVideoDownloader` class in `src/api/enhanced_downloader.py`
   - Added `download_supplements` parameter
   - Added `_discover_supplement_items()` method
   - Added `_fetch_supplement_content()` async method
   - Added `_save_html_content()` async method
   - Updated download statistics tracking
3. **CLI**: Updated `download` command in `src/main.py`
   - Added `--supplements/--no-supplements` flag
   - Updated output messages
   - Added supplement statistics display

### Dependencies
No new dependencies required. Uses existing libraries:
- `aiohttp` for async HTTP requests
- `aiofiles` for async file operations
- `click` for CLI options

## Examples

### Example 1: Download Everything for a Course
```bash
# First scrape the course
python -m src.main scrape business-english-intro

# Then download all content
python -m src.main download business-english-intro --supplements --resolution 720p
```

### Example 2: Download Only Supplements (for quick reference)
```bash
python -m src.main download business-english-intro --no-subtitles --supplements
```

### Example 3: Resume Interrupted Download with Supplements
```bash
python -m src.main download business-english-intro --supplements --resume
```

## Troubleshooting

### No supplements found
- Not all courses have supplement materials
- Some courses use different content types (quizzes, assignments, etc.)
- Ensure the course was scraped with the latest version

### Supplement download failed
- Check authentication (COURSERA_API_TOKEN in .env)
- Some supplements may be locked or unavailable
- Check logs for specific error messages

### Empty HTML files
- Some supplements may not have content
- The API may return empty responses for certain items
- These are logged as warnings

## Future Enhancements
Potential improvements for future versions:
- Support for other content types (quizzes, peer reviews, etc.)
- PDF extraction and download
- Asset embedding in HTML files
- Markdown conversion option
- Custom supplement filters

## Testing
See `test_supplement_download.md` for detailed testing instructions.

## Contributing
When contributing supplement-related features:
1. Maintain backward compatibility
2. Add appropriate error handling
3. Update documentation
4. Include tests for new functionality
5. Follow existing code patterns

## License
Same as the main project.
