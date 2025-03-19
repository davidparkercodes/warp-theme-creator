#!/usr/bin/env python
"""Generate preview for the Matrix theme."""

import os
import yaml
from warp_theme_creator.preview import ThemePreviewGenerator

def main():
    """Generate Matrix theme preview."""
    # Path to the theme file
    theme_path = os.path.join(os.path.dirname(__file__), "themes", "matrix.yaml")
    output_dir = os.path.join(os.path.dirname(__file__), "themes")
    
    # Load the theme
    with open(theme_path, 'r') as f:
        theme = yaml.safe_load(f)
    
    # Create preview generator
    preview_generator = ThemePreviewGenerator()
    
    # Generate preview
    print("Generating Matrix theme preview...")
    svg_path, png_path = preview_generator.save_previews(theme, output_dir, generate_png=True)
    
    print(f"SVG Preview generated: {svg_path}")
    if png_path:
        print(f"PNG Preview generated: {png_path}")
    else:
        print("PNG preview could not be generated. You may need to install cairosvg.")

if __name__ == "__main__":
    main()