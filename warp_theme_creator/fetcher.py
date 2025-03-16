"""Website content fetching module.

This module handles fetching and parsing content from websites,
including HTML, CSS, and images for color extraction.
"""

from typing import Dict, List, Optional, Set, Tuple, Union
import re
import requests
from requests.exceptions import RequestException
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


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
            # Check that scheme is http or https, and netloc is not empty
            return result.scheme in ('http', 'https') and bool(result.netloc)
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
    
    def extract_css_urls(self, html: str, base_url: str) -> List[str]:
        """Extract CSS URLs from HTML content.

        Args:
            html: The HTML content to extract CSS URLs from
            base_url: The base URL to resolve relative URLs

        Returns:
            A list of CSS URLs found in the HTML
        """
        if not html:
            return []
        
        css_urls = set()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find <link> tags with rel="stylesheet"
        for link in soup.find_all('link', rel="stylesheet"):
            href = link.get('href')
            if href:
                css_urls.add(href)
        
        # Find <style> tags with @import
        for style in soup.find_all('style'):
            # Find all @import statements
            imports = re.findall(r'@import\s+[\'"]([^\'"]+)[\'"]', style.text)
            css_urls.update(imports)
        
        # Find inline style with @import
        for style_attr in soup.find_all(style=True):
            imports = re.findall(r'@import\s+[\'"]([^\'"]+)[\'"]', style_attr['style'])
            css_urls.update(imports)
        
        # Make all URLs absolute
        return [urljoin(base_url, url) for url in css_urls]
    
    def extract_image_urls(self, html: str, base_url: str) -> List[str]:
        """Extract image URLs from HTML content.

        Args:
            html: The HTML content to extract image URLs from
            base_url: The base URL to resolve relative URLs

        Returns:
            A list of image URLs found in the HTML
        """
        if not html:
            return []
        
        image_urls = set()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find <img> tags
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                image_urls.add(src)
        
        # Find <div> and other elements with background-image in style
        for elem in soup.find_all(style=True):
            bg_images = re.findall(r'background-image\s*:\s*url\([\'"]?([^\'")\s]+)[\'"]?\)', elem['style'])
            image_urls.update(bg_images)
        
        # Make all URLs absolute
        return [urljoin(base_url, url) for url in image_urls]
    
    def fetch_all_resources(self, url: str, max_css: int = 10, max_images: int = 20) -> Dict[str, Union[str, List[str], Dict[str, str]]]:
        """Fetch HTML, CSS, and image URLs from a website.

        Args:
            url: The URL of the website to fetch resources from
            max_css: Maximum number of CSS files to fetch
            max_images: Maximum number of images to fetch

        Returns:
            A dictionary containing:
            - 'html': The HTML content (str)
            - 'css_urls': List of CSS URLs found in the HTML
            - 'image_urls': List of image URLs found in the HTML
            - 'errors': Dict of any errors encountered
        """
        # Initialize return data
        result = {
            'html': '',
            'css_urls': [],
            'image_urls': [],
            'errors': {}
        }
        
        # Fetch HTML
        html, error = self.fetch_html(url)
        if error:
            result['errors']['html'] = error['error']
            return result
            
        result['html'] = html
        
        # Extract CSS URLs
        css_urls = self.extract_css_urls(html, url)
        result['css_urls'] = css_urls[:max_css]  # Limit number of CSS files
        
        # Extract image URLs
        image_urls = self.extract_image_urls(html, url)
        result['image_urls'] = image_urls[:max_images]  # Limit number of images
        
        return result
