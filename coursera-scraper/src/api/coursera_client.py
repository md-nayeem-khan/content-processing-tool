"""Main Coursera API client."""

import time
import json
from typing import Dict, Any, Optional, Union
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .auth import CourseraAuth
from ..core.course_models import APIConfig, APIEndpointConfig
from ..utils.exceptions import (
    APIError, AuthenticationError, RateLimitError,
    CourseNotFoundError, InvalidResponseError
)
from ..utils.logger import LoggerMixin, log_api_request


class CourseraClient(LoggerMixin):
    """HTTP client for Coursera API with authentication and retry logic."""

    def __init__(
        self,
        auth: CourseraAuth,
        api_config: APIConfig,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        rate_limit_delay: float = 1.0
    ):
        """Initialize the API client."""
        self.auth = auth
        self.api_config = api_config
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0

        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],  # Updated parameter name
            backoff_factor=backoff_factor
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.logger.info(f"Coursera API client initialized with base URL: {api_config.base_url}")

    def _wait_for_rate_limit(self) -> None:
        """Implement rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _make_request(self, method: str, url: str, endpoint_headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        """Make HTTP request with cookie-based authentication and error handling."""
        # Rate limiting
        self._wait_for_rate_limit()

        # Determine if CSRF token is needed (typically for POST requests)
        include_csrf = method.upper() != 'GET'

        # Get base authentication headers
        headers = kwargs.pop('headers', {})
        auth_headers = self.auth.get_headers(include_csrf=include_csrf, custom_headers=endpoint_headers)
        headers.update(auth_headers)
        kwargs['headers'] = headers

        # Add authentication cookies
        cookies = kwargs.pop('cookies', {})
        cookies.update(self.auth.get_cookies())
        kwargs['cookies'] = cookies

        kwargs['timeout'] = self.timeout

        try:
            response = self.session.request(method, url, **kwargs)
            log_api_request(self.logger, method, url, response.status_code)

            # Handle different status codes
            if response.status_code == 401:
                raise AuthenticationError("Invalid or expired authentication cookies")
            elif response.status_code == 403:
                raise AuthenticationError("Access forbidden - check cookie permissions or CSRF token")
            elif response.status_code == 404:
                raise CourseNotFoundError(f"Resource not found: {url}")
            elif response.status_code == 429:
                raise RateLimitError("API rate limit exceeded")
            elif response.status_code >= 400:
                raise APIError(f"API request failed with status {response.status_code}: {response.text}")

            return response

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise APIError(f"Network error: {e}")

    def get(self, endpoint_name: str, **url_params) -> Dict[str, Any]:
        """Make GET request to a configured endpoint."""
        if endpoint_name not in self.api_config.endpoints:
            raise ValueError(f"Unknown endpoint: {endpoint_name}")

        # Get endpoint configuration
        endpoint = self.api_config.endpoints[endpoint_name]
        url = self.api_config.get_endpoint_url(endpoint_name, **url_params)

        try:
            # Pass endpoint-specific headers
            response = self._make_request('GET', url, endpoint_headers=endpoint.headers)
            data = response.json()
            return data

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response from {url}: {e}")
            raise InvalidResponseError(f"Invalid JSON response: {e}")

    def get_course_info(self, course_slug: str) -> Dict[str, Any]:
        """Get course information by slug/ID."""
        self.logger.info(f"Fetching course info for: {course_slug}")
        return self.get('course_info', course_slug=course_slug)

    def get_lecture_video(self, course_id: str, lecture_id: str) -> Dict[str, Any]:
        """Get lecture video details including sources, subtitles, etc."""
        self.logger.info(f"Fetching video details for lecture: {lecture_id} in course: {course_id}")
        return self.get('lecture_video', course_id=course_id, lecture_id=lecture_id)

    def get_course_modules(self, course_id: str) -> Dict[str, Any]:
        """Get course modules by course ID."""
        self.logger.info(f"Fetching modules for course: {course_id}")
        return self.get('course_modules', course_id=course_id)

    def get_course_materials(self, course_slug: str) -> Dict[str, Any]:
        """
        Get complete course materials structure using onDemandCourseMaterials.v2 API.

        This returns the proper Coursera structure with:
        - Modules (course sections)
        - Lessons (topics within modules)
        - Items (videos, readings, quizzes within lessons)
        """
        self.logger.info(f"Fetching course materials for: {course_slug}")
        return self.get('course_materials', course_slug=course_slug)

    def test_connection(self) -> bool:
        """Test API connection and authentication."""
        try:
            # Test with the video endpoint we know works
            course_id = "46b4tHEkEeWbbw5cIAKQrw"  # business-english-intro
            lecture_id = "sf1NL"  # Video email guidelines
            test_data = self.get_lecture_video(course_id, lecture_id)
            if 'elements' in test_data and 'linked' in test_data:
                self.logger.info("API connection test successful")
                return True
            else:
                self.logger.warning("API connection test: unexpected response format")
                return False

        except Exception as e:
            self.logger.error(f"API connection test failed: {e}")
            return False

    @classmethod
    def from_config_file(cls, config_path: Union[str, Path], auth: CourseraAuth) -> 'CourseraClient':
        """Create client from API configuration file."""
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"API config file not found: {config_path}")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # Parse endpoints
            endpoints = {}
            for name, endpoint_data in config_data['endpoints'].items():
                endpoints[name] = APIEndpointConfig(**endpoint_data)

            # Create API config
            api_config = APIConfig(
                base_url=config_data['base_url'],
                endpoints=endpoints
            )

            return cls(auth=auth, api_config=api_config)

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise InvalidResponseError(f"Invalid API configuration file: {e}")


class ResponseParser(LoggerMixin):
    """Utility class for parsing API responses according to configuration."""

    def __init__(self, api_config: APIConfig):
        """Initialize parser with API configuration."""
        self.api_config = api_config

    def parse_course_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse course information response."""
        endpoint = self.api_config.endpoints['course_info']
        parsed = {}

        for field in ['course_name', 'description', 'modules']:
            value = endpoint.get_mapped_value(response_data, field)
            parsed[field] = value

        self.logger.debug(f"Parsed course response: {list(parsed.keys())}")
        return parsed

    def parse_module_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse module details response."""
        endpoint = self.api_config.endpoints['module_details']
        parsed = {}

        for field in ['module_name', 'lessons']:
            value = endpoint.get_mapped_value(response_data, field)
            parsed[field] = value

        self.logger.debug(f"Parsed module response: {list(parsed.keys())}")
        return parsed

    def parse_lesson_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse lesson content response."""
        endpoint = self.api_config.endpoints['lesson_content']
        parsed = {}

        for field in ['lesson_name', 'video_url', 'assets']:
            value = endpoint.get_mapped_value(response_data, field)
            parsed[field] = value

        self.logger.debug(f"Parsed lesson response: {list(parsed.keys())}")
        return parsed