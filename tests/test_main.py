"""Tests for the main module."""

import os
import unittest
from unittest import mock
import tempfile
import sys
from warp_theme_creator.main import main, parse_args


class TestMain(unittest.TestCase):
    """Test the main functionality."""

    def test_parse_args(self):
        """Test command line argument parsing."""
        test_cases = [
            # Basic URL
            (
                ["https://example.com"],
                {
                    "url": "https://example.com",
                    "name": None,
                    "output": "./themes",
                    "extract_background": False,
                    "brightness": 1.0,
                    "saturation": 1.0,
                }
            ),
            # With theme name
            (
                ["https://example.com", "--name", "Example Theme"],
                {
                    "url": "https://example.com",
                    "name": "Example Theme",
                    "output": "./themes",
                    "extract_background": False,
                    "brightness": 1.0,
                    "saturation": 1.0,
                }
            ),
            # With output directory
            (
                ["https://example.com", "--output", "/tmp/themes"],
                {
                    "url": "https://example.com",
                    "name": None,
                    "output": "/tmp/themes",
                    "extract_background": False,
                    "brightness": 1.0,
                    "saturation": 1.0,
                }
            ),
            # With background extraction
            (
                ["https://example.com", "--extract-background"],
                {
                    "url": "https://example.com",
                    "name": None,
                    "output": "./themes",
                    "extract_background": True,
                    "brightness": 1.0,
                    "saturation": 1.0,
                }
            ),
            # With adjustment factors
            (
                ["https://example.com", "--brightness", "1.2", "--saturation", "0.8"],
                {
                    "url": "https://example.com",
                    "name": None,
                    "output": "./themes",
                    "extract_background": False,
                    "brightness": 1.2,
                    "saturation": 0.8,
                }
            ),
        ]
        
        for args, expected in test_cases:
            with self.subTest(args=args):
                parsed = parse_args(args)
                for key, value in expected.items():
                    self.assertEqual(getattr(parsed, key), value)

    @mock.patch('warp_theme_creator.main.Fetcher')
    @mock.patch('warp_theme_creator.main.ColorExtractor')
    @mock.patch('warp_theme_creator.main.ThemeGenerator')
    def test_main_success(self, mock_theme_generator, mock_color_extractor, mock_fetcher):
        """Test successful execution of main function."""
        # Setup mocks
        mock_fetcher_instance = mock.MagicMock()
        mock_color_extractor_instance = mock.MagicMock()
        mock_theme_generator_instance = mock.MagicMock()
        
        mock_fetcher.return_value = mock_fetcher_instance
        mock_color_extractor.return_value = mock_color_extractor_instance
        mock_theme_generator.return_value = mock_theme_generator_instance
        
        # Mock fetch_all_resources to return success
        mock_fetcher_instance.fetch_all_resources.return_value = {
            'html': "<html>Test</html>",
            'css_urls': [],
            'image_urls': [],
            'css_contents': {},
            'image_contents': {}
        }
        
        # Mock color extraction
        mock_color_extractor_instance.extract_css_colors.return_value = {}
        mock_color_extractor_instance.select_accent_color.return_value = "#0087D7"
        mock_color_extractor_instance.select_background_color.return_value = "#1E1E1E"
        mock_color_extractor_instance.select_foreground_color.return_value = "#FFFFFF"
        
        # Mock terminal colors generation
        mock_color_extractor_instance.generate_terminal_colors.return_value = {
            "black": "#000000",
            "bright_black": "#555555",
            "red": "#FF0000",
            "green": "#00FF00",
            "yellow": "#FFFF00",
            "blue": "#0000FF",
            "magenta": "#FF00FF",
            "cyan": "#00FFFF",
            "white": "#FFFFFF",
            "bright_red": "#FF5555",
            "bright_green": "#55FF55",
            "bright_yellow": "#FFFF55",
            "bright_blue": "#5555FF",
            "bright_magenta": "#FF55FF",
            "bright_cyan": "#55FFFF",
            "bright_white": "#FFFFFF"
        }
        
        # Mock theme creation and saving
        mock_theme_generator_instance.create_theme.return_value = {"name": "Test Theme"}
        mock_theme_generator_instance.save_theme.return_value = "/tmp/test_theme.yaml"
        
        # Create a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Run main with test arguments
            args = ["https://example.com", "--output", temp_dir]
            exit_code = main(args)
            
            # Verify success exit code
            self.assertEqual(exit_code, 0)
            
            # Verify methods were called
            mock_fetcher_instance.fetch_all_resources.assert_called_once()
            mock_color_extractor_instance.generate_terminal_colors.assert_called_once()
            mock_theme_generator_instance.create_theme.assert_called_once()
            mock_theme_generator_instance.save_theme.assert_called_once()

    @mock.patch('warp_theme_creator.main.Fetcher')
    def test_main_fetch_error(self, mock_fetcher):
        """Test main function handling fetch errors."""
        # Setup mocks
        mock_fetcher_instance = mock.MagicMock()
        mock_fetcher.return_value = mock_fetcher_instance
        
        # Mock fetch_all_resources to return error
        mock_fetcher_instance.fetch_all_resources.return_value = {
            'errors': {"error": "Connection error"}
        }
        
        # Capture stdout to verify error message
        with mock.patch('sys.stdout'):
            # Run main with test arguments
            args = ["https://example.com"]
            exit_code = main(args)
            
            # Verify error exit code
            self.assertEqual(exit_code, 1)
            
            # Verify method was called
            mock_fetcher_instance.fetch_all_resources.assert_called_once()


if __name__ == "__main__":
    unittest.main()