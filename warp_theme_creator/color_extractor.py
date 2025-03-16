"""Color extraction module.

This module handles extracting colors from websites,
including both CSS and image colors.
"""

from typing import Dict, List, Optional, Tuple, Union
import re
from io import BytesIO
from colorthief import ColorThief
from PIL import Image


class ColorExtractor:
    """Extract colors from website content."""

    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color code to RGB tuple.

        Args:
            hex_color: Hex color code (with or without #)

        Returns:
            RGB tuple (r, g, b)
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color code.

        Args:
            rgb: RGB tuple (r, g, b)

        Returns:
            Hex color code (with #)
        """
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    
    def extract_css_colors(self, css_content: str) -> List[str]:
        """Extract colors from CSS content.

        Args:
            css_content: CSS content as string

        Returns:
            List of hex color codes
        """
        # Regular expressions for color formats
        hex_pattern = r'#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b'
        rgb_pattern = r'rgb\(\s*([0-9]+)\s*,\s*([0-9]+)\s*,\s*([0-9]+)\s*\)'
        
        # Extract hex colors
        hex_colors = re.findall(hex_pattern, css_content)
        colors = [f'#{c}' if len(c) > 0 else '#000000' for c in hex_colors]
        
        # Extract RGB colors
        rgb_colors = re.findall(rgb_pattern, css_content)
        for r, g, b in rgb_colors:
            try:
                rgb = (int(r), int(g), int(b))
                colors.append(self.rgb_to_hex(rgb))
            except ValueError:
                continue
        
        # Remove duplicates and return
        return list(set(colors))
    
    def extract_image_colors(self, image_data: bytes, color_count: int = 5) -> List[str]:
        """Extract dominant colors from an image.

        Args:
            image_data: Image content in bytes
            color_count: Number of colors to extract

        Returns:
            List of hex color codes
        """
        try:
            image_file = BytesIO(image_data)
            color_thief = ColorThief(image_file)
            palette = color_thief.get_palette(color_count=color_count)
            return [self.rgb_to_hex(color) for color in palette]
        except Exception as e:
            print(f"Error extracting colors from image: {e}")
            return []
    
    def select_accent_color(self, colors: List[str]) -> str:
        """Select the best accent color from a list of colors.

        Args:
            colors: List of hex color codes

        Returns:
            Selected accent color as hex
        """
        # TODO: Implement a better algorithm to select an appropriate accent color
        # For now, just return the first color or a default
        if colors:
            return colors[0]
        return "#0087D7"  # Default Warp blue
    
    def select_background_color(self, colors: List[str]) -> str:
        """Select the best background color from a list of colors.

        Args:
            colors: List of hex color codes

        Returns:
            Selected background color as hex
        """
        # TODO: Implement a better algorithm to choose background (likely dark or light)
        # For now, return a dark color or default
        dark_colors = [c for c in colors if self._is_dark_color(c)]
        if dark_colors:
            return dark_colors[0]
        return "#1E1E1E"  # Default dark background
    
    def select_foreground_color(self, background: str) -> str:
        """Select the best foreground color based on background.

        Args:
            background: Background color as hex

        Returns:
            Selected foreground color as hex
        """
        # Choose foreground based on background luminance
        if self._is_dark_color(background):
            return "#FFFFFF"  # White text on dark background
        return "#000000"  # Black text on light background
    
    def _is_dark_color(self, hex_color: str) -> bool:
        """Check if a color is dark based on luminance.

        Args:
            hex_color: Hex color code

        Returns:
            True if color is dark, False otherwise
        """
        r, g, b = self.hex_to_rgb(hex_color)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance < 0.5
    
    def generate_terminal_colors(self, accent: str, background: str) -> Dict[str, str]:
        """Generate a complete set of terminal colors.

        Args:
            accent: Accent color as hex
            background: Background color as hex

        Returns:
            Dictionary of terminal colors
        """
        # TODO: Implement a better algorithm to generate cohesive terminal colors
        # For now, return a simple set based on accent and background
        is_dark_bg = self._is_dark_color(background)
        
        # Basic color palette
        if is_dark_bg:
            black = "#000000"
            red = "#FF5555"
            green = "#50FA7B"
            yellow = "#F1FA8C"
            blue = accent
            magenta = "#FF79C6"
            cyan = "#8BE9FD"
            white = "#BFBFBF"
            bright_black = "#4D4D4D"
            bright_red = "#FF6E67"
            bright_green = "#5AF78E"
            bright_yellow = "#F4F99D"
            bright_blue = self._brighten_color(accent)
            bright_magenta = "#FF92D0"
            bright_cyan = "#9AEDFE"
            bright_white = "#FFFFFF"
        else:
            black = "#1E1E1E"
            red = "#E53935"
            green = "#43A047"
            yellow = "#FFB300"
            blue = accent
            magenta = "#D81B60"
            cyan = "#00ACC1"
            white = "#F5F5F5"
            bright_black = "#666666"
            bright_red = "#FF5252"
            bright_green = "#69F0AE"
            bright_yellow = "#FFD740"
            bright_blue = self._darken_color(accent)
            bright_magenta = "#FF4081"
            bright_cyan = "#64FFDA"
            bright_white = "#FFFFFF"
        
        return {
            "black": black,
            "red": red,
            "green": green,
            "yellow": yellow,
            "blue": blue,
            "magenta": magenta,
            "cyan": cyan,
            "white": white,
            "bright_black": bright_black,
            "bright_red": bright_red,
            "bright_green": bright_green,
            "bright_yellow": bright_yellow,
            "bright_blue": bright_blue,
            "bright_magenta": bright_magenta,
            "bright_cyan": bright_cyan,
            "bright_white": bright_white
        }
    
    def _brighten_color(self, hex_color: str, factor: float = 1.2) -> str:
        """Brighten a color by a factor.

        Args:
            hex_color: Hex color code
            factor: Brightening factor

        Returns:
            Brightened color as hex
        """
        r, g, b = self.hex_to_rgb(hex_color)
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return self.rgb_to_hex((r, g, b))
    
    def _darken_color(self, hex_color: str, factor: float = 0.8) -> str:
        """Darken a color by a factor.

        Args:
            hex_color: Hex color code
            factor: Darkening factor

        Returns:
            Darkened color as hex
        """
        r, g, b = self.hex_to_rgb(hex_color)
        r = max(0, int(r * factor))
        g = max(0, int(g * factor))
        b = max(0, int(b * factor))
        return self.rgb_to_hex((r, g, b))
