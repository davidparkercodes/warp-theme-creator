"""Website content fetching module.

This module handles fetching and parsing content from websites,
including HTML, CSS, and images for color extraction.
"""

from typing import Dict, List, Optional, Tuple, Union
import requests
from requests.exceptions import RequestException
from urllib.parse import urljoin, urlparse


class Fetcher:
    """Handles fetching content from websites for color extraction."""

    def __init__(self, timeout: int = 10):
        """Initialize the fetcher with a default timeout.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WarpThemeCreator/0.1.0 (+https://github.com/davidparkercodes/warp-theme-creator)'
        })
    
    def validate_url(self, url: str) -> bool:
        """Validate if the URL is properly formatted.

        Args:
            url: The URL to validate

        Returns:
            True if the URL is valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def fetch_html(self, url: str) -> Tuple[Optional[str], Dict[str, str]]:
        """Fetch HTML content from the specified URL.

        Args:
            url: The URL to fetch HTML from

        Returns:
            A tuple of (HTML content, error dict) - if successful, error dict is empty
        """
        if not self.validate_url(url):
            return None, {'error': 'Invalid URL format'}
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text, {}
        except RequestException as e:
            return None, {'error': f'Failed to fetch {url}: {str(e)}'}
    
    def fetch_css(self, base_url: str, css_url: str) -> Tuple[Optional[str], Dict[str, str]]:
        """Fetch CSS content from the specified URL.

        Args:
            base_url: The base URL of the website
            css_url: The relative or absolute URL of the CSS file

        Returns:
            A tuple of (CSS content, error dict) - if successful, error dict is empty
        """
        full_url = urljoin(base_url, css_url)
        if not self.validate_url(full_url):
            return None, {'error': 'Invalid CSS URL format'}
        
        try:
            response = self.session.get(full_url, timeout=self.timeout)
            response.raise_for_status()
            return response.text, {}
        except RequestException as e:
            return None, {'error': f'Failed to fetch CSS {full_url}: {str(e)}'}
    
    def fetch_image(self, base_url: str, image_url: str) -> Tuple[Optional[bytes], Dict[str, str]]:
        """Fetch image content from the specified URL.

        Args:
            base_url: The base URL of the website
            image_url: The relative or absolute URL of the image

        Returns:
            A tuple of (image content in bytes, error dict) - if successful, error dict is empty
        """
        full_url = urljoin(base_url, image_url)
        if not self.validate_url(full_url):
            return None, {'error': 'Invalid image URL format'}
        
        try:
            response = self.session.get(full_url, timeout=self.timeout)
            response.raise_for_status()
            return response.content, {}
        except RequestException as e:
            return None, {'error': f'Failed to fetch image {full_url}: {str(e)}'}
