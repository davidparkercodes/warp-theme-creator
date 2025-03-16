"""SVG Preview generation module.

This module generates SVG preview images for Warp terminal themes.
"""

import os
from typing import Dict, Any, List, Optional
import yaml


# SVG template for theme preview
DEFAULT_SVG_TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 145"><rect width="300" height="145" fill="{background}" class="Dynamic" rx="5"/><text x="15" y="15" fill="{foreground}" class="Dynamic" font-family="monospace" font-size=".6em">ls</text><text x="15" y="30" fill="{blue}" class="Dynamic" font-family="monospace" font-size=".6em">
dir
</text><text x="65" y="30" fill="{red}" class="Dynamic" font-family="monospace" font-size=".6em">
executable
</text><text x="175" y="30" fill="{foreground}" class="Dynamic" font-family="monospace" font-size=".6em">
file
</text><path stroke="{foreground}" d="M0 40h300" class="Dynamic" style="stroke-width:.2"/><text x="15" y="55" fill="{foreground}" class="Dynamic" font-family="monospace" font-size=".6em">bash ~/colors.sh</text><text x="15" y="70" fill="{foreground}" class="Dynamic" font-family="monospace" font-size=".6em">
normal:
</text><text x="55" y="70" fill="{black}" class="Dynamic" font-family="monospace" font-size=".6em">
black
</text><text x="85" y="70" fill="{red}" class="Dynamic" font-family="monospace" font-size=".6em">
red
</text><text x="105" y="70" fill="{green}" class="Dynamic" font-family="monospace" font-size=".6em">
green
</text><text x="135" y="70" fill="{yellow}" class="Dynamic" font-family="monospace" font-size=".6em">
yellow
</text><text x="170" y="70" fill="{blue}" class="Dynamic" font-family="monospace" font-size=".6em">
blue
</text><text x="195" y="70" fill="{magenta}" class="Dynamic" font-family="monospace" font-size=".6em">
magenta
</text><text x="235" y="70" fill="{cyan}" class="Dynamic" font-family="monospace" font-size=".6em">
cyan
</text><text x="260" y="70" fill="{white}" class="Dynamic" font-family="monospace" font-size=".6em">
white
</text><text x="15" y="85" fill="{foreground}" class="Dynamic" font-family="monospace" font-size=".6em">
bright:
</text><text x="55" y="85" fill="{brblack}" class="Dynamic" font-family="monospace" font-size=".6em">
black
</text><text x="85" y="85" fill="{brred}" class="Dynamic" font-family="monospace" font-size=".6em">
red
</text><text x="105" y="85" fill="{brgreen}" class="Dynamic" font-family="monospace" font-size=".6em">
green
</text><text x="135" y="85" fill="{bryellow}" class="Dynamic" font-family="monospace" font-size=".6em">
yellow
</text><text x="170" y="85" fill="{brblue}" class="Dynamic" font-family="monospace" font-size=".6em">
blue
</text><text x="195" y="85" fill="{brmagenta}" class="Dynamic" font-family="monospace" font-size=".6em">
magenta
</text><text x="235" y="85" fill="{brcyan}" class="Dynamic" font-family="monospace" font-size=".6em">
cyan
</text><text x="260" y="85" fill="{brwhite}" class="Dynamic" font-family="monospace" font-size=".6em">
white
</text><path stroke="{foreground}" d="M0 95h300" class="Dynamic" style="stroke-width:.2"/><text x="15" y="110" fill="{magenta}" class="Dynamic" font-family="monospace" font-size=".6em">
~/project
</text><text x="65" y="110" fill="{green}" class="Dynamic" font-family="monospace" font-size=".6em">
git(
    </text><text x="85" y="110" fill="{yellow}" class="Dynamic" font-family="monospace" font-size=".6em">
      main
    </text><text x="113" y="110" fill="{green}" class="Dynamic" font-family="monospace" font-size=".6em">
      )
</text><path stroke="{accent}" d="M15 120v10" class="Dynamic" style="stroke-width:2"/></svg>'''


class ThemePreviewGenerator:
    """Generate SVG previews for Warp terminal themes."""

    def __init__(self, svg_template: Optional[str] = None):
        """Initialize the theme preview generator.
        
        Args:
            svg_template: Optional custom SVG template
        """
        self.svg_template = svg_template or DEFAULT_SVG_TEMPLATE
    
    def generate_color_dict(self, theme: Dict[str, Any]) -> Dict[str, str]:
        """Convert theme data to a color dictionary for SVG template.
        
        Args:
            theme: Theme configuration dictionary
            
        Returns:
            Dictionary of all colors in a format ready for SVG template
        """
        color_dict = {}
        
        # Add accent, foreground, background
        color_dict["accent"] = theme.get("accent", "#0087D7")
        color_dict["foreground"] = theme.get("foreground", "#FFFFFF")
        color_dict["background"] = theme.get("background", "#1E1E1E")
        
        # Add normal colors
        normal_colors = theme.get("terminal_colors", {}).get("normal", {})
        for color_name, color_value in normal_colors.items():
            color_dict[color_name] = color_value
        
        # Add bright colors with "br" prefix
        bright_colors = theme.get("terminal_colors", {}).get("bright", {})
        for color_name, color_value in bright_colors.items():
            color_dict[f"br{color_name}"] = color_value
        
        return color_dict
    
    def generate_svg(self, theme: Dict[str, Any]) -> str:
        """Generate SVG preview from theme data.
        
        Args:
            theme: Theme configuration dictionary
            
        Returns:
            SVG content as a string
        """
        color_dict = self.generate_color_dict(theme)
        svg_content = self.svg_template
        
        # Replace placeholders with actual colors
        for key, value in color_dict.items():
            if isinstance(value, str):
                svg_content = svg_content.replace(f"{{{key}}}", value)
        
        return svg_content
    
    def save_preview(self, theme: Dict[str, Any], output_path: str) -> str:
        """Generate and save SVG preview for a theme.
        
        Args:
            theme: Theme configuration dictionary
            output_path: Directory path to save the preview
            
        Returns:
            Path to the saved SVG file
        """
        # Create sanitized filename from theme name
        theme_name = theme.get("name", "generated_theme")
        sanitized_name = ''.join(c for c in theme_name.lower() if c.isalnum() or c == '_')
        filename = f"{sanitized_name}_preview.svg"
        
        # Create previews directory if it doesn't exist
        previews_dir = os.path.join(output_path, "previews")
        os.makedirs(previews_dir, exist_ok=True)
        
        # Full path to save the preview
        full_path = os.path.join(previews_dir, filename)
        
        # Generate SVG content
        svg_content = self.generate_svg(theme)
        
        # Write SVG to file
        with open(full_path, 'w') as f:
            f.write(svg_content)
        
        return full_path
    
    def generate_previews_for_directory(self, themes_dir: str) -> List[str]:
        """Generate previews for all themes in a directory.
        
        Args:
            themes_dir: Directory containing theme files
            
        Returns:
            List of paths to generated preview files
        """
        # Get all theme files in directory
        theme_files = [f for f in os.listdir(themes_dir) 
                      if f.endswith(('.yaml', '.yml')) and os.path.isfile(os.path.join(themes_dir, f))]
        
        generated_previews = []
        
        for theme_file in theme_files:
            try:
                # Load theme file
                theme_path = os.path.join(themes_dir, theme_file)
                with open(theme_path, 'r') as f:
                    theme = yaml.safe_load(f)
                
                # Generate and save preview
                preview_path = self.save_preview(theme, themes_dir)
                generated_previews.append(preview_path)
                
            except Exception as e:
                print(f"Error generating preview for {theme_file}: {str(e)}")
        
        return generated_previews