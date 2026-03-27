"""Custom exceptions for the Coursera scraper."""


class CourseraScraperError(Exception):
    """Base exception for all Coursera scraper errors."""
    pass


class APIError(CourseraScraperError):
    """Base exception for API-related errors."""
    pass


class AuthenticationError(APIError):
    """Raised when authentication fails."""
    pass


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""
    pass


class CourseNotFoundError(APIError):
    """Raised when a course is not found."""
    pass


class InvalidResponseError(APIError):
    """Raised when API response is invalid or unexpected."""
    pass


class FileSystemError(CourseraScraperError):
    """Base exception for file system related errors."""
    pass


class DirectoryCreationError(FileSystemError):
    """Raised when directory creation fails."""
    pass


class FileWriteError(FileSystemError):
    """Raised when file writing fails."""
    pass


class ConfigurationError(CourseraScraperError):
    """Raised when configuration is invalid."""
    pass


class ValidationError(CourseraScraperError):
    """Raised when input validation fails."""
    pass


class DownloadError(CourseraScraperError):
    """Raised when file download fails."""
    pass