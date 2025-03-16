"""Tests for the preview module."""

import os
import tempfile
import unittest
from unittest.mock import patch, mock_open

import yaml

from warp_theme_creator.preview import ThemePreviewGenerator


class TestThemePreviewGenerator(unittest.TestCase):
    """Test the ThemePreviewGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.preview_generator = ThemePreviewGenerator()
        self.temp_dir = tempfile.mkdtemp()
        
        # Sample theme data for testing
        self.sample_theme = {
            "name": "Test Theme",
            "accent": "#FF0000",
            "background": "#000000",
            "foreground": "#FFFFFF",
            "terminal_colors": {
                "normal": {
                    "black": "#000000",
                    "red": "#FF0000",
                    "green": "#00FF00",
                    "yellow": "#FFFF00",
                    "blue": "#0000FF",
                    "magenta": "#FF00FF",
                    "cyan": "#00FFFF",
                    "white": "#FFFFFF"
                },
                "bright": {
                    "black": "#808080",
                    "red": "#FF8080",
                    "green": "#80FF80",
                    "yellow": "#FFFF80",
                    "blue": "#8080FF",
                    "magenta": "#FF80FF",
                    "cyan": "#80FFFF",
                    "white": "#FFFFFF"
                }
            }
        }

    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary directory
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def test_generate_color_dict(self):
        """Test that color dictionary is correctly generated from theme."""
        color_dict = self.preview_generator.generate_color_dict(self.sample_theme)
        
        # Check basic theme colors
        self.assertEqual(color_dict["accent"], "#FF0000")
        self.assertEqual(color_dict["background"], "#000000")
        self.assertEqual(color_dict["foreground"], "#FFFFFF")
        
        # Check terminal colors
        self.assertEqual(color_dict["red"], "#FF0000")
        self.assertEqual(color_dict["green"], "#00FF00")
        self.assertEqual(color_dict["blue"], "#0000FF")
        
        # Check bright colors have "br" prefix
        self.assertEqual(color_dict["brred"], "#FF8080")
        self.assertEqual(color_dict["brgreen"], "#80FF80")
        self.assertEqual(color_dict["brblue"], "#8080FF")

    def test_generate_svg(self):
        """Test that SVG is correctly generated with theme colors."""
        svg_content = self.preview_generator.generate_svg(self.sample_theme)
        
        # Check for replaced color values in SVG
        self.assertIn('fill="#000000"', svg_content)  # background
        self.assertIn('fill="#FFFFFF"', svg_content)  # foreground
        self.assertIn('stroke="#FF0000"', svg_content)  # accent
        
        # Check for terminal colors
        self.assertIn('fill="#00FF00"', svg_content)  # green
        self.assertIn('fill="#0000FF"', svg_content)  # blue
        
        # Check for bright colors
        self.assertIn('fill="#80FF80"', svg_content)  # bright green
        self.assertIn('fill="#8080FF"', svg_content)  # bright blue

    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_preview(self, mock_file, mock_makedirs):
        """Test that preview is saved correctly."""
        output_path = self.preview_generator.save_preview(self.sample_theme, "/fake/path")
        
        # Check that directories are created
        mock_makedirs.assert_called_with("/fake/path/previews", exist_ok=True)
        
        # Check that the file is opened for writing
        mock_file.assert_called_with("/fake/path/previews/testtheme_preview.svg", "w")
        
        # Check SVG content is written
        file_handle = mock_file()
        self.assertTrue(file_handle.write.called)
        
        # Check that the returned path is correct
        self.assertEqual(output_path, "/fake/path/previews/testtheme_preview.svg")

    @patch("os.path.isfile", return_value=True)
    @patch("os.listdir", return_value=["theme1.yaml", "theme2.yml", "not_a_theme.txt"])
    @patch("builtins.open", new_callable=mock_open, read_data=yaml.dump({
        "name": "Theme1",
        "accent": "#FF0000",
        "background": "#000000",
        "foreground": "#FFFFFF",
        "terminal_colors": {
            "normal": {"black": "#000000", "red": "#FF0000", "green": "#00FF00", "yellow": "#FFFF00",
                       "blue": "#0000FF", "magenta": "#FF00FF", "cyan": "#00FFFF", "white": "#FFFFFF"},
            "bright": {"black": "#808080", "red": "#FF8080", "green": "#80FF80", "yellow": "#FFFF80",
                      "blue": "#8080FF", "magenta": "#FF80FF", "cyan": "#80FFFF", "white": "#FFFFFF"}
        }
    }))
    @patch("warp_theme_creator.preview.ThemePreviewGenerator.save_preview")
    def test_generate_previews_for_directory(self, mock_save_preview, mock_open_file, mock_listdir, mock_isfile):
        """Test generating previews for all themes in a directory."""
        # Set up mock to return different paths for different themes
        mock_save_preview.side_effect = [
            "/fake/path/previews/theme1_preview.svg",
            "/fake/path/previews/theme2_preview.svg"
        ]
        
        # Generate previews
        preview_paths = self.preview_generator.generate_previews_for_directory("/fake/path")
        
        # Check that save_preview was called twice (once for each theme)
        self.assertEqual(mock_save_preview.call_count, 2)
        
        # Check that the function returns the correct paths
        self.assertEqual(len(preview_paths), 2)
        self.assertEqual(preview_paths[0], "/fake/path/previews/theme1_preview.svg")
        self.assertEqual(preview_paths[1], "/fake/path/previews/theme2_preview.svg")


if __name__ == "__main__":
    unittest.main()