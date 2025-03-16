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
        
    def test_extract_css_urls(self):
        """Test extracting CSS URLs from HTML."""
        html = """
        <html>
            <head>
                <link rel="stylesheet" href="/styles/main.css">
                <link rel="stylesheet" href="https://cdn.example.com/style.css">
                <style>
                    @import "/styles/imported.css";
                    @import "https://cdn.example.com/imported.css";
                    body { color: black; }
                </style>
            </head>
            <body>
                <div style="@import '/styles/inline.css';">Test</div>
            </body>
        </html>
        """
        base_url = "https://example.com"
        css_urls = self.fetcher.extract_css_urls(html, base_url)
        
        # Expected URLs
        expected_urls = [
            "https://example.com/styles/main.css",
            "https://cdn.example.com/style.css",
            "https://example.com/styles/imported.css",
            "https://cdn.example.com/imported.css",
            "https://example.com/styles/inline.css"
        ]
        
        # We don't care about the order, just that all are found
        for url in expected_urls:
            self.assertIn(url, css_urls)
        
        # Check that we found the expected number of unique URLs
        self.assertEqual(len(css_urls), len(expected_urls))
        
    def test_extract_css_urls_empty_html(self):
        """Test extracting CSS URLs from empty HTML."""
        css_urls = self.fetcher.extract_css_urls("", "https://example.com")
        self.assertEqual(css_urls, [])
        
    def test_extract_image_urls(self):
        """Test extracting image URLs from HTML."""
        html = """
        <html>
            <body>
                <img src="/images/logo.png">
                <img src="https://cdn.example.com/hero.jpg">
                <div style="background-image: url('/images/bg.jpg');">Test</div>
                <div style="background-image: url(https://cdn.example.com/bg.png);">Test</div>
            </body>
        </html>
        """
        base_url = "https://example.com"
        image_urls = self.fetcher.extract_image_urls(html, base_url)
        
        # Expected URLs
        expected_urls = [
            "https://example.com/images/logo.png",
            "https://cdn.example.com/hero.jpg",
            "https://example.com/images/bg.jpg",
            "https://cdn.example.com/bg.png"
        ]
        
        # We don't care about the order, just that all are found
        for url in expected_urls:
            self.assertIn(url, image_urls)
        
        # Check that we found the expected number of unique URLs
        self.assertEqual(len(image_urls), len(expected_urls))
        
    def test_extract_image_urls_empty_html(self):
        """Test extracting image URLs from empty HTML."""
        image_urls = self.fetcher.extract_image_urls("", "https://example.com")
        self.assertEqual(image_urls, [])
        
    @mock.patch("warp_theme_creator.fetcher.Fetcher.fetch_html")
    @mock.patch("warp_theme_creator.fetcher.Fetcher.extract_css_urls")
    @mock.patch("warp_theme_creator.fetcher.Fetcher.extract_image_urls")
    def test_fetch_all_resources_success(self, mock_extract_image_urls, mock_extract_css_urls, mock_fetch_html):
        """Test successful fetching of all resources."""
        # Mock responses
        mock_fetch_html.return_value = ("<html></html>", {})
        mock_extract_css_urls.return_value = ["https://example.com/style1.css", "https://example.com/style2.css"]
        mock_extract_image_urls.return_value = ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]
        
        result = self.fetcher.fetch_all_resources("https://example.com")
        
        # Verify the result
        self.assertEqual(result["html"], "<html></html>")
        self.assertEqual(result["css_urls"], ["https://example.com/style1.css", "https://example.com/style2.css"])
        self.assertEqual(result["image_urls"], ["https://example.com/image1.jpg", "https://example.com/image2.jpg"])
        self.assertEqual(result["errors"], {})
        
        # Verify function calls
        mock_fetch_html.assert_called_once_with("https://example.com")
        mock_extract_css_urls.assert_called_once_with("<html></html>", "https://example.com")
        mock_extract_image_urls.assert_called_once_with("<html></html>", "https://example.com")
        
    @mock.patch("warp_theme_creator.fetcher.Fetcher.fetch_html")
    def test_fetch_all_resources_html_error(self, mock_fetch_html):
        """Test fetching all resources with HTML error."""
        # Mock error response
        mock_fetch_html.return_value = (None, {"error": "Connection error"})
        
        result = self.fetcher.fetch_all_resources("https://example.com")
        
        # Verify the result
        self.assertEqual(result["html"], "")
        self.assertEqual(result["css_urls"], [])
        self.assertEqual(result["image_urls"], [])
        self.assertEqual(result["errors"], {"html": "Connection error"})
        
    @mock.patch("warp_theme_creator.fetcher.Fetcher.fetch_html")
    @mock.patch("warp_theme_creator.fetcher.Fetcher.extract_css_urls")
    @mock.patch("warp_theme_creator.fetcher.Fetcher.extract_image_urls")
    def test_fetch_all_resources_max_limits(self, mock_extract_image_urls, mock_extract_css_urls, mock_fetch_html):
        """Test resource limits in fetch_all_resources."""
        # Mock responses with more items than limits
        mock_fetch_html.return_value = ("<html></html>", {})
        mock_extract_css_urls.return_value = [f"https://example.com/style{i}.css" for i in range(20)]
        mock_extract_image_urls.return_value = [f"https://example.com/image{i}.jpg" for i in range(30)]
        
        # Set limits lower than the number of items
        result = self.fetcher.fetch_all_resources("https://example.com", max_css=5, max_images=10)
        
        # Verify the result respects limits
        self.assertEqual(len(result["css_urls"]), 5)
        self.assertEqual(len(result["image_urls"]), 10)


if __name__ == "__main__":
    unittest.main()