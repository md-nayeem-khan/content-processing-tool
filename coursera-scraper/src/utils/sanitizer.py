"""File name sanitization and path utilities."""

import re
import unicodedata
from pathlib import Path
from typing import Union
from pathvalidate import sanitize_filename, sanitize_filepath


def sanitize_course_name(name: str, max_length: int = 100) -> str:
    """Sanitize course name for use as directory name."""
    # Remove or replace problematic characters
    sanitized = sanitize_filename(name, replacement_text="_")

    # Convert to lowercase and replace spaces with hyphens
    sanitized = sanitized.lower().replace(" ", "-")

    # Remove multiple consecutive hyphens/underscores
    sanitized = re.sub(r'[-_]+', '-', sanitized)

    # Trim length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip('-_')

    # Ensure it doesn't start/end with problematic characters
    sanitized = sanitized.strip('-_.')

    # Fallback if name becomes empty
    if not sanitized:
        sanitized = "untitled-course"

    return sanitized


def sanitize_module_name(name: str, order: int = 0, max_length: int = 80) -> str:
    """Sanitize module name with optional ordering prefix."""
    # Basic sanitization
    sanitized = sanitize_filename(name, replacement_text="_")

    # Replace spaces with hyphens and lowercase
    sanitized = sanitized.lower().replace(" ", "-")

    # Remove multiple consecutive hyphens/underscores
    sanitized = re.sub(r'[-_]+', '-', sanitized)

    # Add ordering prefix
    if order > 0:
        prefix = f"module-{order:02d}-"
        available_length = max_length - len(prefix)
        if len(sanitized) > available_length:
            sanitized = sanitized[:available_length].rstrip('-_')
        sanitized = prefix + sanitized
    else:
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length].rstrip('-_')

    # Clean up
    sanitized = sanitized.strip('-_.')

    # Fallback
    if not sanitized or sanitized == f"module-{order:02d}-":
        sanitized = f"module-{order:02d}-untitled" if order > 0 else "untitled-module"

    return sanitized


def sanitize_lesson_name(name: str, order: int = 0, max_length: int = 80) -> str:
    """Sanitize lesson name with optional ordering prefix."""
    # Basic sanitization
    sanitized = sanitize_filename(name, replacement_text="_")

    # Replace spaces with hyphens and lowercase
    sanitized = sanitized.lower().replace(" ", "-")

    # Remove multiple consecutive hyphens/underscores
    sanitized = re.sub(r'[-_]+', '-', sanitized)

    # Add ordering prefix
    if order > 0:
        prefix = f"lesson-{order:02d}-"
        available_length = max_length - len(prefix)
        if len(sanitized) > available_length:
            sanitized = sanitized[:available_length].rstrip('-_')
        sanitized = prefix + sanitized
    else:
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length].rstrip('-_')

    # Clean up
    sanitized = sanitized.strip('-_.')

    # Fallback
    if not sanitized or sanitized == f"lesson-{order:02d}-":
        sanitized = f"lesson-{order:02d}-untitled" if order > 0 else "untitled-lesson"

    return sanitized


def sanitize_sequential_video_name(sequence_number: int, original_name: str, extension: str = None, max_length: int = 255) -> str:
    """Sanitize video file name with sequential numbering prefix."""
    # Create prefix with sequence number
    prefix = f"{sequence_number}_"

    # Remove extension if present to handle separately
    base_name = original_name
    if extension and original_name.endswith(extension):
        base_name = original_name[:-len(extension)]

    # Remove resolution patterns (e.g., _720p, _480p, _1080p, etc.)
    resolution_patterns = ['_720p', '_540p', '_480p', '_360p', '_1080p', '_240p']
    for pattern in resolution_patterns:
        if base_name.endswith(pattern):
            base_name = base_name[:-len(pattern)]
            break

    # Basic sanitization
    sanitized = sanitize_filename(base_name, replacement_text="_")

    # Normalize unicode
    sanitized = unicodedata.normalize('NFKD', sanitized)

    # Additional cleanup
    sanitized = re.sub(r'[^\w\-_. ]', '_', sanitized)
    sanitized = re.sub(r'[_\-\s]+', '_', sanitized)
    sanitized = sanitized.strip('_.')

    # Calculate available length for base name (accounting for prefix and extension)
    available_length = max_length - len(prefix)
    if extension:
        if not extension.startswith('.'):
            extension = '.' + extension
        available_length -= len(extension)

    # Trim base name if needed
    if len(sanitized) > available_length:
        sanitized = sanitized[:available_length].rstrip('_.')

    # Combine prefix with sanitized name
    result = prefix + sanitized

    # Add extension back
    if extension:
        result += extension

    # Fallback if name becomes too short
    if len(sanitized.strip('_')) == 0:
        timestamp = str(int(__import__('time').time()))
        if extension:
            result = f"{prefix}video_{timestamp}{extension}"
        else:
            result = f"{prefix}video_{timestamp}"

    return result


def sanitize_file_name(name: str, extension: str = None, max_length: int = 255) -> str:
    """Sanitize file name for downloads."""
    # Remove extension if present to handle separately
    base_name = name
    if extension and name.endswith(extension):
        base_name = name[:-len(extension)]

    # Basic sanitization
    sanitized = sanitize_filename(base_name, replacement_text="_")

    # Normalize unicode
    sanitized = unicodedata.normalize('NFKD', sanitized)

    # Additional cleanup
    sanitized = re.sub(r'[^\w\-_. ]', '_', sanitized)
    sanitized = re.sub(r'[_\-\s]+', '_', sanitized)
    sanitized = sanitized.strip('_.')

    # Add extension back
    if extension:
        if not extension.startswith('.'):
            extension = '.' + extension
        sanitized += extension

    # Trim length
    if len(sanitized) > max_length:
        if extension:
            available_length = max_length - len(extension)
            sanitized = sanitized[:available_length].rstrip('_.') + extension
        else:
            sanitized = sanitized[:max_length].rstrip('_.')

    # Fallback
    if not sanitized or sanitized == extension:
        timestamp = str(int(__import__('time').time()))
        if extension:
            sanitized = f"untitled_{timestamp}{extension}"
        else:
            sanitized = f"untitled_{timestamp}"

    return sanitized


def ensure_unique_path(path: Union[str, Path]) -> Path:
    """Ensure path is unique by appending number if needed."""
    path = Path(path)

    if not path.exists():
        return path

    # Extract parts
    parent = path.parent
    stem = path.stem
    suffix = path.suffix

    # Find unique name
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def create_safe_directory(path: Union[str, Path]) -> Path:
    """Create directory safely, handling conflicts."""
    path = Path(path)

    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except OSError as e:
        # If creation fails, try with a unique name
        unique_path = ensure_unique_path(path)
        unique_path.mkdir(parents=True, exist_ok=True)
        return unique_path


def get_file_extension(url: str, content_type: str = None) -> str:
    """Extract file extension from URL or content type."""
    # Try URL first
    url_lower = url.lower()
    for ext in ['.mp4', '.pdf', '.pptx', '.docx', '.txt', '.html', '.json', '.zip']:
        if ext in url_lower:
            return ext

    # Try content type
    if content_type:
        content_type = content_type.lower()
        type_mapping = {
            'video/mp4': '.mp4',
            'application/pdf': '.pdf',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'text/plain': '.txt',
            'text/html': '.html',
            'application/json': '.json',
            'application/zip': '.zip'
        }
        return type_mapping.get(content_type, '.bin')

    return '.bin'