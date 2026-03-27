"""Authentication handling for Coursera API."""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from ..utils.exceptions import AuthenticationError
from ..utils.logger import LoggerMixin


class CourseraAuth(LoggerMixin):
    """Handles cookie-based authentication for Coursera API."""

    def __init__(self, cauth_cookie: Optional[str] = None, csrf_token: Optional[str] = None):
        """Initialize authentication with cookies and CSRF token."""
        # Load environment variables
        load_dotenv()

        # Load authentication credentials
        self.cauth_cookie = cauth_cookie or self._load_from_env('COURSERA_CAUTH_COOKIE')
        self.csrf_token = csrf_token or self._load_from_env('COURSERA_CSRF_TOKEN')
        self.csrf3_token_cookie = self._load_from_env('COURSERA_CSRF3_TOKEN_COOKIE')

        # Validate required credentials
        if not self.cauth_cookie:
            raise AuthenticationError(
                "No Coursera CAUTH cookie provided. "
                "Set COURSERA_CAUTH_COOKIE environment variable or pass cauth_cookie directly."
            )

        # CSRF token is optional for some GET requests
        if not self.csrf_token:
            self.logger.warning(
                "No CSRF token provided. Some API calls (especially POST) may fail. "
                "Set COURSERA_CSRF_TOKEN for full functionality."
            )

        self.logger.info("Cookie-based authentication initialized successfully")

    def _load_from_env(self, key: str) -> Optional[str]:
        """Load value from environment variables."""
        return os.getenv(key)

    def get_headers(self, include_csrf: bool = True, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }

        # Add CSRF token only if requested and available
        if include_csrf and self.csrf_token:
            headers['x-csrf3-token'] = self.csrf_token

        # Add optional Origin and Referer for some endpoints
        if include_csrf:
            headers.update({
                'Content-Type': 'application/json',
                'Origin': 'https://www.coursera.org',
                'Referer': 'https://www.coursera.org/',
            })

        # Add custom headers from endpoint configuration
        if custom_headers:
            headers.update(custom_headers)

        return headers

    def get_cookies(self) -> Dict[str, str]:
        """Get cookies for API requests."""
        cookies = {
            'CAUTH': self.cauth_cookie,
        }

        # Add CSRF3-Token cookie if available
        if self.csrf3_token_cookie:
            cookies['CSRF3-Token'] = self.csrf3_token_cookie

        return cookies

    def validate_credentials(self) -> bool:
        """Validate that credentials are properly formatted."""
        if not self.cauth_cookie:
            return False

        # Basic CAUTH cookie format validation
        if len(self.cauth_cookie) < 20:
            return False

        # CSRF token validation (optional)
        if self.csrf_token and len(self.csrf_token) < 10:
            return False

        return True

    def update_credentials(self, cauth_cookie: Optional[str] = None, csrf_token: Optional[str] = None) -> None:
        """Update authentication credentials."""
        if cauth_cookie:
            old_preview = self.cauth_cookie[:20] + "..." if self.cauth_cookie else "None"
            self.cauth_cookie = cauth_cookie
            new_preview = cauth_cookie[:20] + "..."
            self.logger.info(f"CAUTH cookie updated from {old_preview} to {new_preview}")

        if csrf_token:
            self.csrf_token = csrf_token
            self.logger.info("CSRF token updated")

    def is_authenticated(self) -> bool:
        """Check if authentication is properly set up."""
        return (self.cauth_cookie is not None and
                self.validate_credentials())

    def __repr__(self) -> str:
        """String representation of auth object."""
        cauth_preview = self.cauth_cookie[:20] + "..." if self.cauth_cookie else "None"
        csrf_preview = self.csrf_token[:10] + "..." if self.csrf_token else "None"
        return f"CourseraAuth(cauth={cauth_preview}, csrf={csrf_preview})"