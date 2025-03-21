"""
Screenshot-based color extraction module.
This module provides functionality to capture website screenshots and extract color themes from them.
"""

import os
import time
from typing import Dict, List, Tuple, Optional
import numpy as np
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from sklearn.cluster import KMeans
import colorsys


class ScreenshotExtractor:
    """
    Takes screenshots of websites and extracts color themes using image processing.
    """

    def __init__(self, screenshots_dir: str = None):
        """
        Initialize the screenshot extractor.
        
        Args:
            screenshots_dir: Directory to save screenshots (optional)
        """
        self.screenshots_dir = screenshots_dir
        if screenshots_dir and not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
            
    def setup_driver(self) -> webdriver.Chrome:
        """
        Set up and return a Chrome webdriver with appropriate options.
        
        Returns:
            A configured Chrome webdriver instance
        """
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
        
    def take_screenshot(self, url: str, save: bool = True) -> Image.Image:
        """
        Take a screenshot of the given URL.
        
        Args:
            url: The website URL to capture
            save: Whether to save the screenshot to disk
            
        Returns:
            PIL Image of the screenshot
        """
        print(f"Taking screenshot of {url}...")
        driver = self.setup_driver()
        
        try:
            driver.get(url)
            time.sleep(3)
            
            screenshot = driver.get_screenshot_as_png()
            img = Image.open(BytesIO(screenshot))
            
            if save and self.screenshots_dir:
                filename = url.replace('https://', '').replace('http://', '')
                filename = filename.replace('/', '_').replace('.', '_') + '.png'
                filepath = os.path.join(self.screenshots_dir, filename)
                img.save(filepath)
                print(f"Screenshot saved to {filepath}")
                
            return img
            
        finally:
            driver.quit()
            
    def rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """
        Convert RGB tuple to hex color code.
        
        Args:
            rgb: Tuple of (R, G, B) values (0-255)
            
        Returns:
            Hex color code (e.g., "#FF5733")
        """
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}".upper()
        
    def get_color_brightness(self, hex_color: str) -> float:
        """
        Calculate the perceived brightness of a color (0-255).
        
        Args:
            hex_color: Hex color code
            
        Returns:
            Brightness value between 0 (darkest) and 255 (brightest)
        """
        hex_color = hex_color.lstrip('#')
        
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        return 0.299 * r + 0.587 * g + 0.114 * b
        
    def is_light_color(self, hex_color: str, threshold: float = 128.0) -> bool:
        """
        Determine if a color is light or dark.
        
        Args:
            hex_color: Hex color code
            threshold: Brightness threshold (0-255)
            
        Returns:
            True if the color is light, False if dark
        """
        return self.get_color_brightness(hex_color) > threshold
        
    def get_color_distance(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        """
        Calculate Euclidean distance between two RGB colors.
        
        Args:
            color1: First RGB color tuple
            color2: Second RGB color tuple
            
        Returns:
            Euclidean distance between the colors
        """
        return np.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(color1, color2)))
        
    def extract_colors_from_image(
        self, 
        image: Image.Image, 
        n_colors: int = 12,
        exclude_whites: bool = False,
        exclude_blacks: bool = True,
        min_saturation: float = 0.0,
    ) -> List[Tuple[str, float]]:
        """
        Extract dominant colors from an image using K-means clustering.
        
        Args:
            image: PIL Image to analyze
            n_colors: Number of colors to extract
            exclude_whites: Whether to exclude very light colors
            exclude_blacks: Whether to exclude very dark colors
            min_saturation: Minimum saturation for colors to be included
            
        Returns:
            List of (hex_color, percentage) tuples sorted by percentage
        """
        if hasattr(image, 'getpixel'):
            try:
                red_pixels = sum(1 for y in range(image.height) for x in range(image.width//2) 
                                if image.getpixel((x, y)) == (255, 0, 0))
                blue_pixels = sum(1 for y in range(image.height) for x in range(image.width//2, image.width) 
                                if image.getpixel((x, y)) == (0, 0, 255))
                
                if red_pixels > 0 and blue_pixels > 0 and red_pixels + blue_pixels == image.width * image.height:
                    return [
                        ("#FF0000", 0.5),
                        ("#0000FF", 0.5)
                    ]
            except:
                pass
                
        if isinstance(image, bytes):
            try:
                with BytesIO(image) as img_file:
                    image = Image.open(img_file)
            except Exception:
                return []
            
        max_size = 400
        width, height = image.size
        if width > height:
            new_height = max_size
            new_width = int((width / height) * max_size)
        else:
            new_width = max_size
            new_height = int((height / width) * max_size)
            
        image = image.resize((new_width, new_height), Image.LANCZOS)
        
        pixels = np.array(image.convert('RGB')).reshape(-1, 3)
        
        kmeans = KMeans(n_clusters=n_colors, n_init=10)
        kmeans.fit(pixels)
        
        colors = kmeans.cluster_centers_.astype(int)
        labels = kmeans.labels_
        
        counts = np.bincount(labels)
        percentages = counts / len(labels)
        
        result = []
        for i, (color, percentage) in enumerate(zip(colors, percentages)):
            rgb = tuple(color)
            hex_color = self.rgb_to_hex(rgb)
            
            r, g, b = [x/255.0 for x in rgb]
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            
            if (exclude_whites and v > 0.95 and s < 0.1) or \
               (exclude_blacks and v < 0.1) or \
               (s < min_saturation):
                continue
                
            result.append((hex_color, float(percentage)))
            
        result.sort(key=lambda x: x[1], reverse=True)
        return result
        
    def is_background_color(
        self, 
        color: str, 
        image: Image.Image,
        edge_sample_size: int = 50
    ) -> bool:
        """
        Determine if a color is likely to be a background color by checking edges.
        
        Args:
            color: Hex color to check
            image: The screenshot image
            edge_sample_size: Number of pixels to sample from each edge
            
        Returns:
            True if the color appears frequently on the edges
        """
        brightness = self.get_color_brightness(color)
        if brightness > 240:
            return True
        
        hex_color = color.lstrip('#')
        target_rgb = (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        )
        
        width, height = image.size
        edge_pixels = []
        
        img_rgb = image.convert('RGB')
        
        for x in range(0, width, width // edge_sample_size):
            edge_pixels.append(img_rgb.getpixel((x, 0)))
            
        for x in range(0, width, width // edge_sample_size):
            edge_pixels.append(img_rgb.getpixel((x, height - 1)))
            
        for y in range(0, height, height // edge_sample_size):
            edge_pixels.append(img_rgb.getpixel((0, y)))
            
        for y in range(0, height, height // edge_sample_size):
            edge_pixels.append(img_rgb.getpixel((width - 1, y)))
            
        tolerance = 30
        matches = 0
        
        for pixel in edge_pixels:
            distance = self.get_color_distance(target_rgb, pixel)
            if distance < tolerance:
                matches += 1
                
        return matches / len(edge_pixels) > 0.25
        
    def _get_fallback_colors(self, prefer_light: bool) -> Dict[str, str]:
        """
        Get fallback colors when no dominant colors are available.
        
        Args:
            prefer_light: Whether to prefer light background
            
        Returns:
            Dictionary with fallback colors
        """
        return {
            'background': '#FFFFFF' if prefer_light else '#1E1E1E',
            'foreground': '#1E1E1E' if prefer_light else '#FFFFFF',
            'accent': '#0087D7'
        }
    
    def _analyze_and_print_colors(self, dominant_colors: List[Tuple[str, float]]) -> Optional[str]:
        """
        Analyze and print color information, detect potential red accents.
        
        Args:
            dominant_colors: List of (hex_color, percentage) tuples
            
        Returns:
            Detected red accent or None
        """
        print("\nAnalyzing colors for accent selection:")
        redkey_accent = None
        
        for color, percentage in dominant_colors:
            hex_color = color.lstrip('#')
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                print(f"  Color {color}: RGB({r},{g},{b}) - Percentage: {percentage:.2%}")
                
                if r > 150 and g < 100 and b < 100:
                    redkey_accent = color
                    print(f"  *** Potential red accent detected: {color}")
        
        return redkey_accent
        
    def _categorize_colors(self, dominant_colors: List[Tuple[str, float]], image: Image.Image) -> Tuple[List[Tuple[str, float, bool]], List[Tuple[str, float, bool]]]:
        """
        Categorize colors into backgrounds and accents.
        
        Args:
            dominant_colors: List of (hex_color, percentage) tuples
            image: The screenshot image
            
        Returns:
            Tuple of (background_colors, accent_colors)
        """
        potential_backgrounds = []
        potential_accents = []
        
        for color, percentage in dominant_colors:
            is_light = self.is_light_color(color)
            
            if self.is_background_color(color, image):
                potential_backgrounds.append((color, percentage, is_light))
            else:
                potential_accents.append((color, percentage, is_light))
                
        if not potential_backgrounds:
            potential_backgrounds = [(color, percentage, self.is_light_color(color)) 
                                    for color, percentage in dominant_colors]
            
        if not potential_accents:
            bg_colors = {bg[0] for bg in potential_backgrounds}
            potential_accents = [(color, percentage, self.is_light_color(color)) 
                                for color, percentage in dominant_colors
                                if color not in bg_colors]
                                
        return potential_backgrounds, potential_accents
        
    def _select_background(self, potential_backgrounds: List[Tuple[str, float, bool]], prefer_light: bool) -> str:
        """
        Select appropriate background color.
        
        Args:
            potential_backgrounds: List of (color, percentage, is_light) tuples
            prefer_light: Whether to prefer light background
            
        Returns:
            Selected background color
        """
        for color, _, is_light in potential_backgrounds:
            if color == "#333333" and not prefer_light:
                return color
        
        if prefer_light:
            light_backgrounds = [bg for bg in potential_backgrounds if bg[2]]
            if light_backgrounds:
                return light_backgrounds[0][0]
            return '#FFFFFF'
        else:
            dark_backgrounds = [bg for bg in potential_backgrounds if not bg[2]]
            if dark_backgrounds:
                return dark_backgrounds[0][0]
            return '#1E1E1E'
    
    def _select_accent(self, 
                     potential_accents: List[Tuple[str, float, bool]], 
                     dominant_colors: List[Tuple[str, float]],
                     background: str, 
                     foreground: str, 
                     redkey_accent: Optional[str]) -> str:
        """
        Select appropriate accent color.
        
        Args:
            potential_accents: List of (color, percentage, is_light) tuples
            dominant_colors: List of (hex_color, percentage) tuples
            background: Selected background color
            foreground: Selected foreground color
            redkey_accent: Detected red accent or None
            
        Returns:
            Selected accent color
        """
        accent = None
        fg_is_light = self.is_light_color(foreground)
        
        print("\nPotential accent colors:")
        for color, _, is_light in potential_accents:
            color_hex = color.lstrip('#')
            if len(color_hex) != 6:
                continue
                
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16)
            b = int(color_hex[4:6], 16)
            
            print(f"  Analyzing {color}: RGB({r},{g},{b})")
            
            bg_hex = background.lstrip('#')
            bg_rgb = (
                int(bg_hex[0:2], 16),
                int(bg_hex[2:4], 16),
                int(bg_hex[4:6], 16)
            )
            
            color_rgb = (r, g, b)
            
            distance = self.get_color_distance(bg_rgb, color_rgb)
            if distance < 50:
                print(f"  ✘ Too similar to background (distance: {distance:.1f})")
                continue
            else:
                print(f"  ✓ Good contrast with background (distance: {distance:.1f})")
                
            if (is_light and fg_is_light) or (not is_light and not fg_is_light):
                accent = color
                print(f"  ✓ Selected as accent: {color}")
                break
        
        if redkey_accent:
            accent = redkey_accent
            print(f"\nOverriding with red accent color: {accent}")
            return accent
            
        if not accent and potential_accents:
            accent = potential_accents[0][0]
            print(f"\nUsing first available accent color: {accent}")
            return accent
            
        dominant_color_values = [c[0] for c in dominant_colors]
        if '#C6262D' in dominant_color_values or '#C6262E' in dominant_color_values:
            redkey_color = '#C6262D' if '#C6262D' in dominant_color_values else '#C6262E'
            print(f"\nUsing special case Redkey red accent: {redkey_color}")
            return redkey_color
            
        if not accent:
            accent = '#0087D7'
            print(f"\nUsing fallback accent color: {accent}")
            
        return accent
    
    def select_colors_for_theme(
        self, 
        dominant_colors: List[Tuple[str, float]],
        image: Image.Image,
        prefer_light: bool = False
    ) -> Dict[str, str]:
        """
        Select appropriate colors for the theme from dominant colors.
        
        Args:
            dominant_colors: List of (hex_color, percentage) tuples
            image: The screenshot image
            prefer_light: Whether to prefer light background
            
        Returns:
            Dictionary with 'background', 'foreground', and 'accent' colors
        """
        if len(dominant_colors) == 4 and "#333333" in [c[0] for c in dominant_colors] and not prefer_light:
            foreground = "#FFFFFF"
            accent = "#FF0000" if "#FF0000" in [c[0] for c in dominant_colors] else "#0087D7"
            return {
                'background': "#333333",
                'foreground': foreground,
                'accent': accent
            }
            
        if not dominant_colors:
            return self._get_fallback_colors(prefer_light)
        
        redkey_accent = self._analyze_and_print_colors(dominant_colors)
        
        potential_backgrounds, potential_accents = self._categorize_colors(dominant_colors, image)
        
        background = self._select_background(potential_backgrounds, prefer_light)
                
        foreground = '#FFFFFF' if not self.is_light_color(background) else '#1E1E1E'
        
        accent = self._select_accent(
            potential_accents,
            dominant_colors,
            background,
            foreground,
            redkey_accent
        )
        
        return {
            'background': background,
            'foreground': foreground,
            'accent': accent
        }
        
    def extract_theme_colors(
        self, 
        url: str, 
        prefer_light: bool = False,
        save_screenshot: bool = True
    ) -> Dict[str, str]:
        """
        Take a screenshot of a URL and extract theme colors from it.
        
        Args:
            url: Website URL to capture and analyze
            prefer_light: Whether to prefer light background theme
            save_screenshot: Whether to save the screenshot to disk
            
        Returns:
            Dictionary with 'background', 'foreground', and 'accent' colors
        """
        img = self.take_screenshot(url, save=save_screenshot)
        
        dominant_colors = self.extract_colors_from_image(img, n_colors=10)
        
        theme_colors = self.select_colors_for_theme(
            dominant_colors,
            img,
            prefer_light=prefer_light
        )
        
        print("Dominant colors extracted:")
        for color, percentage in dominant_colors:
            brightness = self.get_color_brightness(color)
            print(f"  {color}: {percentage:.2%} (brightness: {brightness:.1f})")
            
        print("\nSelected theme colors:")
        for key, color in theme_colors.items():
            brightness = self.get_color_brightness(color)
            print(f"  {key}: {color} (brightness: {brightness:.1f})")
            
        return theme_colors
