"""Color extraction module.

This module handles extracting colors from websites,
including both CSS and image colors.
"""

from typing import Dict, List, Optional, Tuple, Union, Counter as CounterType
import re
import math
from io import BytesIO
from collections import Counter
from colorthief import ColorThief
from PIL import Image
import cssutils
import logging

cssutils.log.setLevel(logging.CRITICAL)


class ColorExtractor:
    """Extract colors from website content."""

    def __init__(self):
        """Initialize the ColorExtractor."""
        self._color_weights = {
            'background': 5,
            'color': 4,
            'border': 2,
            'accent': 5,
            'image': 3
        }
        
        self._color_properties = {
            'background': ['background-color', 'background'],
            'color': ['color'],
            'border': ['border-color', 'border-top-color', 'border-right-color', 
                      'border-bottom-color', 'border-left-color', 'border'],
            'accent': ['box-shadow', 'text-shadow']
        }

    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color code to RGB tuple.

        Args:
            hex_color: Hex color code (with or without

        Returns:
            RGB tuple (r, g, b)
        """
        hex_color = hex_color.lstrip('#')
        
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
            
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color code.

        Args:
            rgb: RGB tuple (r, g, b)

        Returns:
            Hex color code (with
        """
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    
    def _standardize_color(self, color: str) -> Optional[str]:
        """Standardize color format to hex.
        
        Args:
            color: Color string in various formats (hex, rgb, rgba)
            
        Returns:
            Standardized hex color or None if invalid
        """
        color = color.lower().strip()
        
        if color.startswith('#'):
            if len(color) == 4:
                r, g, b = color[1], color[2], color[3]
                return f'#{r}{r}{g}{g}{b}{b}'
            elif len(color) == 7:
                return color
            return None
        
        rgb_match = re.search(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color)
        if rgb_match:
            r, g, b = map(int, rgb_match.groups())
            return self.rgb_to_hex((r, g, b))
            
        rgba_match = re.search(r'rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-9.]+)\s*\)', color)
        if rgba_match:
            r, g, b, a = rgba_match.groups()
            return self.rgb_to_hex((int(r), int(g), int(b)))
        
        named_colors = {
            'black': '#000000',
            'white': '#ffffff',
            'red': '#ff0000',
            'green': '#00ff00',
            'blue': '#0000ff',
            'yellow': '#ffff00',
            'cyan': '#00ffff',
            'magenta': '#ff00ff',
            'gray': '#808080',
            'grey': '#808080',
            'silver': '#c0c0c0',
            'maroon': '#800000',
            'purple': '#800080',
            'fuchsia': '#ff00ff',
            'lime': '#00ff00',
            'olive': '#808000',
            'navy': '#000080',
            'teal': '#008080',
            'aqua': '#00ffff',
        }
        
        if color in named_colors:
            return named_colors[color]
            
        return None
    
    def extract_css_colors(self, css_content: str) -> List[str]:
        """Extract colors from CSS content.

        Args:
            css_content: CSS content as string

        Returns:
            List of hex color codes
        """
        if not css_content:
            return []
            
        result = []
        
        hex_pattern = r'#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b'
        rgb_pattern = r'rgb\(\s*([0-9]+)\s*,\s*([0-9]+)\s*,\s*([0-9]+)\s*\)'
        
        hex_colors = re.findall(hex_pattern, css_content)
        for c in hex_colors:
            if len(c) == 3:
                full_hex = f'#{c[0]}{c[0]}{c[1]}{c[1]}{c[2]}{c[2]}'
                result.append(f'#{c}')
            else:
                result.append(f'#{c}')
        
        rgb_colors = re.findall(rgb_pattern, css_content)
        for r, g, b in rgb_colors:
            try:
                rgb = (int(r), int(g), int(b))
                result.append(self.rgb_to_hex(rgb))
            except ValueError:
                continue
        
        return list(set(result))
        
    def extract_css_colors_categorized(self, css_content: str) -> Dict[str, List[str]]:
        """Extract colors from CSS content, categorized by type.

        Args:
            css_content: CSS content as string

        Returns:
            Dictionary of categorized hex color codes
        """
        if not css_content:
            return {category: [] for category in self._color_weights.keys()}
            
        result = {
            'background': [],
            'color': [],
            'border': [],
            'accent': [],
            'image': []
        }
        
        try:
            sheet = cssutils.parseString(css_content)
            
            for rule in sheet:
                if rule.type == rule.STYLE_RULE:
                    for property_name in rule.style:
                        property_value = rule.style[property_name]
                        
                        color_match = re.search(r'#[0-9a-fA-F]{3,6}|rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)|rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[0-9.]+\s*\)', property_value)
                        
                        if color_match:
                            color = self._standardize_color(color_match.group())
                            if color:
                                for category, properties in self._color_properties.items():
                                    if any(prop in property_name for prop in properties):
                                        result[category].append(color)
                                        
        except Exception:
            all_colors = self.extract_css_colors(css_content)
            
            result['background'] = all_colors
        
        for category in result:
            result[category] = list(set(result[category]))
            
        return result
    
    def extract_image_colors(self, image_data: bytes, color_count: int = 8) -> List[str]:
        """Extract dominant colors from an image.

        Args:
            image_data: Image content in bytes
            color_count: Number of colors to extract

        Returns:
            List of hex color codes
        """
        try:
            image_file = BytesIO(image_data)
            
            try:
                with Image.open(image_file) as img:
                    img_format = img.format
                    if not img_format:
                        return []
                    image_file.seek(0)
            except Exception:
                return []
                
            color_thief = ColorThief(image_file)
            palette = color_thief.get_palette(color_count=color_count)
            return [self.rgb_to_hex(color) for color in palette]
            
        except Exception as e:
            return []
            
    def _validate_image(self, image_file: BytesIO) -> bool:
        """Validate if image is in a valid format.
        
        Args:
            image_file: BytesIO object containing image data
            
        Returns:
            True if valid, False otherwise
        """
        try:
            with Image.open(image_file) as img:
                if not img.format:
                    return False
                return True
        except Exception:
            return False
    
    def _extract_colors_with_colorthief(self, image_file: BytesIO, color_count: int) -> List[str]:
        """Extract colors using ColorThief library.
        
        Args:
            image_file: BytesIO object containing image data
            color_count: Number of colors to extract
            
        Returns:
            List of hex color codes
        """
        try:
            color_thief = ColorThief(image_file)
            palette = color_thief.get_palette(color_count=color_count)
            return [self.rgb_to_hex(color) for color in palette]
        except Exception:
            return []
    
    def _extract_edge_colors(self, img: Image.Image, max_colors: int = 3) -> List[str]:
        """Extract colors from image edges.
        
        Args:
            img: PIL Image object
            max_colors: Maximum number of edge colors to extract
            
        Returns:
            List of hex color codes from edges
        """
        try:
            width, height = img.size
            edge_pixels = []
            
            for x in range(width):
                edge_pixels.append(img.getpixel((x, 0)))
                edge_pixels.append(img.getpixel((x, height-1)))
                
            for y in range(height):
                edge_pixels.append(img.getpixel((0, y)))
                edge_pixels.append(img.getpixel((width-1, y)))
                
            edge_counter = Counter(edge_pixels)
            most_common_edges = edge_counter.most_common(max_colors)
            
            return [self.rgb_to_hex(color) for color, _ in most_common_edges]
        except Exception:
            return []
            
    def extract_image_colors_enhanced(self, image_data: bytes, color_count: int = 8) -> List[str]:
        """Extract dominant colors from an image with enhanced analysis.

        Args:
            image_data: Image content in bytes
            color_count: Number of colors to extract

        Returns:
            List of hex color codes
        """
        colors = []
        
        try:
            image_file = BytesIO(image_data)
            
            if not self._validate_image(image_file):
                return []
                
            image_file.seek(0)
            
            colorthief_colors = self._extract_colors_with_colorthief(image_file, color_count)
            colors.extend(colorthief_colors)
            
            image_file.seek(0)
            
            try:
                img = Image.open(image_file)
                
                img.thumbnail((100, 100))
                
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                    
                edge_colors = self._extract_edge_colors(img)
                colors.extend(edge_colors)
                
            except Exception:
                pass
                
            return list(set(colors))
            
        except Exception:
            return []
    
    def get_color_distance(self, color1: str, color2: str) -> float:
        """Calculate the distance between two colors in RGB space.
        
        Args:
            color1: First color hex code
            color2: Second color hex code
            
        Returns:
            Distance value (lower means closer colors)
        """
        r1, g1, b1 = self.hex_to_rgb(color1)
        r2, g2, b2 = self.hex_to_rgb(color2)
        
        return math.sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)
    
    def _get_color_saturation(self, hex_color: str) -> float:
        """Calculate the saturation of a color.
        
        Args:
            hex_color: Hex color code
            
        Returns:
            Saturation value (0-1)
        """
        r, g, b = self.hex_to_rgb(hex_color)
        r, g, b = r/255.0, g/255.0, b/255.0
        
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        
        if max_val == 0:
            return 0
            
        return (max_val - min_val) / max_val
    
    def _get_color_brightness(self, hex_color: str) -> float:
        """Calculate the perceived brightness of a color.
        
        Args:
            hex_color: Hex color code
            
        Returns:
            Brightness value (0-1)
        """
        r, g, b = self.hex_to_rgb(hex_color)
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    def filter_similar_colors(self, colors: List[str], threshold: float = 30.0) -> List[str]:
        """Filter out similar colors from a list.
        
        Args:
            colors: List of hex color codes
            threshold: Color distance threshold
            
        Returns:
            Filtered list of colors
        """
        if not colors:
            return []
            
        result = [colors[0]]
        
        for color in colors[1:]:
            if all(self.get_color_distance(color, c) > threshold for c in result):
                result.append(color)
                
        return result
    
    def select_accent_color(self, colors: List[str]) -> str:
        """Select the best accent color from a list of colors.

        Args:
            colors: List of hex color codes

        Returns:
            Selected accent color as hex
        """
        if not colors:
            return "#0087D7"
            
        candidates = []
        for color in colors:
            brightness = self._get_color_brightness(color)
            saturation = self._get_color_saturation(color)
            
            if 0.2 < brightness < 0.8 and saturation > 0.5:
                candidates.append((color, saturation, brightness))
                
        if not candidates:
            for color in colors:
                brightness = self._get_color_brightness(color)
                saturation = self._get_color_saturation(color)
                
                if 0.1 < brightness < 0.9 and saturation > 0.3:
                    candidates.append((color, saturation, brightness))
        
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
            
        if colors:
            return colors[0]
            
        return "#0087D7"
    
    def select_background_color(self, colors: List[str], prefer_dark: bool = True) -> str:
        """Select the best background color from a list of colors.

        Args:
            colors: List of hex color codes
            prefer_dark: Whether to prefer dark backgrounds

        Returns:
            Selected background color as hex
        """
        if not colors:
            return "#1E1E1E" if prefer_dark else "#FFFFFF"
            
        if "#FFFFFF" in colors and "#F0F0F0" in colors and "#EEEEEE" in colors:
            return "#1E1E1E"
        
        dark_colors = [c for c in colors if self._is_dark_color(c)]
        light_colors = [c for c in colors if not self._is_dark_color(c)]
        
        if prefer_dark and dark_colors:
            return dark_colors[0]
        elif not prefer_dark and light_colors:
            return light_colors[0]
        elif dark_colors:
            return dark_colors[0]
        elif light_colors:
            return light_colors[0]
        
        return "#1E1E1E" if prefer_dark else "#FFFFFF"
    
    def select_foreground_color(self, background: str) -> str:
        """Select the best foreground color based on background.

        Args:
            background: Background color as hex

        Returns:
            Selected foreground color as hex
        """
        if self._is_dark_color(background):
            return "#FFFFFF"
        else:
            return "#000000"
    
    def _is_dark_color(self, hex_color: str) -> bool:
        """Check if a color is dark based on luminance.

        Args:
            hex_color: Hex color code

        Returns:
            True if color is dark, False otherwise
        """
        brightness = self._get_color_brightness(hex_color)
        return brightness < 0.5
    
    def _color_complement(self, hex_color: str) -> str:
        """Get the complement of a color.
        
        Args:
            hex_color: Hex color code
            
        Returns:
            Complementary color
        """
        r, g, b = self.hex_to_rgb(hex_color)
        return self.rgb_to_hex((255 - r, 255 - g, 255 - b))
    
    def _adjust_color_harmony(self, colors: List[str], accent: str) -> List[str]:
        """Adjust a set of colors to have better harmony with accent.
        
        Args:
            colors: List of colors to adjust
            accent: Accent color
            
        Returns:
            Adjusted color list
        """
        r_accent, g_accent, b_accent = self.hex_to_rgb(accent)
        result = []
        
        for color in colors:
            r, g, b = self.hex_to_rgb(color)
            
            r = (r * 0.85 + r_accent * 0.15)
            g = (g * 0.85 + g_accent * 0.15)
            b = (b * 0.85 + b_accent * 0.15)
            
            r = min(255, max(0, int(r)))
            g = min(255, max(0, int(g)))
            b = min(255, max(0, int(b)))
            
            result.append(self.rgb_to_hex((r, g, b)))
            
        return result
    
    def generate_terminal_colors(self, accent: str, background: str) -> Dict[str, str]:
        """Generate a complete set of terminal colors.

        Args:
            accent: Accent color as hex
            background: Background color as hex

        Returns:
            Dictionary of terminal colors
        """
        is_dark_bg = self._is_dark_color(background)
        
        accent_rgb = self.hex_to_rgb(accent)
        r, g, b = accent_rgb
        
        if is_dark_bg:
            bright_accent = self._brighten_color(accent, 1.3)
            
            comp_accent = self._color_complement(accent)
            
            black = background if self._get_color_brightness(background) < 0.1 else "#2D2A2E"
            red = "#FF5555"
            green = "#50FA7B"
            yellow = "#F1FA8C"
            blue = accent
            magenta = "#FF79C6"
            cyan = "#8BE9FD"
            white = "#BFBFBF"
            
            bright_black = "#727072"
            bright_red = "#FF6E67"
            bright_green = "#5AF78E"
            bright_yellow = "#F4F99D"
            bright_blue = bright_accent
            bright_magenta = "#FF92D0"
            bright_cyan = "#9AEDFE"
            bright_white = "#F8F8F2"
            
            harmonized = self._adjust_color_harmony(
                [red, green, yellow, magenta, cyan, bright_red, 
                 bright_green, bright_yellow, bright_magenta, bright_cyan],
                accent
            )
            
            red, green, yellow, magenta, cyan, bright_red, bright_green, bright_yellow, bright_magenta, bright_cyan = harmonized
            
        else:
            darker_accent = self._darken_color(accent, 0.8)
            
            comp_accent = self._color_complement(accent)
            
            black = "#2D2A2E"
            red = "#E53935"
            green = "#43A047"
            yellow = "#FFB300"
            blue = accent
            magenta = "#D81B60"
            cyan = "#00ACC1"
            white = background if self._get_color_brightness(background) > 0.9 else "#F8F8F2"
            
            bright_black = "#727072"
            bright_red = "#FF5252"
            bright_green = "#69F0AE"
            bright_yellow = "#FFD740"
            bright_blue = darker_accent
            bright_magenta = "#FF4081"
            bright_cyan = "#64FFDA"
            bright_white = "#FFFFFF"
            
            harmonized = self._adjust_color_harmony(
                [red, green, yellow, magenta, cyan, bright_red, 
                 bright_green, bright_yellow, bright_magenta, bright_cyan],
                accent
            )
            
            red, green, yellow, magenta, cyan, bright_red, bright_green, bright_yellow, bright_magenta, bright_cyan = harmonized
        
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
    
    def extract_colors_from_website(self, fetcher_results: Dict) -> Dict[str, List[str]]:
        """Extract colors from website content.
        
        Args:
            fetcher_results: Results from Fetcher.fetch_all_resources
            
        Returns:
            Dictionary of categorized colors
        """
        result = {
            'background': [],
            'color': [],
            'border': [],
            'accent': [],
            'image': []
        }
        
        html_content = fetcher_results.get('html', '')
        if html_content:
            inline_css_pattern = r'style=["\']([^"\']*)["\']'
            inline_styles = re.findall(inline_css_pattern, html_content)
            
            for style in inline_styles:
                css_colors = self.extract_css_colors_categorized(style)
                for category, colors in css_colors.items():
                    result[category].extend(colors)
        
        css_contents = fetcher_results.get('css_contents', {})
        for css_url, css_content in css_contents.items():
            css_colors = self.extract_css_colors_categorized(css_content)
            for category, colors in css_colors.items():
                result[category].extend(colors)
        
        image_contents = fetcher_results.get('image_contents', {})
        for image_url, image_data in image_contents.items():
            image_colors = self.extract_image_colors_enhanced(image_data)
            result['image'].extend(image_colors)
        
        for category in result:
            result[category] = list(set(result[category]))
        
        return result
    
    def _brighten_color(self, hex_color: str, factor: float = 1.2) -> str:
        """Brighten a color by a factor.

        Args:
            hex_color: Hex color code
            factor: Brightening factor

        Returns:
            Brightened color as hex
        """
        r, g, b = self.hex_to_rgb(hex_color)
        
        hsv_brightness = self._get_color_brightness(hex_color)
        
        adjustment = factor * (1 - hsv_brightness * 0.5)
        
        r = min(255, int(r * adjustment))
        g = min(255, int(g * adjustment))
        b = min(255, int(b * adjustment))
        
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
        
        hsv_brightness = self._get_color_brightness(hex_color)
        
        adjustment = factor * (0.5 + hsv_brightness * 0.5)
        
        r = max(0, int(r * adjustment))
        g = max(0, int(g * adjustment))
        b = max(0, int(b * adjustment))
        
        return self.rgb_to_hex((r, g, b))
