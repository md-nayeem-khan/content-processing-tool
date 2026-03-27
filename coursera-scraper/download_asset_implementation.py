"""Missing download_asset method that needs to be added to FileManager class."""

import requests
import time
from pathlib import Path
from typing import Optional
from ..core.course_models import ContentAsset
from ..utils.sanitizer import sanitize_file_name

def download_asset(self, asset: ContentAsset, target_directory: Path) -> bool:
    """Download a single content asset (video, PDF, document, etc.)."""
    if not asset.url:
        self.logger.warning(f"No URL provided for asset: {asset.name}")
        return False

    try:
        target_directory.mkdir(parents=True, exist_ok=True)

        # Sanitize filename
        safe_filename = sanitize_file_name(asset.name)
        file_path = target_directory / safe_filename

        # Skip if file already exists and skip_existing is enabled
        if file_path.exists():
            self.logger.info(f"File already exists: {file_path}")
            asset.local_path = file_path
            return True

        # Download with authentication headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }

        self.logger.info(f"Downloading: {asset.name} -> {file_path}")

        # Make download request
        response = requests.get(asset.url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()

        # Get file size
        total_size = int(response.headers.get('content-length', 0))

        # Download in chunks
        downloaded_size = 0
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)

        # Update asset metadata
        asset.local_path = file_path
        asset.file_size = downloaded_size
        asset.downloaded = True

        self.logger.info(f"Successfully downloaded: {asset.name} ({downloaded_size} bytes)")
        return True

    except Exception as e:
        self.logger.error(f"Failed to download {asset.name}: {e}")
        # Clean up partial download
        if file_path.exists():
            try:
                file_path.unlink()
            except:
                pass
        return False