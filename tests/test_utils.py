"""Tests for the utils module."""

import unittest
from warp_theme_creator.utils import (
    is_valid_hex_color,
    adjust_color_brightness,
    adjust_color_saturation,
    rgb_to_hsl,
    hsl_to_rgb
)


class TestUtils(unittest.TestCase):
    """Test the utility functions."""

    def test_is_valid_hex_color(self):
        """Test hex color validation."""
        valid_colors = [
            "#000000",
            "#FFFFFF",
            "#123456",
            "#ABC",
            "#abc",
            "#FFF",
        ]
        
        invalid_colors = [
            "",
            "000000",
            "FFFFFF",
            "#GHIJKL",
            "#1234",
            "#12345",
            "#1234567",
            "rgb(255, 255, 255)",
        ]
        
        for color in valid_colors:
            with self.subTest(color=color):
                self.assertTrue(is_valid_hex_color(color))
                
        for color in invalid_colors:
            with self.subTest(color=color):
                self.assertFalse(is_valid_hex_color(color))

    def test_adjust_color_brightness(self):
        """Test brightness adjustment."""
        # Test brightening
        self.assertEqual(adjust_color_brightness("#000000", 2.0), "#000000")  # Black stays black
        self.assertEqual(adjust_color_brightness("#808080", 1.5), "#c0c0c0")  # Gray gets lighter
        
        # Test darkening
        self.assertEqual(adjust_color_brightness("#FFFFFF", 0.5), "#7f7f7f")  # White gets darker
        self.assertEqual(adjust_color_brightness("#FF0000", 0.5), "#7f0000")  # Red gets darker
        
        # Test clamping (not exceeding 255)
        self.assertEqual(adjust_color_brightness("#FFFFFF", 1.5), "#ffffff")  # White stays white
        
        # Test with 3-digit hex
        self.assertEqual(adjust_color_brightness("#F00", 0.5), "#7f0000")  # Red gets darker

    def test_adjust_color_saturation(self):
        """Test saturation adjustment."""
        # Increase saturation
        self.assertEqual(adjust_color_saturation("#808080", 2.0), "#808080")  # Gray stays gray
        
        # Decrease saturation
        original = "#FF0000"  # Pure red
        desaturated = adjust_color_saturation(original, 0.5)
        # Convert back to HSL to check saturation was halved
        r, g, b = int(desaturated[1:3], 16), int(desaturated[3:5], 16), int(desaturated[5:7], 16)
        h, s, l = rgb_to_hsl(r, g, b)
        self.assertAlmostEqual(s, 0.5, places=1)
        
        # Test with 3-digit hex for fully desaturated color (gray with same luminance)
        desaturated = adjust_color_saturation("#F00", 0.0)
        # The value should be a gray color, exact value may vary by implementation
        r, g, b = int(desaturated[1:3], 16), int(desaturated[3:5], 16), int(desaturated[5:7], 16)
        h, s, l = rgb_to_hsl(r, g, b)
        self.assertAlmostEqual(s, 0.0, places=1)  # Should be fully desaturated
        self.assertAlmostEqual(l, 0.5, places=1)  # Should maintain luminance

    def test_rgb_to_hsl(self):
        """Test RGB to HSL conversion."""
        test_cases = [
            ((255, 0, 0), (0, 1.0, 0.5)),      # Red
            ((0, 255, 0), (120, 1.0, 0.5)),    # Green
            ((0, 0, 255), (240, 1.0, 0.5)),    # Blue
            ((255, 255, 255), (0, 0.0, 1.0)),  # White
            ((0, 0, 0), (0, 0.0, 0.0)),        # Black
            ((128, 128, 128), (0, 0.0, 0.5)),  # Gray
        ]
        
        for rgb, expected_hsl in test_cases:
            with self.subTest(rgb=rgb):
                h, s, l = rgb_to_hsl(*rgb)
                expected_h, expected_s, expected_l = expected_hsl
                
                # H is cyclic, so for gray/white/black it doesn't matter
                if s > 0:
                    self.assertEqual(h, expected_h)
                
                self.assertAlmostEqual(s, expected_s, places=1)
                self.assertAlmostEqual(l, expected_l, places=1)

    def test_hsl_to_rgb(self):
        """Test HSL to RGB conversion."""
        test_cases = [
            ((0, 1.0, 0.5), (255, 0, 0)),      # Red
            ((120, 1.0, 0.5), (0, 255, 0)),    # Green
            ((240, 1.0, 0.5), (0, 0, 255)),    # Blue
            ((0, 0.0, 1.0), (255, 255, 255)),  # White
            ((0, 0.0, 0.0), (0, 0, 0)),        # Black
            ((0, 0.0, 0.5), (128, 128, 128)),  # Gray
        ]
        
        for hsl, expected_rgb in test_cases:
            with self.subTest(hsl=hsl):
                rgb = hsl_to_rgb(*hsl)
                self.assertEqual(rgb, expected_rgb)

    def test_color_conversions_roundtrip(self):
        """Test roundtrip conversion (RGB -> HSL -> RGB)."""
        test_colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (0, 255, 255),  # Cyan
            (255, 0, 255),  # Magenta
            (255, 255, 255),# White
            (0, 0, 0),      # Black
            (128, 128, 128),# Gray
        ]
        
        for rgb in test_colors:
            with self.subTest(rgb=rgb):
                hsl = rgb_to_hsl(*rgb)
                rgb_back = hsl_to_rgb(*hsl)
                
                # Allow for small rounding differences
                self.assertAlmostEqual(rgb[0], rgb_back[0], delta=1)
                self.assertAlmostEqual(rgb[1], rgb_back[1], delta=1)
                self.assertAlmostEqual(rgb[2], rgb_back[2], delta=1)


if __name__ == "__main__":
    unittest.main()