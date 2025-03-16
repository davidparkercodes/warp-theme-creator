#!/usr/bin/env python3
"""Test script for the enhanced SVG preview generator."""

import os
import sys
import yaml

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from warp_theme_creator.preview import ThemePreviewGenerator


def test_enhanced_preview():
    """Test the enhanced SVG preview generator with an existing theme."""
    # Locate the themes directory
    themes_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "themes")
    
    # Find the first theme file
    theme_files = [f for f in os.listdir(themes_dir) 
                   if f.endswith(('.yaml', '.yml')) and os.path.isfile(os.path.join(themes_dir, f))]
    
    if not theme_files:
        print("No theme files found in themes directory.")
        return 1
    
    theme_file = theme_files[0]
    theme_path = os.path.join(themes_dir, theme_file)
    
    print(f"Testing enhanced preview generator with theme: {theme_file}")
    
    # Load the theme
    with open(theme_path, 'r') as f:
        theme = yaml.safe_load(f)
    
    # Generate the preview
    preview_generator = ThemePreviewGenerator()
    output_path = preview_generator.save_preview(theme, themes_dir)
    
    print(f"Preview generated: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(test_enhanced_preview())