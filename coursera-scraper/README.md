# Coursera Course Scraper

A Python CLI tool for scraping and organizing Coursera course content into structured folder hierarchies.

## Features

- **CLI Interface**: Command-line tool with rich formatting and progress bars
- **Structured Organization**: Creates organized folders with proper hierarchy (course → modules → lessons)
- **Comprehensive Content**: Downloads metadata, content URLs, and actual files
- **Configurable API**: User-provided API endpoint configurations via JSON
- **Authentication**: Secure token-based authentication via environment variables
- **Progress Tracking**: Real-time progress with resume capability for interrupted downloads
- **File Management**: Safe filename sanitization and conflict resolution
- **Error Handling**: Robust error handling with detailed logging

## Installation

1. **Clone or download** this project to your local machine

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your Coursera API token**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Coursera API token
   ```

## Configuration

### 1. Environment Variables (.env)

Create a `.env` file in the project root with your Coursera API token:

```bash
# Required: Your Coursera API authentication token
COURSERA_API_TOKEN=your_token_here

# Optional overrides
LOG_LEVEL=INFO
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=30
RETRY_ATTEMPTS=3
```

### 2. API Endpoints (config/api_endpoints.json)

Configure the Coursera API endpoints and response mappings. Update this file with the actual API URLs and response structure you provide:

```json
{
  "base_url": "https://api.coursera.org",
  "endpoints": {
    "course_info": {
      "path": "/api/courses.v1/courses/{course_slug}",
      "method": "GET",
      "response_mapping": {
        "course_name": "elements[0].name",
        "description": "elements[0].description",
        "modules": "elements[0].courseModules"
      }
    },
    "module_details": {
      "path": "/api/courses.v1/modules/{module_id}",
      "method": "GET",
      "response_mapping": {
        "module_name": "elements[0].name",
        "lessons": "elements[0].lessons"
      }
    },
    "lesson_content": {
      "path": "/api/onDemandLectures.v1/lectures/{lesson_id}",
      "method": "GET",
      "response_mapping": {
        "lesson_name": "elements[0].name",
        "video_url": "elements[0].content.definition.value",
        "assets": "elements[0].assets"
      }
    }
  }
}
```

### 3. Application Settings (config/settings.json)

Customize application behavior:

```json
{
  "default_output_dir": "./courses",
  "filename_sanitization": true,
  "max_filename_length": 100,
  "create_backups": false,
  "log_level": "INFO",
  "max_concurrent_requests": 5,
  "request_timeout": 30,
  "retry_attempts": 3,
  "retry_backoff_factor": 2
}
```

### 4. Download Rules (config/download_rules.json)

Configure what content to download:

```json
{
  "download_files": true,
  "file_types": ["pdf", "mp4", "txt", "docx", "pptx", "html", "json"],
  "max_file_size_mb": 500,
  "create_metadata": true,
  "save_urls": true,
  "concurrent_downloads": 3,
  "skip_existing": true,
  "create_progress_file": true
}
```

## Usage

### Basic Commands

**Scrape a course:**
```bash
python -m src.main scrape "machine-learning-course"
```

**Check configuration:**
```bash
python -m src.main config
```

**Test API connection:**
```bash
python -m src.main test
```

**Check course status:**
```bash
python -m src.main status
```

### Command Options

**Scrape with custom output directory:**
```bash
python -m src.main scrape "course-name" --output-dir ./my-courses
```

**Dry run (see what would be done):**
```bash
python -m src.main scrape "course-name" --dry-run
```

**Verbose output:**
```bash
python -m src.main scrape "course-name" --verbose
```

**Custom config directory:**
```bash
python -m src.main scrape "course-name" --config-dir ./my-config
```

## Output Structure

For a course named "Machine Learning Fundamentals", the scraper creates:

```
courses/
└── machine-learning-fundamentals/
    ├── course_metadata.json           # Course information
    ├── content_urls.txt               # All discovered URLs
    ├── .scraping_progress.json        # Progress tracking (hidden)
    ├── module-01-introduction/
    │   ├── module_metadata.json
    │   ├── content_urls.txt
    │   ├── lesson-01-overview/
    │   │   ├── lesson_metadata.json
    │   │   ├── content_urls.txt
    │   │   ├── video.mp4              # Downloaded content
    │   │   ├── transcript.pdf
    │   │   └── slides.pdf
    │   └── lesson-02-basics/
    │       └── ...
    └── module-02-algorithms/
        └── ...
```

## API Integration Guide

This tool requires you to provide the actual Coursera API details. Here's what you need to configure:

### 1. Obtain API Access

- Get a Coursera API token from your Coursera developer account
- Identify the correct API endpoints for course data
- Note the response structure for each endpoint

### 2. Update Configuration

- Add your token to `.env` file
- Update `config/api_endpoints.json` with actual API URLs
- Adjust response mappings based on actual API response structure

### 3. Test Connection

Run the test command to verify your setup:
```bash
python -m src.main test
```

## Troubleshooting

### Common Issues

**Authentication Failed:**
- Check that `COURSERA_API_TOKEN` is set in `.env`
- Verify your token is valid and has necessary permissions
- Ensure token format is correct (no extra spaces or quotes)

**API Connection Failed:**
- Verify `config/api_endpoints.json` has correct URLs
- Check network connectivity
- Ensure API endpoints are accessible with your token

**Configuration Error:**
- Validate JSON syntax in configuration files
- Check that all required fields are present
- Review file paths and permissions

**Course Not Found:**
- Verify the course identifier/slug is correct
- Check that the course is accessible with your account
- Ensure the course exists and is public or enrolled

### Logging

Logs are written to `logs/coursera_scraper.log` with rotation. Check logs for detailed error information:

```bash
tail -f logs/coursera_scraper.log
```

### Debug Mode

Enable verbose logging by setting environment variable:
```bash
LOG_LEVEL=DEBUG python -m src.main scrape "course-name"
```

## Development

### Project Structure

```
src/
├── main.py                # CLI entry point
├── cli/                   # CLI components
├── api/                   # API client and auth
├── core/                  # Core scraping logic
├── config/                # Configuration management
└── utils/                 # Utilities and helpers
```

### Key Components

- **CourseraClient**: API client with retry logic and rate limiting
- **CourseScraper**: Main orchestration logic
- **FileManager**: Handles directory creation and file operations
- **ConfigManager**: Manages all configuration files

### Extending

To add support for additional content types:
1. Update `config/download_rules.json` file types
2. Modify `utils/sanitizer.py` for new extensions
3. Add parsing logic in `core/scraper.py` if needed

## License

This project is provided as-is for educational purposes. Ensure you comply with Coursera's Terms of Service when using this tool.

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review logs for detailed error messages
3. Verify your API configuration and credentials
4. Test with a simple course first

---

**Note**: This tool requires you to provide your own Coursera API access and configuration. The actual API endpoints and authentication methods depend on your specific setup with Coursera's developer platform.