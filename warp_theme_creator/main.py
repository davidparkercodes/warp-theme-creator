"""Main entry point for the Warp Theme Creator.

This module provides the command-line interface for the tool.
"""

import argparse
import os
import sys
from typing import List, Optional

from warp_theme_creator.fetcher import Fetcher
from warp_theme_creator.color_extractor import ColorExtractor
from warp_theme_creator.theme_generator import ThemeGenerator


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
    
    return parser.parse_args(args)


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
    
    print(f"Fetching content from {parsed_args.url}...")
    
    # Create instances of our modules
    fetcher = Fetcher()
    color_extractor = ColorExtractor()
    theme_generator = ThemeGenerator()
    
    # Fetch HTML content
    html_content, html_error = fetcher.fetch_html(parsed_args.url)
    if html_error:
        print(f"Error: {html_error['error']}")
        return 1
    
    print("Extracting colors...")
    
    # TODO: Parse HTML content to find CSS and image URLs
    # TODO: Extract colors from HTML, CSS, and images
    # For now, just generate a placeholder theme
    
    accent_color = "#0087D7"  # Default blue
    background_color = "#1E1E1E"  # Default dark background
    foreground_color = "#FFFFFF"  # Default white text
    
    # Generate terminal colors based on accent and background
    terminal_colors = color_extractor.generate_terminal_colors(accent_color, background_color)
    
    # Generate theme name from URL if not provided
    theme_name = parsed_args.name
    if theme_name is None:
        from urllib.parse import urlparse
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
