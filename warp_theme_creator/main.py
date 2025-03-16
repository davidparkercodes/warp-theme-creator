"""Main entry point for the Warp Theme Creator.

This module provides the command-line interface for the tool.
"""

import argparse
import os
import sys
from typing import List, Optional, Dict
from urllib.parse import urlparse
import re

from warp_theme_creator.fetcher import Fetcher
from warp_theme_creator.color_extractor import ColorExtractor
from warp_theme_creator.theme_generator import ThemeGenerator
from warp_theme_creator.utils import adjust_color_brightness, adjust_color_saturation


def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args: Command line arguments

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate Warp terminal themes from website colors",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "url",
        help="URL of the website to extract colors from"
    )
    
    parser.add_argument(
        "--name",
        default=None,
        help="Name for the generated theme (default: website domain)"
    )
    
    parser.add_argument(
        "--output",
        default="./themes",
        help="Directory to save the generated theme"
    )
    
    parser.add_argument(
        "--extract-background",
        action="store_true",
        help="Extract and use background image from website"
    )
    
    parser.add_argument(
        "--brightness",
        type=float,
        default=1.0,
        help="Brightness adjustment factor for colors"
    )
    
    parser.add_argument(
        "--saturation",
        type=float,
        default=1.0,
        help="Saturation adjustment factor for colors"
    )
    
    parser.add_argument(
        "--prefer-light",
        action="store_true",
        help="Prefer light background instead of dark"
    )
    
    parser.add_argument(
        "--max-css",
        type=int,
        default=10,
        help="Maximum number of CSS files to fetch"
    )
    
    parser.add_argument(
        "--max-images",
        type=int,
        default=5,
        help="Maximum number of images to analyze"
    )
    
    return parser.parse_args(args)


def fetch_website_resources(fetcher: Fetcher, url: str, max_css: int, max_images: int) -> Dict:
    """Fetch website resources for color extraction.

    Args:
        fetcher: Fetcher instance
        url: Website URL
        max_css: Maximum number of CSS files to fetch
        max_images: Maximum number of images to analyze

    Returns:
        Dictionary of fetched resources
    """
    print(f"Fetching HTML content from {url}...")
    resources = fetcher.fetch_all_resources(url, max_css=max_css, max_images=max_images)
    
    if not resources.get('html'):
        print("Error: Failed to fetch HTML content.")
        return resources
    
    # Fetch CSS files
    css_urls = resources.get('css_urls', [])
    css_contents = {}
    
    if css_urls:
        print(f"Fetching {len(css_urls)} CSS files...")
        for css_url in css_urls:
            css_content, css_error = fetcher.fetch_css(url, css_url)
            if css_content:
                css_contents[css_url] = css_content
            elif css_error:
                resources.setdefault('errors', {})
                resources['errors'][f'css_{css_url}'] = css_error['error']
    
    resources['css_contents'] = css_contents
    
    # Fetch images
    image_urls = resources.get('image_urls', [])
    image_contents = {}
    
    if image_urls:
        print(f"Fetching {len(image_urls)} images...")
        for image_url in image_urls:
            image_data, image_error = fetcher.fetch_image(url, image_url)
            if image_data:
                image_contents[image_url] = image_data
            elif image_error:
                resources.setdefault('errors', {})
                resources['errors'][f'image_{image_url}'] = image_error['error']
    
    resources['image_contents'] = image_contents
    
    return resources


def extract_theme_colors(color_extractor: ColorExtractor, resources: Dict, prefer_light: bool = False) -> Dict[str, str]:
    """Extract theme colors from fetched website resources.

    Args:
        color_extractor: ColorExtractor instance
        resources: Fetched website resources
        prefer_light: Whether to prefer light background

    Returns:
        Dictionary with accent, background, and foreground colors
    """
    all_colors = []
    categorized_colors = {
        'background': [],
        'color': [],
        'border': [],
        'accent': [],
        'image': []
    }
    
    # Process HTML inline styles
    html_content = resources.get('html', '')
    if html_content:
        inline_css_pattern = r'style=["\']([^"\']*)["\']'
        inline_styles = re.findall(inline_css_pattern, html_content)
        
        for style in inline_styles:
            css_colors = color_extractor.extract_css_colors(style)
            for category, colors in css_colors.items():
                categorized_colors[category].extend(colors)
                all_colors.extend(colors)
    
    # Process CSS files
    css_contents = resources.get('css_contents', {})
    for css_url, css_content in css_contents.items():
        css_colors = color_extractor.extract_css_colors(css_content)
        for category, colors in css_colors.items():
            categorized_colors[category].extend(colors)
            all_colors.extend(colors)
    
    # Process images
    image_contents = resources.get('image_contents', {})
    for image_url, image_data in image_contents.items():
        image_colors = color_extractor.extract_image_colors(image_data)
        categorized_colors['image'].extend(image_colors)
        all_colors.extend(image_colors)
    
    # Remove duplicates
    all_colors = list(set(all_colors))
    for category in categorized_colors:
        categorized_colors[category] = list(set(categorized_colors[category]))
    
    # Extract accent color (prioritize accent category, then image, then others)
    accent_candidates = (
        categorized_colors['accent'] + 
        categorized_colors['image'] + 
        categorized_colors['border'] +
        categorized_colors['color'] +
        categorized_colors['background']
    )
    accent_color = color_extractor.select_accent_color(accent_candidates) if accent_candidates else "#0087D7"
    
    # Extract background color (prioritize background category)
    background_candidates = categorized_colors['background'] + all_colors
    background_color = color_extractor.select_background_color(
        background_candidates, 
        prefer_dark=not prefer_light
    ) if background_candidates else ("#FFFFFF" if prefer_light else "#1E1E1E")
    
    # Determine foreground color based on background
    foreground_color = color_extractor.select_foreground_color(background_color)
    
    return {
        'accent': accent_color,
        'background': background_color,
        'foreground': foreground_color
    }


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the application.

    Args:
        args: Command line arguments

    Returns:
        Exit code
    """
    if args is None:
        args = sys.argv[1:]
    
    parsed_args = parse_args(args)
    
    # Create instances of our modules
    fetcher = Fetcher()
    color_extractor = ColorExtractor()
    theme_generator = ThemeGenerator()
    
    # Validate URL
    if not fetcher.validate_url(parsed_args.url):
        print(f"Error: Invalid URL format: {parsed_args.url}")
        print("Please provide a valid URL starting with http:// or https://")
        return 1
    
    # Fetch website resources
    resources = fetch_website_resources(
        fetcher, 
        parsed_args.url, 
        parsed_args.max_css, 
        parsed_args.max_images
    )
    
    # Check if fetching was successful
    if not resources.get('html'):
        return 1
    
    print("Extracting colors...")
    
    # Extract theme colors
    theme_colors = extract_theme_colors(
        color_extractor, 
        resources, 
        parsed_args.prefer_light
    )
    
    # Apply brightness and saturation adjustments if needed
    if parsed_args.brightness != 1.0 or parsed_args.saturation != 1.0:
        print(f"Adjusting colors (brightness: {parsed_args.brightness}, saturation: {parsed_args.saturation})...")
        
        for key in theme_colors:
            if parsed_args.brightness != 1.0:
                theme_colors[key] = adjust_color_brightness(theme_colors[key], parsed_args.brightness)
            
            if parsed_args.saturation != 1.0:
                theme_colors[key] = adjust_color_saturation(theme_colors[key], parsed_args.saturation)
    
    accent_color = theme_colors['accent']
    background_color = theme_colors['background']
    foreground_color = theme_colors['foreground']
    
    print(f"Selected colors:")
    print(f"  Accent: {accent_color}")
    print(f"  Background: {background_color}")
    print(f"  Foreground: {foreground_color}")
    
    # Generate terminal colors based on accent and background
    terminal_colors = color_extractor.generate_terminal_colors(accent_color, background_color)
    
    # Generate theme name from URL if not provided
    theme_name = parsed_args.name
    if theme_name is None:
        domain = urlparse(parsed_args.url).netloc
        theme_name = domain.replace("www.", "").split(".")[0].title()
    
    # Create theme
    theme = theme_generator.create_theme(
        accent=accent_color,
        background=background_color,
        foreground=foreground_color,
        terminal_colors=terminal_colors,
        name=theme_name
    )
    
    # Save theme
    output_dir = os.path.abspath(parsed_args.output)
    theme_path = theme_generator.save_theme(theme, output_dir)
    
    print(f"Theme generated successfully: {theme_path}")
    print(f"Install with: cp {theme_path} ~/.warp/themes/")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
