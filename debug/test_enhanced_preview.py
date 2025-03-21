#\!/usr/bin/env python
"""
Debug script to test the enhanced preview generation with PNG output.

Usage:
  python test_enhanced_preview.py [--png]
"""

import os
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from warp_theme_creator.preview import ThemePreviewGenerator

def main():
    """Main function to generate and test the preview."""
    generate_png = "--png" in sys.argv
    
    repo_root = Path(__file__).parent.parent
    themes_dir = repo_root / "themes"
    
    if not themes_dir.exists():
        print(f"Error: Themes directory not found at {themes_dir}")
        return 1
    
    theme_file = themes_dir / "test_theme.yaml"
    if not theme_file.exists():
        theme_files = list(themes_dir.glob("*.yaml"))
        if not theme_files:
            print(f"Error: No theme files found in {themes_dir}")
            return 1
        theme_file = theme_files[0]
    
    with open(theme_file, 'r') as f:
        theme = yaml.safe_load(f)
    
    print(f"Generating preview for theme: {theme.get('name', 'Unknown')}")
    print(f"Accent color: {theme.get('accent', 'Unknown')}")
    print(f"Background: {theme.get('background', 'Unknown')}")
    print(f"Foreground: {theme.get('foreground', 'Unknown')}")
    
    preview_generator = ThemePreviewGenerator()
    
    output_dir = repo_root / "themes"
    
    svg_path, png_path = preview_generator.save_previews(theme, output_dir, generate_png=generate_png)
    
    print(f"\nSVG preview generated at: {svg_path}")
    if generate_png and png_path:
        print(f"PNG preview generated at: {png_path}")
    elif generate_png and not png_path:
        print("PNG generation failed. Make sure cairosvg is installed.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
