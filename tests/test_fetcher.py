"""Tests for the fetcher module."""

import unittest
from unittest import mock
from warp_theme_creator.fetcher import Fetcher
from requests.exceptions import RequestException


class TestFetcher(unittest.TestCase):
    """Test the Fetcher class."""

    def setUp(self):
        """Set up test fixtures."""
        self.fetcher = Fetcher()

    def test_validate_url_valid(self):
        """Test URL validation with valid URLs."""
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://www.example.com/path/to/page",
            "http://sub.domain.example.com",
        ]
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(self.fetcher.validate_url(url))

    def test_validate_url_invalid(self):
        """Test URL validation with invalid URLs."""
        invalid_urls = [
            "",
            "example.com",
            "www.example.com",
            "ftp://example.com",
            "http://",
            "https://",
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(self.fetcher.validate_url(url))

    @mock.patch("requests.Session.get")
    def test_fetch_html_success(self, mock_get):
        """Test successful HTML fetching."""
        # Mock successful response
        mock_response = mock.Mock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        html, error = self.fetcher.fetch_html("https://example.com")
        
        # Verify the result
        self.assertEqual(html, "<html><body>Test</body></html>")
        self.assertEqual(error, {})
        mock_get.assert_called_once_with("https://example.com", timeout=10)

    @mock.patch("requests.Session.get")
    def test_fetch_html_error(self, mock_get):
        """Test HTML fetching with error."""
        # Mock error response
        mock_get.side_effect = RequestException("Connection error")

        html, error = self.fetcher.fetch_html("https://example.com")
        
        # Verify the result
        self.assertIsNone(html)
        self.assertIn("error", error)
        self.assertIn("Connection error", error["error"])
        
    def test_fetch_html_invalid_url(self):
        """Test HTML fetching with invalid URL."""
        html, error = self.fetcher.fetch_html("invalid_url")
        
        # Verify the result
        self.assertIsNone(html)
        self.assertIn("error", error)
        self.assertEqual(error["error"], "Invalid URL format")
        
    @mock.patch("requests.Session.get")
    def test_fetch_css_success(self, mock_get):
        """Test successful CSS fetching."""
        # Mock successful response
        mock_response = mock.Mock()
        mock_response.text = "body { color: #fff; }"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        base_url = "https://example.com"
        css_url = "/style.css"
        css, error = self.fetcher.fetch_css(base_url, css_url)
        
        # Verify the result
        self.assertEqual(css, "body { color: #fff; }")
        self.assertEqual(error, {})
        mock_get.assert_called_once_with("https://example.com/style.css", timeout=10)
        
    @mock.patch("requests.Session.get")
    def test_fetch_css_absolute_url(self, mock_get):
        """Test CSS fetching with absolute URL."""
        # Mock successful response
        mock_response = mock.Mock()
        mock_response.text = "body { color: #fff; }"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        base_url = "https://example.com"
        css_url = "https://cdn.example.com/style.css"
        css, error = self.fetcher.fetch_css(base_url, css_url)
        
        # Verify the result
        self.assertEqual(css, "body { color: #fff; }")
        self.assertEqual(error, {})
        mock_get.assert_called_once_with("https://cdn.example.com/style.css", timeout=10)
        
    def test_fetch_css_invalid_url(self):
        """Test CSS fetching with invalid URL."""
        base_url = "https://example.com"
        css_url = "javascript:alert(1)"  # Invalid URL
        
        css, error = self.fetcher.fetch_css(base_url, css_url)
        
        # Verify the result
        self.assertIsNone(css)
        self.assertIn("error", error)
        self.assertEqual(error["error"], "Invalid CSS URL format")
        
    @mock.patch("requests.Session.get")
    def test_fetch_css_error(self, mock_get):
        """Test CSS fetching with error."""
        # Mock error response
        mock_get.side_effect = RequestException("Connection error")

        base_url = "https://example.com"
        css_url = "/style.css"
        css, error = self.fetcher.fetch_css(base_url, css_url)
        
        # Verify the result
        self.assertIsNone(css)
        self.assertIn("error", error)
        self.assertIn("Connection error", error["error"])
        
    @mock.patch("requests.Session.get")
    def test_fetch_image_success(self, mock_get):
        """Test successful image fetching."""
        # Mock successful response
        mock_response = mock.Mock()
        mock_response.content = b"image data"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        base_url = "https://example.com"
        image_url = "/image.jpg"
        image, error = self.fetcher.fetch_image(base_url, image_url)
        
        # Verify the result
        self.assertEqual(image, b"image data")
        self.assertEqual(error, {})
        mock_get.assert_called_once_with("https://example.com/image.jpg", timeout=10)
        
    @mock.patch("requests.Session.get")
    def test_fetch_image_absolute_url(self, mock_get):
        """Test image fetching with absolute URL."""
        # Mock successful response
        mock_response = mock.Mock()
        mock_response.content = b"image data"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        base_url = "https://example.com"
        image_url = "https://cdn.example.com/image.jpg"
        image, error = self.fetcher.fetch_image(base_url, image_url)
        
        # Verify the result
        self.assertEqual(image, b"image data")
        self.assertEqual(error, {})
        mock_get.assert_called_once_with("https://cdn.example.com/image.jpg", timeout=10)
        
    def test_fetch_image_invalid_url(self):
        """Test image fetching with invalid URL."""
        base_url = "https://example.com"
        image_url = "javascript:alert(1)"  # Invalid URL
        
        image, error = self.fetcher.fetch_image(base_url, image_url)
        
        # Verify the result
        self.assertIsNone(image)
        self.assertIn("error", error)
        self.assertEqual(error["error"], "Invalid image URL format")
        
    @mock.patch("requests.Session.get")
    def test_fetch_image_error(self, mock_get):
        """Test image fetching with error."""
        # Mock error response
        mock_get.side_effect = RequestException("Connection error")

        base_url = "https://example.com"
        image_url = "/image.jpg"
        image, error = self.fetcher.fetch_image(base_url, image_url)
        
        # Verify the result
        self.assertIsNone(image)
        self.assertIn("error", error)
        self.assertIn("Connection error", error["error"])


if __name__ == "__main__":
    unittest.main()