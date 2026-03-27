# Test Supplement Download Feature

## Overview
This document describes how to test the new supplement download feature.

## Prerequisites
1. Course must be already scraped using the `scrape` command
2. Authentication must be configured (.env file with COURSERA_API_TOKEN)
3. Course must contain supplement materials (e.g., business-english-intro has many supplements)

## Test Commands

### 1. Test with supplements enabled (default videos + subtitles + supplements)
```bash
python -m src.main download business-english-intro --supplements
```

### 2. Test with only supplements (no videos, no subtitles)
```bash
python -m src.main download business-english-intro --no-subtitles --supplements
```

### 3. Test full download (videos + subtitles + supplements)
```bash
python -m src.main download business-english-intro --subtitles --supplements
```

### 4. Test without supplements (original behavior - only videos and subtitles)
```bash
python -m src.main download business-english-intro
```

## Expected Results

### Supplement Files
- Supplements should be saved as `.html` files
- Sequential naming: `1_supplement_name.html`, `2_supplement_name.html`, etc.
- Files should contain the HTML content from the API's `renderableHtml` field
- Files should be saved in the same lesson directory as videos

### Statistics Output
The command should show three categories of statistics:
```
SUCCESS: Downloaded content
Videos: X downloaded | Y skipped | Z failed
Subtitles: X downloaded | Y skipped | Z failed
Supplements: X downloaded | Y skipped | Z failed
```

### Sample Supplement Content
Supplement HTML files should contain structured content like:
- Vocabulary lists
- Reading materials
- Summary pages
- Additional resources

## Verification Steps

1. **Check file existence**: Navigate to a lesson directory and verify `.html` files exist
2. **Check file content**: Open an HTML file and verify it contains valid HTML markup
3. **Check sequential naming**: Verify files follow the naming pattern: `{seq}_{name}.html`
4. **Check statistics**: Verify the console output shows correct counts
5. **Check error handling**: Test with a course that has no supplements

## Example Test Course
The `business-english-intro` course is ideal for testing because it contains many supplement items:
- Vocabulary lists
- Summary pages
- Reading materials

Located in items like:
- "rdDyY" - Vocabulary List
- "090KY" - READ FIRST
- "4Eq2G" - Summary
- And many more throughout the course

## Notes
- Supplement download is optional (off by default) to maintain backward compatibility
- Supplements are downloaded only if `--supplements` flag is provided
- The feature gracefully handles cases where supplements don't have content
- Existing downloaded supplements are skipped to avoid re-downloading
