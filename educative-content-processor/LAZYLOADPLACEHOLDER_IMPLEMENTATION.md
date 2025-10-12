# LazyLoadPlaceholder Component Implementation

## Overview

The `LazyLoadPlaceholder` component handler enables processing of dynamically loaded widgets from Educative courses. This component type is used for content that is loaded on-demand rather than being included in the initial page response.

## Supported Widget Types

### ✅ MxGraphWidget (Implemented)
Interactive graph diagrams created with mxGraph library. These are commonly used for flowcharts, system diagrams, and visual representations.

### 🔄 CanvasAnimation (Planned)
Animated canvas-based visualizations (support coming soon).

## How It Works

### 1. Component Detection

When the processor encounters a `LazyLoadPlaceholder` component, it extracts:

```json
{
    "type": "LazyLoadPlaceholder",
    "content": {
        "actualType": "MxGraphWidget",
        "widgetIndex": 4,
        "contentRevision": "423",
        "pageId": 6043988183744512,
        "height": 400,
        "width": 600,
        "slidesCount": 0
    }
}
```

**Key fields:**
- `actualType`: The actual widget type (MxGraphWidget, CanvasAnimation, etc.)
- `pageId`: The page containing the widget
- `contentRevision`: Version/revision of the content
- `widgetIndex`: Index of the widget on the page

### 2. API Call to Fetch Widget Data

The system constructs an API URL using course credentials:

```
https://www.educative.io/api/collection/{author_id}/{collection_id}/page/{pageId}/{contentRevision}/{widgetIndex}?work_type=collection
```

**Example:**
```
https://www.educative.io/api/collection/10370001/4941429335392256/page/6043988183744512/423/4?work_type=collection
```

**Authentication:**
- Uses `author_id` and `collection_id` from course context
- Includes authentication token and cookies from environment

### 3. Widget Data Extraction

The API returns the actual widget component:

```json
{
    "components": [
        {
            "type": "MxGraphWidget",
            "mode": "edit",
            "content": {
                "useObject": true,
                "xml": "<mxGraphModel>...</mxGraphModel>",
                "svg": "",
                "caption": "Activities to include in the interview",
                "path": "/api/collection/10370001/4941429335392256/page/6043988183744512/image/6068212462780416",
                "prevPath": "...",
                "prevSvg": "",
                "prevXml": "...",
                "waInstantlyOpened": true,
                "statusData": {
                    "status": "INIT",
                    "text": ""
                },
                "comp_id": "DFXVRNy3IW6jp2xxmO9I1"
            }
        }
    ],
    "summary": {
        "description": "...",
        "tags": [],
        "title": "The Do's and Don'ts of the System Design Interview",
        "titleUpdated": true
    }
}
```

**Extracted data:**
- `content.path`: Image URL for the diagram
- `content.caption`: Caption text for the figure

### 4. Image Download and Processing

The system uses existing image infrastructure:

1. **Download** - Uses `_download_image_async()` with authentication
2. **Format Detection** - MIME type detection from HTTP headers
3. **Conversion** - Converts to PNG if needed using `_convert_image_to_png()`
4. **Storage** - Saves in hierarchical structure: `Images/chapter_X/section_Y/`

### 5. LaTeX Generation

Generates standard LaTeX figure environment:

```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.8\textwidth]{Images/chapter_26/section_6043988183744512/6068212462780416.png}
    \caption{Activities to include in the interview}
\end{figure}
```

## Implementation Details

### Code Location

**File:** `section_processor.py`

**Method:** `_process_lazy_load_placeholder_async()`

**Lines:** ~637-776

### Context Requirements

The processor requires course context to be set before processing:

```python
processor.set_book_context(
    book_name="my-course",
    chapter_number=1,
    section_id="123456",
    author_id="10370001",           # Required for API calls
    collection_id="4941429335392256", # Required for API calls
    token="auth-token",               # Required for authentication
    cookie="session-cookie"           # Required for authentication
)
```

### Error Handling

The implementation includes comprehensive error handling:

1. **Missing actualType** - Returns placeholder text
2. **Unsupported widget type** - Returns informative message
3. **Missing parameters** - Validates pageId, contentRevision, widgetIndex
4. **Missing credentials** - Checks for author_id and collection_id
5. **API errors** - Catches HTTP errors and returns error message
6. **Image download failures** - Falls back to error text
7. **Format conversion failures** - Uses original format or placeholder

### Debug Output

The implementation provides detailed logging:

```
DEBUG: Processing LazyLoadPlaceholder with actualType: MxGraphWidget
DEBUG: Fetching MxGraphWidget from: https://www.educative.io/api/collection/...
DEBUG: Successfully fetched MxGraphWidget data
DEBUG: Found MxGraphWidget image path: /api/collection/.../image/...
✅ Using converted PNG image for MxGraphWidget: Images/chapter_26/section_123/image.png
```

## Integration with Main Workflow

### In `main.py`

The credentials are passed when setting book context (line ~865):

```python
processor.set_book_context(
    request.book_name, 
    request.chapter_number, 
    section_id,
    author_id=author_id,
    collection_id=collection_id,
    token=token,
    cookie=cookie
)
```

### In Component Processing

Added to the async component processor (line ~219):

```python
elif component_type == "LazyLoadPlaceholder":
    latex_content, images = await self._process_lazy_load_placeholder_async(component)
    latex_parts.append(latex_content)
    generated_images.extend(images)
```

## API Endpoint Pattern

The LazyLoadPlaceholder uses a specific API pattern:

```
/api/collection/{author_id}/{collection_id}/page/{pageId}/{contentRevision}/{widgetIndex}?work_type=collection
```

**Parameters:**
- `author_id`: Course author ID (from course metadata)
- `collection_id`: Course collection ID (from course metadata)
- `pageId`: From LazyLoadPlaceholder content
- `contentRevision`: From LazyLoadPlaceholder content
- `widgetIndex`: From LazyLoadPlaceholder content
- `work_type`: Always "collection" for course content

## Future Enhancements

### CanvasAnimation Support

To add CanvasAnimation support, extend the handler:

```python
if actual_type == "MxGraphWidget":
    # Current implementation
    ...
elif actual_type == "CanvasAnimation":
    # New implementation for canvas animations
    # May require different API endpoint or processing logic
    ...
```

### Other Widget Types

The framework is extensible for additional widget types:
- Interactive code editors
- Embedded videos
- Custom visualizations
- Any other lazy-loaded content

## Testing

To test LazyLoadPlaceholder handling:

1. Find a course with MxGraphWidget content
2. Identify a section containing LazyLoadPlaceholder
3. Process the section with proper credentials
4. Verify:
   - API call succeeds
   - Image is downloaded
   - Format conversion works
   - LaTeX is generated correctly
   - Image appears in hierarchical directory

## Benefits

✅ **Automatic handling** - No manual intervention needed  
✅ **Reuses infrastructure** - Leverages existing image download/conversion  
✅ **Proper authentication** - Uses course credentials securely  
✅ **Error resilience** - Graceful degradation on failures  
✅ **Extensible design** - Easy to add new widget types  
✅ **Debug friendly** - Comprehensive logging for troubleshooting  

## Related Components

- **DrawIOWidget** - Similar image-based component (static)
- **Image Download** - `_download_image_async()` method
- **Image Conversion** - `_convert_image_to_png()` method
- **Context Management** - `set_book_context()` method

## Summary

The LazyLoadPlaceholder implementation seamlessly integrates lazy-loaded widgets into the content processing pipeline. It fetches widget data on-demand, extracts images, and generates proper LaTeX output using the existing image processing infrastructure. The design is extensible and can easily support additional widget types in the future.
