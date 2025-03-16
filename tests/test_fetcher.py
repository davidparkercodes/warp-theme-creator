"""Tests for the fetcher module."""

import unittest
from unittest import mock
from warp_theme_creator.fetcher import Fetcher


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
        mock_get.side_effect = Exception("Connection error")

        html, error = self.fetcher.fetch_html("https://example.com")
        
        # Verify the result
        self.assertIsNone(html)
        self.assertIn("error", error)
        self.assertIn("Connection error", error["error"])


if __name__ == "__main__":
    unittest.main()