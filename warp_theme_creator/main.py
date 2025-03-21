"""Main entry point for the Warp Theme Creator.

This module provides the command-line interface for the tool.
"""

import argparse
import os
import sys
import shutil
from typing import List, Optional, Dict, Tuple, Any
from urllib.parse import urlparse
import re
from io import BytesIO
from PIL import Image

from warp_theme_creator.fetcher import Fetcher
from warp_theme_creator.color_extractor import ColorExtractor
from warp_theme_creator.theme_generator import ThemeGenerator
from warp_theme_creator.preview import ThemePreviewGenerator
from warp_theme_creator.utils import adjust_color_brightness, adjust_color_saturation
from warp_theme_creator.screenshots import ScreenshotExtractor


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
        "--background-opacity",
        type=float,
        default=0.8,
        help="Opacity value for background image (0.0 to 1.0)"
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
    
    preview_group = parser.add_mutually_exclusive_group()
    preview_group.add_argument(
        "--generate-preview",
        action="store_true",
        default=True,
        help="Generate SVG preview of the theme (enabled by default)"
    )
    preview_group.add_argument(
        "--no-generate-preview",
        action="store_false",
        dest="generate_preview",
        help="Disable SVG preview generation"
    )
    
    parser.add_argument(
        "--generate-all-previews",
        action="store_true",
        help="Generate SVG previews for all themes in the output directory"
    )
    
    parser.add_argument(
        "--png",
        action="store_true",
        help="Also generate PNG versions of previews"
    )
    
    parser.add_argument(
        "--use-screenshot",
        action="store_true",
        help="Use screenshot-based color extraction (more accurate for visual appearance)"
    )
    
    parser.add_argument(
        "--save-screenshot",
        action="store_true",
        help="Save the screenshot taken for color extraction"
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


def validate_image(img_file: BytesIO) -> Optional[Tuple[int, int, float]]:
    """Validate an image and extract its dimensions and aspect ratio.
    
    Args:
        img_file: BytesIO object containing image data
        
    Returns:
        Tuple of (width, height, aspect_ratio) or None if invalid
    """
    try:
        with Image.open(img_file) as img:
            if not img.format:
                return None
            
            width, height = img.size
            aspect_ratio = width / height if height > 0 else 0
            
            return width, height, aspect_ratio
    except Exception:
        return None


def filter_suitable_background_images(resources: Dict) -> List[Dict]:
    """Filter images suitable for background use.
    
    Args:
        resources: Fetched website resources
        
    Returns:
        List of suitable image data dictionaries
    """
    if not resources.get('image_contents'):
        return []
    
    image_data = []
    
    for image_url, image_bytes in resources.get('image_contents', {}).items():
        try:
            with BytesIO(image_bytes) as img_file:
                dimensions = validate_image(img_file)
                if not dimensions:
                    continue
                    
                width, height, aspect_ratio = dimensions
                
                img_file.seek(0)
                
                size = width * height
                if size < 10000 or aspect_ratio > 5 or aspect_ratio < 0.2:
                    continue
                
                image_data.append({
                    'url': image_url,
                    'bytes': image_bytes,
                    'size': size,
                    'width': width,
                    'height': height
                })
        except Exception:
            continue
    
    image_data.sort(key=lambda x: x['size'], reverse=True)
    return image_data


def resize_image_if_needed(img: Image.Image, max_dimension: int = 1920) -> Image.Image:
    """Resize image if it exceeds the maximum dimension.
    
    Args:
        img: PIL Image object
        max_dimension: Maximum allowed dimension
        
    Returns:
        Resized or original image
    """
    if img.width <= max_dimension and img.height <= max_dimension:
        return img
        
    if img.width > img.height:
        new_width = max_dimension
        new_height = int(img.height * (max_dimension / img.width))
    else:
        new_height = max_dimension
        new_width = int(img.width * (max_dimension / img.height))
        
    return img.resize((new_width, new_height), Image.LANCZOS)


def save_background_image(image_data: Dict, theme_name: str, output_dir: str) -> Optional[str]:
    """Save the selected background image.
    
    Args:
        image_data: Selected image data dictionary
        theme_name: Name of the theme (used for filename)
        output_dir: Directory to save the image
        
    Returns:
        Path to saved image or None if operation failed
    """
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    sanitized_name = ''.join(c for c in theme_name.lower() if c.isalnum() or c == '_')
    filename = f"{sanitized_name}_background.jpg"
    output_path = os.path.join(images_dir, filename)
    
    try:
        with BytesIO(image_data['bytes']) as img_file:
            with Image.open(img_file) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img = resize_image_if_needed(img)
                
                img.save(output_path, "JPEG", quality=90)
                return output_path
    except Exception:
        return None
    
    return None


def extract_background_image(resources: Dict, theme_name: str, output_dir: str) -> Optional[str]:
    """Extract and save a suitable background image from website resources.
    
    Args:
        resources: Fetched website resources
        theme_name: Name of the theme (used for filename)
        output_dir: Directory to save the image
        
    Returns:
        Path to saved background image or None if no suitable image found
    """
    image_data = filter_suitable_background_images(resources)
    
    if not image_data:
        return None
    
    selected_image = image_data[0]
    
    return save_background_image(selected_image, theme_name, output_dir)


def score_logo_image(image_url: str, img: Image.Image) -> int:
    """Score an image based on logo heuristics.
    
    Args:
        image_url: URL of the image
        img: PIL Image object
        
    Returns:
        Score indicating likelihood of being a logo
    """
    score = 0
    width, height = img.size
    size = width * height
    
    if size < 50000:
        score += 20
    elif size < 150000:
        score += 10
    else:
        score -= 10
    
    if img.mode == 'RGBA':
        score += 10
    
    url_lower = image_url.lower()
    if any(keyword in url_lower for keyword in ['logo', 'brand', 'icon', 'symbol', 'header']):
        score += 25
    
    aspect_ratio = width / height if height > 0 else 0
    if 0.5 <= aspect_ratio <= 2.0:
        score += 10
    else:
        score -= 5
        
    if url_lower.endswith(('.svg', '.png')):
        score += 15
        
    return score


def process_image_for_logo(image_url: str, image_data: bytes) -> Optional[Dict]:
    """Process an image to determine if it might be a logo.
    
    Args:
        image_url: URL of the image
        image_data: Binary image data
        
    Returns:
        Dictionary with image data and score or None if invalid
    """
    try:
        with BytesIO(image_data) as img_file:
            with Image.open(img_file) as img:
                if not img.format:
                    return None
                    
                score = score_logo_image(image_url, img)
                
                width, height = img.size
                size = width * height
                
                return {
                    'url': image_url,
                    'data': image_data,
                    'score': score,
                    'size': size
                }
    except Exception:
        return None
    
    return None


def identify_logo_images(resources: Dict) -> Dict[str, bytes]:
    """Identifies potential logo images from website resources.

    Args:
        resources: Fetched website resources

    Returns:
        Dictionary of logo URL to image data
    """
    image_contents = resources.get('image_contents', {})
    
    if not image_contents:
        return {}
        
    scored_images = []
    
    for image_url, image_data in image_contents.items():
        scored_image = process_image_for_logo(image_url, image_data)
        if scored_image:
            scored_images.append(scored_image)
    
    scored_images.sort(key=lambda x: x['score'], reverse=True)
    
    top_images = scored_images[:3] if scored_images else []
    
    return {img['url']: img['data'] for img in top_images}

def extract_css_colors_from_html(color_extractor: ColorExtractor, html_content: str) -> Tuple[List[str], Dict[str, List[str]]]:
    """Extract colors from HTML inline styles.
    
    Args:
        color_extractor: ColorExtractor instance
        html_content: HTML content as string
        
    Returns:
        Tuple of (all_colors, categorized_colors)
    """
    all_colors = []
    categorized_colors = {
        'background': [],
        'color': [],
        'border': [],
        'accent': [],
        'image': []
    }
    
    if not html_content:
        return all_colors, categorized_colors
    
    inline_css_pattern = r'style=["\']([^"\']*)["\']'
    inline_styles = re.findall(inline_css_pattern, html_content)
    
    for style in inline_styles:
        css_colors = color_extractor.extract_css_colors_categorized(style)
        for category, colors in css_colors.items():
            categorized_colors[category].extend(colors)
            all_colors.extend(colors)
            
    return all_colors, categorized_colors


def extract_css_colors_from_stylesheets(color_extractor: ColorExtractor, css_contents: Dict[str, str]) -> Tuple[List[str], Dict[str, List[str]]]:
    """Extract colors from CSS stylesheets.
    
    Args:
        color_extractor: ColorExtractor instance
        css_contents: Dictionary of CSS URL to content
        
    Returns:
        Tuple of (all_colors, categorized_colors)
    """
    all_colors = []
    categorized_colors = {
        'background': [],
        'color': [],
        'border': [],
        'accent': [],
        'image': []
    }
    
    for css_url, css_content in css_contents.items():
        css_colors = color_extractor.extract_css_colors_categorized(css_content)
        for category, colors in css_colors.items():
            categorized_colors[category].extend(colors)
            all_colors.extend(colors)
            
    return all_colors, categorized_colors


def extract_colors_from_logos(color_extractor: ColorExtractor, logo_images: Dict[str, bytes]) -> Tuple[List[str], List[str]]:
    """Extract colors from logo images.
    
    Args:
        color_extractor: ColorExtractor instance
        logo_images: Dictionary of logo URL to image data
        
    Returns:
        Tuple of (all_colors, logo_colors)
    """
    all_colors = []
    logo_colors = []
    
    for image_url, image_data in logo_images.items():
        image_colors = color_extractor.extract_image_colors_enhanced(image_data)
        logo_colors.extend(image_colors)
        all_colors.extend(image_colors)
        
    return all_colors, logo_colors


def extract_colors_from_general_images(color_extractor: ColorExtractor, image_contents: Dict[str, bytes], logo_images: Dict[str, bytes]) -> List[str]:
    """Extract colors from general (non-logo) images.
    
    Args:
        color_extractor: ColorExtractor instance
        image_contents: Dictionary of image URL to image data
        logo_images: Dictionary of logo URLs to skip
        
    Returns:
        List of extracted colors
    """
    all_colors = []
    
    for image_url, image_data in image_contents.items():
        if image_url in logo_images:
            continue
            
        image_colors = color_extractor.extract_image_colors_enhanced(image_data)
        all_colors.extend(image_colors)
        
    return all_colors


def prioritize_accent_candidates(logo_colors: List[str], categorized_colors: Dict[str, List[str]]) -> List[str]:
    """Prioritize color candidates for accent color.
    
    Args:
        logo_colors: Colors extracted from logo images
        categorized_colors: Categorized colors from CSS
        
    Returns:
        Prioritized list of accent color candidates
    """
    if logo_colors:
        return (
            logo_colors +
            categorized_colors['accent'] + 
            categorized_colors['border'] +
            categorized_colors['color'] +
            categorized_colors['background']
        )
    else:
        return (
            categorized_colors['accent'] + 
            categorized_colors['image'] + 
            categorized_colors['border'] +
            categorized_colors['color'] +
            categorized_colors['background']
        )


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
    
    html_colors, html_categorized = extract_css_colors_from_html(
        color_extractor, 
        resources.get('html', '')
    )
    all_colors.extend(html_colors)
    for category in categorized_colors:
        categorized_colors[category].extend(html_categorized[category])
    
    css_colors, css_categorized = extract_css_colors_from_stylesheets(
        color_extractor, 
        resources.get('css_contents', {})
    )
    all_colors.extend(css_colors)
    for category in categorized_colors:
        categorized_colors[category].extend(css_categorized[category])
    
    logo_images = identify_logo_images(resources)
    logo_image_colors, logo_colors = extract_colors_from_logos(
        color_extractor, 
        logo_images
    )
    all_colors.extend(logo_image_colors)
    categorized_colors['image'].extend(logo_image_colors)
    
    if not logo_colors:
        print("No logo detected, using general site imagery...")
        general_image_colors = extract_colors_from_general_images(
            color_extractor,
            resources.get('image_contents', {}),
            logo_images
        )
        all_colors.extend(general_image_colors)
        categorized_colors['image'].extend(general_image_colors)
    else:
        print(f"Using colors from {len(logo_images)} potential logo/brand images...")
    
    all_colors = list(set(all_colors))
    for category in categorized_colors:
        categorized_colors[category] = list(set(categorized_colors[category]))
    
    accent_candidates = prioritize_accent_candidates(logo_colors, categorized_colors)
    accent_color = color_extractor.select_accent_color(accent_candidates) if accent_candidates else "#0087D7"
    
    background_candidates = categorized_colors['background'] + all_colors
    background_color = color_extractor.select_background_color(
        background_candidates, 
        prefer_dark=not prefer_light
    ) if background_candidates else ("#FFFFFF" if prefer_light else "#1E1E1E")
    
    foreground_color = color_extractor.select_foreground_color(background_color)
    
    return {
        'accent': accent_color,
        'background': background_color,
        'foreground': foreground_color
    }


def initialize_output_directory(output_path: str) -> str:
    """Initialize and return the output directory path.

    Args:
        output_path: The specified output path

    Returns:
        Absolute path to the output directory
    """
    output_dir = os.path.abspath(output_path)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def determine_theme_name(provided_name: Optional[str], url: str) -> str:
    """Determine the theme name from either provided name or URL.

    Args:
        provided_name: User provided theme name or None
        url: Website URL

    Returns:
        Theme name
    """
    if provided_name:
        return provided_name
        
    domain = urlparse(url).netloc
    return domain.replace("www.", "").split(".")[0].title()


def apply_color_adjustments(theme_colors: Dict[str, str], brightness: float, saturation: float) -> Dict[str, str]:
    """Apply brightness and saturation adjustments to colors.

    Args:
        theme_colors: Dictionary of colors
        brightness: Brightness adjustment factor
        saturation: Saturation adjustment factor

    Returns:
        Adjusted theme colors
    """
    if brightness == 1.0 and saturation == 1.0:
        return theme_colors
        
    print(f"Adjusting colors (brightness: {brightness}, saturation: {saturation})...")
    
    adjusted_colors = {}
    for key, color in theme_colors.items():
        adjusted_color = color
        
        if brightness != 1.0:
            adjusted_color = adjust_color_brightness(adjusted_color, brightness)
        
        if saturation != 1.0:
            adjusted_color = adjust_color_saturation(adjusted_color, saturation)
            
        adjusted_colors[key] = adjusted_color
    
    return adjusted_colors


def extract_colors_using_screenshot(
    url: str, 
    output_dir: str, 
    prefer_light: bool, 
    save_screenshot: bool
) -> Dict[str, str]:
    """Extract colors using screenshot-based method.

    Args:
        url: Website URL
        output_dir: Output directory
        prefer_light: Whether to prefer light theme
        save_screenshot: Whether to save the screenshot

    Returns:
        Dictionary of theme colors
    """
    print("Using screenshot-based color extraction...")
    
    screenshots_dir = os.path.join(output_dir, "screenshots") if save_screenshot else None
    screenshot_extractor = ScreenshotExtractor(screenshots_dir=screenshots_dir)
    
    return screenshot_extractor.extract_theme_colors(
        url,
        prefer_light=prefer_light,
        save_screenshot=save_screenshot
    )


def generate_previews(
    theme: Dict[str, Any], 
    output_dir: str, 
    generate_png: bool
) -> Tuple[str, Optional[str]]:
    """Generate preview images for the theme.

    Args:
        theme: Theme configuration dictionary
        output_dir: Output directory
        generate_png: Whether to generate PNG previews

    Returns:
        Tuple of (svg_path, png_path or None)
    """
    print(f"Generating {'SVG and PNG' if generate_png else 'SVG'} preview...")
    preview_generator = ThemePreviewGenerator()
    svg_path, png_path = preview_generator.save_previews(theme, output_dir, generate_png=generate_png)
    
    print(f"Preview generated: {svg_path}")
    if png_path:
        print(f"PNG preview generated: {png_path}")
        
    return svg_path, png_path


def generate_all_theme_previews(output_dir: str, generate_png: bool) -> None:
    """Generate previews for all themes in the output directory.

    Args:
        output_dir: Output directory containing theme files
        generate_png: Whether to generate PNG previews
    """
    print(f"Generating {'SVG and PNG' if generate_png else 'SVG'} previews for all themes...")
    preview_generator = ThemePreviewGenerator()
    preview_paths_list = preview_generator.generate_previews_for_directory(
        output_dir, 
        generate_png=generate_png
    )
    
    svg_count = len(preview_paths_list)
    png_count = sum(1 for _, png_path in preview_paths_list if png_path)
    
    preview_dir = os.path.join(output_dir, 'previews')
    if generate_png:
        print(f"Generated {svg_count} SVG and {png_count} PNG previews in {preview_dir}")
    else:
        print(f"Generated {svg_count} SVG previews in {preview_dir}")


def print_theme_details(
    theme_path: str, 
    background_image_path: Optional[str], 
    preview_paths: Optional[Tuple[str, Optional[str]]]
) -> None:
    """Print theme details and installation instructions.

    Args:
        theme_path: Path to saved theme file
        background_image_path: Path to background image or None
        preview_paths: Tuple of (svg_path, png_path) or None
    """
    print(f"Theme generated successfully: {theme_path}")
    print(f"Install with:")
    print(f"  1. cp {theme_path} ~/.warp/themes/")
    
    if background_image_path:
        print(f"  2. cp {background_image_path} ~/.warp/themes/")
        
    if preview_paths:
        svg_path, png_path = preview_paths
        print(f"View SVG preview: {svg_path}")
        if png_path:
            print(f"View PNG preview: {png_path}")


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
    
    fetcher = Fetcher()
    color_extractor = ColorExtractor()
    theme_generator = ThemeGenerator()
    
    if not fetcher.validate_url(parsed_args.url):
        print(f"Error: Invalid URL format: {parsed_args.url}")
        print("Please provide a valid URL starting with http:// or https://")
        return 1
    
    output_dir = initialize_output_directory(parsed_args.output)
    
    theme_name = determine_theme_name(parsed_args.name, parsed_args.url)
    
    if parsed_args.use_screenshot:
        theme_colors = extract_colors_using_screenshot(
            parsed_args.url,
            output_dir,
            parsed_args.prefer_light,
            parsed_args.save_screenshot
        )
    else:
        print("Using traditional color extraction...")
        resources = fetch_website_resources(
            fetcher, 
            parsed_args.url, 
            parsed_args.max_css, 
            parsed_args.max_images
        )
        
        if not resources.get('html'):
            return 1
        
        print("Extracting colors...")
        theme_colors = extract_theme_colors(
            color_extractor, 
            resources, 
            parsed_args.prefer_light
        )
    
    theme_colors = apply_color_adjustments(
        theme_colors,
        parsed_args.brightness,
        parsed_args.saturation
    )
    
    accent_color = theme_colors['accent']
    background_color = theme_colors['background']
    foreground_color = theme_colors['foreground']
    
    print(f"Selected colors:")
    print(f"  Accent: {accent_color}")
    print(f"  Background: {background_color}")
    print(f"  Foreground: {foreground_color}")
    
    terminal_colors = color_extractor.generate_terminal_colors(accent_color, background_color)
    
    background_image_path = None
    if parsed_args.extract_background and not parsed_args.use_screenshot:
        print("Extracting background image...")
        resources = resources if 'resources' in locals() else fetch_website_resources(
            fetcher, 
            parsed_args.url, 
            parsed_args.max_css, 
            parsed_args.max_images
        )
        
        background_image_path = extract_background_image(
            resources, 
            theme_name, 
            output_dir
        )
        if background_image_path:
            print(f"Background image extracted: {os.path.basename(background_image_path)}")
    
    theme = theme_generator.create_theme(
        accent=accent_color,
        background=background_color,
        foreground=foreground_color,
        terminal_colors=terminal_colors,
        name=theme_name,
        background_image=os.path.basename(background_image_path) if background_image_path else None,
        opacity=parsed_args.background_opacity
    )
    
    theme_path = theme_generator.save_theme(theme, output_dir)
    
    preview_paths = None
    if parsed_args.generate_preview:
        preview_paths = generate_previews(theme, output_dir, parsed_args.png)
    
    if parsed_args.generate_all_previews:
        generate_all_theme_previews(output_dir, parsed_args.png)
    
    print_theme_details(theme_path, background_image_path, preview_paths)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
