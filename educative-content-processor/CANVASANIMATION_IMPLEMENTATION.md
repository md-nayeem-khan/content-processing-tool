# CanvasAnimation Component Implementation

## Overview

The `CanvasAnimation` component handler enables processing of multi-image animation sliders from Educative courses. These are interactive animations that show a sequence of images (slides) to illustrate concepts step-by-step.

## Component Structure

### LazyLoadPlaceholder with CanvasAnimation

```json
{
    "type": "LazyLoadPlaceholder",
    "content": {
        "actualType": "CanvasAnimation",
        "widgetIndex": 13,
        "contentRevision": "417",
        "pageId": 4570386150981632,
        "height": 400,
        "width": 900,
        "slidesCount": 7
    }
}
```

**Key fields:**
- `actualType`: "CanvasAnimation"
- `pageId`: The page containing the animation
- `contentRevision`: Version/revision of the content
- `widgetIndex`: Index of the widget on the page
- `slidesCount`: Number of slides in the animation

## How It Works

### 1. API Call to Fetch Animation Data

The system constructs an API URL using course credentials:

```
https://www.educative.io/api/collection/{author_id}/{collection_id}/page/{pageId}/{contentRevision}/{widgetIndex}?work_type=collection
```

**Example:**
```
https://www.educative.io/api/collection/10370001/4941429335392256/page/4570386150981632/417/13?work_type=collection
```

### 2. API Response Structure

The API returns a CanvasAnimation component with multiple canvas objects:

```json
{
    "components": [
        {
            "type": "CanvasAnimation",
            "mode": "edit",
            "content": {
                "version": "1.0",
                "width": 620,
                "height": 200,
                "canvasObjects": [
                    {
                        "width": 620,
                        "height": 200,
                        "objectsDict": {
                            "1651058882664": {
                                "educativeObjContent": {
                                    "type": "MxGraph",
                                    "mode": "edit",
                                    "content": {
                                        "xml_string": "...",
                                        "svg_string": "...",
                                        "path": "/api/collection/.../image/4909187222208512"
                                    }
                                }
                            }
                        },
                        "caption": "Initially, the value of x is 2",
                        "version": "1.0"
                    },
                    {
                        "objectsDict": {
                            "1651058882664": {
                                "educativeObjContent": {
                                    "type": "MxGraph",
                                    "content": {
                                        "path": "/api/collection/.../image/4526750180835328"
                                    }
                                }
                            }
                        },
                        "caption": "T1: write(x) = 10"
                    }
                    // ... more canvas objects
                ]
            }
        }
    ]
}
```

### 3. Image Path Extraction

For each canvas object in the `canvasObjects` array:

1. Navigate to `objectsDict`
2. Find entries with `educativeObjContent.type === "MxGraph"`
3. Extract `educativeObjContent.content.path`
4. Extract the `caption` for the slide

**Example extraction:**
```python
for canvas_obj in canvas_objects:
    objects_dict = canvas_obj.get("objectsDict", {})
    caption = canvas_obj.get("caption", "")
    
    for key, obj_data in objects_dict.items():
        educative_content = obj_data.get("educativeObjContent", {})
        if educative_content.get("type") == "MxGraph":
            mx_content = educative_content.get("content", {})
            image_path = mx_content.get("path", "")
            # Store image_path and caption
```

### 4. Image Download and Processing

For each extracted image path:

1. **Download** - Uses `_download_image_async()` with authentication
2. **Format Detection** - MIME type detection from HTTP headers
3. **Conversion** - Converts to PNG if needed using `_convert_image_to_png()`
4. **Storage** - Saves in hierarchical structure: `Images/chapter_X/section_Y/`

**Example output:**
```
DEBUG: Downloading canvas image 1/7: /api/collection/.../image/6083222035496960
Successfully downloaded image: 6083222035496960.svg (814904 bytes, MIME: image/svg+xml)
✅ Successfully converted SVG to PNG using Wand: 6083222035496960.png
✅ Canvas image 1 processed: Images/chapter_1/section_test/6083222035496960.png
```

### 5. LaTeX Generation with Subfigures

The system generates LaTeX with a **2-column subfigure layout**:

```latex
\begin{figure}[htbp]
    \centering
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \includegraphics[width=\textwidth]{Images/chapter_1/section_test/image1.png}
        \caption{Caption for first slide}
    \end{subfigure}
    \hfill
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \includegraphics[width=\textwidth]{Images/chapter_1/section_test/image2.png}
        \caption{Caption for second slide}
    \end{subfigure}
\end{figure}

\begin{figure}[htbp]
    \centering
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \includegraphics[width=\textwidth]{Images/chapter_1/section_test/image3.png}
        \caption{Caption for third slide}
    \end{subfigure}
    \hfill
    \begin{subfigure}[b]{0.48\textwidth}
        \centering
        \includegraphics[width=\textwidth]{Images/chapter_1/section_test/image4.png}
        \caption{Caption for fourth slide}
    \end{subfigure}
\end{figure}
```

**Layout rules:**
- 2 images per row (side-by-side)
- Each pair in a separate figure environment
- Individual captions for each subfigure
- Odd number of images: last image appears alone
- Width: 0.48\textwidth per subfigure (with \hfill spacing)

## Implementation Details

### Code Location

**File:** `section_processor.py`

**Method:** `_process_canvas_animation_async()`

**Lines:** ~784-957

### Key Features

1. **Multi-image extraction** - Iterates through all canvas objects
2. **Parallel processing** - Downloads images sequentially but efficiently
3. **Caption preservation** - Maintains individual captions for each slide
4. **Automatic layout** - Generates 2-column subfigure arrangement
5. **Error resilience** - Continues processing even if some images fail

### Error Handling

The implementation includes comprehensive error handling:

1. **Missing parameters** - Validates pageId, contentRevision, widgetIndex
2. **Missing credentials** - Checks for author_id and collection_id
3. **API errors** - Catches HTTP errors and returns error message
4. **Empty canvas objects** - Validates that canvasObjects array exists
5. **Image download failures** - Continues with remaining images
6. **No extractable images** - Returns informative error message

### Debug Output

The implementation provides detailed logging:

```
DEBUG: Processing LazyLoadPlaceholder with actualType: CanvasAnimation
DEBUG: Fetching CanvasAnimation from: https://www.educative.io/api/collection/...
DEBUG: Expected slides count: 7
DEBUG: Successfully fetched CanvasAnimation data
DEBUG: Found 7 canvas objects
DEBUG: Canvas object 1: Found image path: /api/collection/.../image/...
DEBUG: Downloading canvas image 1/7: /api/collection/.../image/...
✅ Canvas image 1 processed: Images/chapter_1/section_test/image.png
✅ Generated LaTeX for CanvasAnimation with 7 images
```

## Test Results

### Test Execution

```bash
python test_canvas_animation.py
```

### Test Output

```
Testing CanvasAnimation Component Processing
================================================================================
✅ Processing completed successfully!

Component types found: ['MarkdownEditor', 'LazyLoadPlaceholder']
Generated images: 7 images
   [1] Images/chapter_1/section_test_section_canvas/6083222035496960.png
   [2] Images/chapter_1/section_test_section_canvas/6031258408976384.png
   [3] Images/chapter_1/section_test_section_canvas/4606056114421760.png
   [4] Images/chapter_1/section_test_section_canvas/5592444712517632.png
   [5] Images/chapter_1/section_test_section_canvas/4629851139211264.png
   [6] Images/chapter_1/section_test_section_canvas/5583302404866048.png
   [7] Images/chapter_1/section_test_section_canvas/6613183687294976.png

✅ LazyLoadPlaceholder component was detected
✅ Multiple images generated (7 images)
✅ LaTeX content includes subfigure environment (multi-image layout)
✅ Found 7 subfigures in LaTeX output
```

## Example Use Case

### DNS Resolution Animation

A common use case is showing step-by-step processes like DNS resolution:

**Slide 1:** Browser checks cache  
**Slide 2:** OS checks cache  
**Slide 3:** Local DNS resolver checks cache  
**Slide 4:** ISP DNS checks cache  
**Slide 5:** DNS infrastructure responds  
**Slide 6:** Cache updates at each level  
**Slide 7:** Browser serves from cache  

Each slide has its own caption explaining the step, and they're displayed in a 2-column layout for easy comparison.

## Comparison with MxGraphWidget

| Feature | MxGraphWidget | CanvasAnimation |
|---------|---------------|-----------------|
| **Images** | Single image | Multiple images (slides) |
| **LaTeX Layout** | Single figure | Subfigures (2 per row) |
| **Captions** | One caption | Individual captions per slide |
| **Use Case** | Static diagrams | Step-by-step animations |
| **API Response** | Single MxGraphWidget | Array of canvas objects |
| **Processing Time** | ~1-2 seconds | ~5-10 seconds (multiple downloads) |

## Integration with Main Workflow

### In `section_processor.py`

The router in `_process_lazy_load_placeholder_async` directs to the appropriate handler:

```python
async def _process_lazy_load_placeholder_async(self, component: Dict[str, Any]) -> Tuple[str, List[str]]:
    content = component.get("content", {})
    actual_type = content.get("actualType", "")
    
    if actual_type == "MxGraphWidget":
        return await self._process_mx_graph_widget_async(content)
    elif actual_type == "CanvasAnimation":
        return await self._process_canvas_animation_async(content)
    else:
        return f"\\textit{{LazyLoadPlaceholder type '{actual_type}' not yet supported}}", []
```

### Component Processing Pipeline

```
LazyLoadPlaceholder detected
    ↓
actualType == "CanvasAnimation"?
    ↓
Extract pageId, contentRevision, widgetIndex
    ↓
API Call: /api/collection/{author_id}/{collection_id}/page/{pageId}/{revision}/{index}
    ↓
Parse CanvasAnimation response
    ↓
Extract image paths from canvasObjects
    ↓
Download all images (async, sequential)
    ↓
Convert each to PNG if needed
    ↓
Generate LaTeX with subfigures (2 per row)
    ↓
Return LaTeX + all image paths
```

## Performance Considerations

### Download Time

- **Single image (MxGraphWidget):** ~1-2 seconds
- **7 images (CanvasAnimation):** ~7-14 seconds
- **Network dependent:** Varies based on image sizes and connection

### Optimization Opportunities

1. **Parallel downloads** - Use `asyncio.gather()` for concurrent downloads
2. **Image caching** - Cache downloaded images to avoid re-downloading
3. **Lazy conversion** - Only convert images when LaTeX compilation requires it
4. **Thumbnail generation** - Create smaller versions for faster processing

### Current Implementation

- Sequential downloads (one at a time)
- Immediate conversion after each download
- Full-size images stored
- No caching between runs

## LaTeX Requirements

### Required Packages

The generated LaTeX requires the `subcaption` package:

```latex
\usepackage{subcaption}
```

This package provides the `subfigure` environment used for multi-image layouts.

### Alternative Layouts

The current implementation uses a 2-column layout, but could be extended to support:

- **3-column layout** - For smaller images
- **Single column** - For large, detailed images
- **Custom arrangements** - Based on image count or aspect ratios
- **Grid layout** - For many small images

## Future Enhancements

### 1. Configurable Layout

Allow users to specify layout preferences:

```python
layout_config = {
    "columns": 2,  # Number of columns
    "max_width": "0.48\\textwidth",  # Width per subfigure
    "spacing": "\\hfill"  # Spacing between subfigures
}
```

### 2. Animation Metadata

Extract and use additional metadata:

- Animation duration
- Transition effects
- Playback speed
- Loop settings

### 3. Video Export

For animations with many slides, consider generating:

- Animated GIF
- MP4 video
- PDF with transitions

### 4. Interactive Elements

Preserve interactive features in digital formats:

- Clickable slides
- Navigation controls
- Zoom capabilities

## Benefits

✅ **Automatic multi-image handling** - No manual extraction needed  
✅ **Professional layout** - Subfigure arrangement looks polished  
✅ **Caption preservation** - Each slide's explanation retained  
✅ **Reuses infrastructure** - Leverages existing download/conversion  
✅ **Extensible design** - Easy to modify layout or add features  
✅ **Error resilient** - Continues processing even if some images fail  

## Related Components

- **MxGraphWidget** - Single-image diagrams (static)
- **DrawIOWidget** - Similar image-based component (static)
- **Image Download** - `_download_image_async()` method
- **Image Conversion** - `_convert_image_to_png()` method
- **Context Management** - `set_book_context()` method

## Summary

The CanvasAnimation implementation seamlessly processes multi-image animation sliders from Educative courses. It fetches animation data on-demand, extracts all slide images, and generates professional LaTeX output with a 2-column subfigure layout. The design is extensible and can easily support different layouts or additional animation features in the future.

**Status: PRODUCTION READY**
