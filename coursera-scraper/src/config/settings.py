"""Configuration management for the Coursera scraper."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field

from ..utils.exceptions import ConfigurationError
from ..utils.logger import LoggerMixin


@dataclass
class AppSettings:
    """Application settings configuration."""
    default_output_dir: str = "./courses"
    filename_sanitization: bool = True
    max_filename_length: int = 100
    create_backups: bool = False
    log_level: str = "INFO"
    max_concurrent_requests: int = 5
    request_timeout: int = 30
    retry_attempts: int = 3
    retry_backoff_factor: float = 2.0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppSettings':
        """Create settings from dictionary."""
        # Filter out unknown keys
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)


@dataclass
class DownloadSettings:
    """Download configuration settings."""
    download_files: bool = True
    file_types: list = field(default_factory=lambda: ["pdf", "mp4", "txt", "docx", "pptx", "html", "json"])
    max_file_size_mb: int = 500
    create_metadata: bool = True
    save_urls: bool = True
    concurrent_downloads: int = 3
    skip_existing: bool = True
    create_progress_file: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DownloadSettings':
        """Create download settings from dictionary."""
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)


class ConfigManager(LoggerMixin):
    """Manages all configuration files and settings."""

    def __init__(self, config_dir: Union[str, Path] = "config"):
        """Initialize configuration manager."""
        self.config_dir = Path(config_dir)
        self.app_settings: Optional[AppSettings] = None
        self.download_settings: Optional[DownloadSettings] = None
        self._api_config_data: Optional[Dict[str, Any]] = None

        # Load configurations
        self._load_all_configs()
        self.logger.info(f"Configuration manager initialized with config dir: {self.config_dir}")

    def _load_all_configs(self) -> None:
        """Load all configuration files."""
        self._load_app_settings()
        self._load_download_settings()
        self._load_api_config()

    def _load_app_settings(self) -> None:
        """Load application settings from settings.json."""
        settings_path = self.config_dir / "settings.json"

        if not settings_path.exists():
            self.logger.warning(f"Settings file not found: {settings_path}, using defaults")
            self.app_settings = AppSettings()
            return

        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.app_settings = AppSettings.from_dict(data)
            self.logger.info("Application settings loaded successfully")

        except (json.JSONDecodeError, TypeError) as e:
            raise ConfigurationError(f"Invalid settings.json: {e}")

    def _load_download_settings(self) -> None:
        """Load download settings from download_rules.json."""
        download_path = self.config_dir / "download_rules.json"

        if not download_path.exists():
            self.logger.warning(f"Download rules file not found: {download_path}, using defaults")
            self.download_settings = DownloadSettings()
            return

        try:
            with open(download_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.download_settings = DownloadSettings.from_dict(data)
            self.logger.info("Download settings loaded successfully")

        except (json.JSONDecodeError, TypeError) as e:
            raise ConfigurationError(f"Invalid download_rules.json: {e}")

    def _load_api_config(self) -> None:
        """Load API configuration from api_endpoints.json."""
        api_path = self.config_dir / "api_endpoints.json"

        if not api_path.exists():
            raise ConfigurationError(f"Required API config file not found: {api_path}")

        try:
            with open(api_path, 'r', encoding='utf-8') as f:
                self._api_config_data = json.load(f)
            self.logger.info("API configuration loaded successfully")

        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid api_endpoints.json: {e}")

    def get_api_config_data(self) -> Dict[str, Any]:
        """Get raw API configuration data."""
        if self._api_config_data is None:
            raise ConfigurationError("API configuration not loaded")
        return self._api_config_data

    def get_output_dir(self) -> Path:
        """Get the configured output directory."""
        output_dir = Path(self.app_settings.default_output_dir)
        output_dir.mkdir(exist_ok=True)
        return output_dir

    def get_logs_dir(self) -> Path:
        """Get the logs directory."""
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        return logs_dir

    def is_file_type_allowed(self, file_type: str) -> bool:
        """Check if file type is allowed for download."""
        if not self.download_settings.download_files:
            return False

        # Remove leading dot if present
        file_type = file_type.lstrip('.').lower()
        return file_type in [ft.lower() for ft in self.download_settings.file_types]

    def get_max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.download_settings.max_file_size_mb * 1024 * 1024

    def override_from_env(self) -> None:
        """Override settings with environment variables."""
        if not self.app_settings:
            return

        # Override with environment variables
        env_overrides = {
            'LOG_LEVEL': 'log_level',
            'MAX_CONCURRENT_REQUESTS': 'max_concurrent_requests',
            'REQUEST_TIMEOUT': 'request_timeout',
            'RETRY_ATTEMPTS': 'retry_attempts',
        }

        for env_var, setting_name in env_overrides.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    # Convert to appropriate type
                    if setting_name in ['max_concurrent_requests', 'request_timeout', 'retry_attempts']:
                        value = int(env_value)
                    else:
                        value = env_value

                    setattr(self.app_settings, setting_name, value)
                    self.logger.info(f"Setting {setting_name} overridden from environment: {value}")

                except ValueError as e:
                    self.logger.warning(f"Invalid environment value for {env_var}: {env_value}")

    def validate_config(self) -> bool:
        """Validate all configuration settings."""
        issues = []

        # Validate app settings
        if self.app_settings:
            if self.app_settings.max_concurrent_requests < 1:
                issues.append("max_concurrent_requests must be >= 1")

            if self.app_settings.request_timeout < 1:
                issues.append("request_timeout must be >= 1")

            if self.app_settings.retry_attempts < 0:
                issues.append("retry_attempts must be >= 0")

            if self.app_settings.max_filename_length < 10:
                issues.append("max_filename_length must be >= 10")

        # Validate download settings
        if self.download_settings:
            if self.download_settings.concurrent_downloads < 1:
                issues.append("concurrent_downloads must be >= 1")

            if self.download_settings.max_file_size_mb < 1:
                issues.append("max_file_size_mb must be >= 1")

        # Validate API config
        if self._api_config_data:
            required_keys = ['base_url', 'endpoints']
            for key in required_keys:
                if key not in self._api_config_data:
                    issues.append(f"Missing required API config key: {key}")

        if issues:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"- {issue}" for issue in issues)
            raise ConfigurationError(error_msg)

        self.logger.info("Configuration validation passed")
        return True

    def reload_config(self) -> None:
        """Reload all configuration files."""
        self.logger.info("Reloading configuration...")
        self._load_all_configs()
        self.override_from_env()
        self.validate_config()
        self.logger.info("Configuration reloaded successfully")