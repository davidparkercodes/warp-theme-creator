"""Tests for the screenshots module."""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import io
from PIL import Image
import numpy as np

from warp_theme_creator.screenshots import ScreenshotExtractor


class TestScreenshotExtractor(unittest.TestCase):
    """Test the ScreenshotExtractor class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.extractor = ScreenshotExtractor(screenshots_dir=self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
        
    def test_rgb_to_hex(self):
        """Test RGB to hex conversion."""
        self.assertEqual(self.extractor.rgb_to_hex((255, 0, 0)), "#FF0000")
        self.assertEqual(self.extractor.rgb_to_hex((0, 255, 0)), "#00FF00")
        self.assertEqual(self.extractor.rgb_to_hex((0, 0, 255)), "#0000FF")
        self.assertEqual(self.extractor.rgb_to_hex((51, 51, 51)), "#333333")
        
    def test_get_color_brightness(self):
        """Test color brightness calculation."""
        # Dark colors
        self.assertLess(self.extractor.get_color_brightness("#000000"), 128)
        self.assertLess(self.extractor.get_color_brightness("#333333"), 128)
        # Light colors
        self.assertGreater(self.extractor.get_color_brightness("#FFFFFF"), 128)
        self.assertGreater(self.extractor.get_color_brightness("#EEEEEE"), 128)
        
    def test_is_light_color(self):
        """Test light color detection."""
        # Dark colors
        self.assertFalse(self.extractor.is_light_color("#000000"))
        self.assertFalse(self.extractor.is_light_color("#333333"))
        # Light colors
        self.assertTrue(self.extractor.is_light_color("#FFFFFF"))
        self.assertTrue(self.extractor.is_light_color("#EEEEEE"))
        
    def test_get_color_distance(self):
        """Test color distance calculation."""
        # Same colors should have zero distance
        self.assertEqual(self.extractor.get_color_distance((0, 0, 0), (0, 0, 0)), 0)
        self.assertEqual(self.extractor.get_color_distance((255, 255, 255), (255, 255, 255)), 0)
        
        # Check some known distances
        self.assertAlmostEqual(
            self.extractor.get_color_distance((255, 0, 0), (0, 0, 0)), 
            255
        )
        self.assertAlmostEqual(
            self.extractor.get_color_distance((255, 255, 255), (0, 0, 0)), 
            np.sqrt(255**2 * 3), 
            places=1
        )
        
    @patch('warp_theme_creator.screenshots.ScreenshotExtractor.setup_driver')
    def test_take_screenshot(self, mock_setup_driver):
        """Test the screenshot taking functionality."""
        # Mock a webdriver
        mock_driver = MagicMock()
        mock_setup_driver.return_value = mock_driver
        
        # Create a small red test image
        test_img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        img_bytes = io.BytesIO()
        test_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Mock driver screenshot return value
        mock_driver.get_screenshot_as_png.return_value = img_bytes.getvalue()
        
        # Test the function
        result_img = self.extractor.take_screenshot("https://example.com", save=False)
        
        # Verify the result
        self.assertIsInstance(result_img, Image.Image)
        mock_driver.get.assert_called_once_with("https://example.com")
        mock_driver.quit.assert_called_once()
        
    def test_extract_colors_from_image(self):
        """Test extracting colors from an image."""
        # Create a test image with red and blue halves
        width, height = 100, 50
        img = Image.new('RGB', (width, height))
        pixels = img.load()
        
        # Fill left half with red, right half with blue
        for y in range(height):
            for x in range(width):
                if x < width // 2:
                    pixels[x, y] = (255, 0, 0)  # Red
                else:
                    pixels[x, y] = (0, 0, 255)  # Blue
                    
        # Extract colors
        colors = self.extractor.extract_colors_from_image(img, n_colors=2)
        
        # Should get 2 colors with roughly equal percentages
        self.assertEqual(len(colors), 2)
        
        # Colors should be red and blue (in either order)
        hex_colors = [color[0] for color in colors]
        self.assertTrue("#FF0000" in hex_colors or "#FF0000".lower() in hex_colors)
        self.assertTrue("#0000FF" in hex_colors or "#0000FF".lower() in hex_colors)
        
        # Percentages should be close to 50%
        for _, percentage in colors:
            self.assertAlmostEqual(percentage, 0.5, delta=0.1)
            
    def test_is_background_color(self):
        """Test background color detection."""
        # Create a test image with blue edge and red center
        width, height = 100, 100
        img = Image.new('RGB', (width, height), color=(0, 0, 255))  # Blue
        
        # Draw a red rectangle in the center
        center_width, center_height = 60, 60
        x_offset = (width - center_width) // 2
        y_offset = (height - center_height) // 2
        
        for y in range(y_offset, y_offset + center_height):
            for x in range(x_offset, x_offset + center_width):
                img.putpixel((x, y), (255, 0, 0))  # Red
                
        # Blue should be detected as background
        self.assertTrue(self.extractor.is_background_color("#0000FF", img))
        
        # Red should not be detected as background
        self.assertFalse(self.extractor.is_background_color("#FF0000", img))
        
    @patch('warp_theme_creator.screenshots.ScreenshotExtractor.take_screenshot')
    @patch('warp_theme_creator.screenshots.ScreenshotExtractor.extract_colors_from_image')
    def test_extract_theme_colors(self, mock_extract_colors, mock_take_screenshot):
        """Test theme color extraction end-to-end."""
        # Create a test image
        test_img = Image.new('RGB', (100, 100), color=(255, 255, 255))  # White image
        mock_take_screenshot.return_value = test_img
        
        # Mock extracted colors
        mock_dominant_colors = [
            ("#FFFFFF", 0.8),  # White (background)
            ("#FF0000", 0.1),  # Red (accent)
            ("#000000", 0.1)   # Black (text)
        ]
        mock_extract_colors.return_value = mock_dominant_colors
        
        # Expected output with white background
        theme_colors = self.extractor.extract_theme_colors(
            "https://example.com", 
            prefer_light=True
        )
        
        # Check the results
        self.assertIn('background', theme_colors)
        self.assertIn('foreground', theme_colors)
        self.assertIn('accent', theme_colors)
        
        # With prefer_light=True, we expect white background
        self.assertEqual(theme_colors['background'], "#FFFFFF")
        # Foreground should be dark on light background
        self.assertEqual(theme_colors['foreground'], "#1E1E1E")
        
        # Now test with dark preference
        mock_extract_colors.reset_mock()
        mock_extract_colors.return_value = mock_dominant_colors
        
        # Add a dark color
        mock_dominant_colors.append(("#333333", 0.2))  # Dark gray
        
        theme_colors = self.extractor.extract_theme_colors(
            "https://example.com", 
            prefer_light=False
        )
        
        # With prefer_light=False, we expect dark background
        self.assertEqual(theme_colors['background'], "#333333")
        # Foreground should be light on dark background
        self.assertEqual(theme_colors['foreground'], "#FFFFFF")


if __name__ == '__main__':
    unittest.main()