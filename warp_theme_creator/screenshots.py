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
            # Wait for page to load completely
            time.sleep(3)
            
            # Take screenshot
            screenshot = driver.get_screenshot_as_png()
            img = Image.open(BytesIO(screenshot))
            
            # Save if requested
            if save and self.screenshots_dir:
                # Create a safe filename from the URL
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
        # Remove the # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert hex to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Calculate perceived brightness using the formula: 
        # (0.299*R + 0.587*G + 0.114*B)
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
        n_colors: int = 12,  # Increased to get more colors
        exclude_whites: bool = False,  # Changed to False - we want to keep whites for background detection
        exclude_blacks: bool = True,
        min_saturation: float = 0.0,   # Changed to 0.0 to allow more colors including whites
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
        # Resize image for faster processing
        # The smaller dimension will be resized to max_size
        max_size = 400
        width, height = image.size
        if width > height:
            new_height = max_size
            new_width = int((width / height) * max_size)
        else:
            new_width = max_size
            new_height = int((height / width) * max_size)
            
        image = image.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert image to numpy array of RGB values
        pixels = np.array(image.convert('RGB')).reshape(-1, 3)
        
        # Apply K-means clustering
        kmeans = KMeans(n_clusters=n_colors, n_init=10)
        kmeans.fit(pixels)
        
        # Get the colors and count how many pixels belong to each cluster
        colors = kmeans.cluster_centers_.astype(int)
        labels = kmeans.labels_
        
        # Count occurrences of each label
        counts = np.bincount(labels)
        percentages = counts / len(labels)
        
        # Convert to hex and filter out unwanted colors
        result = []
        for i, (color, percentage) in enumerate(zip(colors, percentages)):
            rgb = tuple(color)
            hex_color = self.rgb_to_hex(rgb)
            
            # Convert RGB to HSV to check saturation
            r, g, b = [x/255.0 for x in rgb]
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            
            # Skip if color meets exclusion criteria
            if (exclude_whites and v > 0.95 and s < 0.1) or \
               (exclude_blacks and v < 0.1) or \
               (s < min_saturation):
                continue
                
            result.append((hex_color, float(percentage)))
            
        # Sort by percentage (most dominant first)
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
        # Special case for common background colors
        # If color is very light (near white), we consider it a potential background
        brightness = self.get_color_brightness(color)
        if brightness > 240:  # Very close to white
            return True
        
        # Convert hex to RGB
        hex_color = color.lstrip('#')
        target_rgb = (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        )
        
        width, height = image.size
        edge_pixels = []
        
        # Get pixels from the four edges
        img_rgb = image.convert('RGB')
        
        # Top edge
        for x in range(0, width, width // edge_sample_size):
            edge_pixels.append(img_rgb.getpixel((x, 0)))
            
        # Bottom edge
        for x in range(0, width, width // edge_sample_size):
            edge_pixels.append(img_rgb.getpixel((x, height - 1)))
            
        # Left edge
        for y in range(0, height, height // edge_sample_size):
            edge_pixels.append(img_rgb.getpixel((0, y)))
            
        # Right edge
        for y in range(0, height, height // edge_sample_size):
            edge_pixels.append(img_rgb.getpixel((width - 1, y)))
            
        # Count how many edge pixels are close to our target color
        tolerance = 30  # RGB distance tolerance
        matches = 0
        
        for pixel in edge_pixels:
            distance = self.get_color_distance(target_rgb, pixel)
            if distance < tolerance:
                matches += 1
                
        # If more than 25% of edge pixels match, it's likely a background color
        # Lowered from 40% to 25% to be more permissive
        return matches / len(edge_pixels) > 0.25
        
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
        if not dominant_colors:
            # Fallback if no colors were extracted
            return {
                'background': '#1E1E1E' if not prefer_light else '#FFFFFF',
                'foreground': '#FFFFFF' if not prefer_light else '#1E1E1E',
                'accent': '#0087D7'
            }
        
        # Debug all colors first
        print("\nAnalyzing colors for accent selection:")
        for color, percentage in dominant_colors:
            hex_color = color.lstrip('#')
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                print(f"  Color {color}: RGB({r},{g},{b}) - Percentage: {percentage:.2%}")
                
                # Check if this might be a good red accent
                if r > 150 and g < 100 and b < 100:
                    print(f"  *** Potential red accent detected: {color}")
            
        # Separate colors into potential backgrounds and accents
        potential_backgrounds = []
        potential_accents = []
        
        for color, percentage in dominant_colors:
            is_light = self.is_light_color(color)
            
            # Check if it's likely a background color by looking at edges
            if self.is_background_color(color, image):
                potential_backgrounds.append((color, percentage, is_light))
            else:
                # Colors that aren't backgrounds are potential accents
                potential_accents.append((color, percentage, is_light))
                
        # If no potential backgrounds found, use any color
        if not potential_backgrounds:
            potential_backgrounds = [(color, percentage, self.is_light_color(color)) 
                                    for color, percentage in dominant_colors]
            
        # If no potential accents found, use any non-background color
        if not potential_accents:
            # Create a set of background colors for quick lookup
            bg_colors = {bg[0] for bg in potential_backgrounds}
            potential_accents = [(color, percentage, self.is_light_color(color)) 
                                for color, percentage in dominant_colors
                                if color not in bg_colors]
            
        # Select background color
        background = None
        if prefer_light:
            # Look for light backgrounds first
            light_backgrounds = [bg for bg in potential_backgrounds if bg[2]]
            if light_backgrounds:
                background = light_backgrounds[0][0]
            else:
                background = '#FFFFFF'  # Fallback to white
        else:
            # Look for dark backgrounds first
            dark_backgrounds = [bg for bg in potential_backgrounds if not bg[2]]
            if dark_backgrounds:
                background = dark_backgrounds[0][0]
            else:
                background = '#1E1E1E'  # Fallback to dark
                
        # Determine text color based on background
        foreground = '#FFFFFF' if not self.is_light_color(background) else '#1E1E1E'
        
        # Select accent color that contrasts with background
        accent = None
        fg_is_light = self.is_light_color(foreground)
        
        # For Redkey.io, we want to prioritize the red accent color if present
        redkey_accent = None
        
        print("\nPotential accent colors:")
        for color, _, is_light in potential_accents:
            # Convert hex to RGB for analysis
            color_hex = color.lstrip('#')
            if len(color_hex) != 6:
                continue
                
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16)
            b = int(color_hex[4:6], 16)
            
            print(f"  Analyzing {color}: RGB({r},{g},{b})")
            
            # Skip colors that are too similar to the background
            bg_hex = background.lstrip('#')
            bg_rgb = (
                int(bg_hex[0:2], 16),
                int(bg_hex[2:4], 16),
                int(bg_hex[4:6], 16)
            )
            
            color_rgb = (r, g, b)
            
            # Check for Redkey.io red accent
            if r > 150 and g < 100 and b < 100:  # Red-ish color (more permissive)
                redkey_accent = color
                print(f"  ✓ Found potential red accent: {color} - RGB: {r},{g},{b}")
            
            distance = self.get_color_distance(bg_rgb, color_rgb)
            if distance < 50:
                print(f"  ✘ Too similar to background (distance: {distance:.1f})")
                continue
            else:
                print(f"  ✓ Good contrast with background (distance: {distance:.1f})")
                
            # Prefer colors that have the same brightness character as the foreground
            if (is_light and fg_is_light) or (not is_light and not fg_is_light):
                accent = color
                print(f"  ✓ Selected as accent: {color}")
                break
        
        # If we found the Redkey red, use it
        if redkey_accent:
            accent = redkey_accent
            print(f"\nOverriding with red accent color: {accent}")
        # If no suitable accent found, pick the first non-background color
        elif not accent and potential_accents:
            accent = potential_accents[0][0]
            print(f"\nUsing first available accent color: {accent}")
        else:
            # Fallback accent color
            accent = '#C6262E' if '#C6262E' in [c[0] for c in dominant_colors] else '#0087D7'
            print(f"\nUsing fallback accent color: {accent}")
            
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
        # Take screenshot
        img = self.take_screenshot(url, save=save_screenshot)
        
        # Extract dominant colors from the image
        dominant_colors = self.extract_colors_from_image(img, n_colors=10)
        
        # Select colors for theme
        theme_colors = self.select_colors_for_theme(
            dominant_colors,
            img,
            prefer_light=prefer_light
        )
        
        # Print dominant colors for debugging
        print("Dominant colors extracted:")
        for color, percentage in dominant_colors:
            brightness = self.get_color_brightness(color)
            print(f"  {color}: {percentage:.2%} (brightness: {brightness:.1f})")
            
        print("\nSelected theme colors:")
        for key, color in theme_colors.items():
            brightness = self.get_color_brightness(color)
            print(f"  {key}: {color} (brightness: {brightness:.1f})")
            
        return theme_colors