"""SVG Preview generation module.

This module generates SVG preview images for Warp terminal themes.
"""

import os
from typing import Dict, Any, List, Optional
import yaml


# SVG template for theme preview - styled more like Warp terminal
DEFAULT_SVG_TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450">
  <!-- Terminal Window with Warp-like styling -->
  <defs>
    <linearGradient id="accentGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0.2"/>
    </linearGradient>
  </defs>

  <!-- Main Terminal Window -->
  <rect width="800" height="450" fill="{background}" rx="10" ry="10"/>
  
  <!-- Window Controls Bar -->
  <rect x="0" y="0" width="800" height="30" fill="#111111" rx="10" ry="10"/>
  <circle cx="20" cy="15" r="7" fill="#FF5F56"/>
  <circle cx="45" cy="15" r="7" fill="#FFBD2E"/>
  <circle cx="70" cy="15" r="7" fill="#27C93F"/>
  
  <!-- Accent color indicator - vertical bar on left side -->
  <rect x="0" y="30" width="4" height="420" fill="{accent}"/>
  
  <!-- Top Command with accent color in prompt -->
  <text x="20" y="60" fill="{foreground}" font-family="monospace" font-size="14">
    <tspan fill="{accent}">➜</tspan>  <tspan fill="{green}">~/project</tspan> <tspan fill="{brblue}">git:(</tspan><tspan fill="{brred}">feature/enhanced-svg-preview</tspan><tspan fill="{brblue}">)</tspan> 
  </text>
  
  <!-- Commands and outputs -->
  <text x="20" y="90" fill="{foreground}" font-family="monospace" font-size="14">
    $ warp-theme-creator https://example.com --generate-preview
  </text>
  
  <text x="20" y="120" fill="{magenta}" font-family="monospace" font-size="14">
    Fetching HTML content from https://example.com...
  </text>
  
  <text x="20" y="150" fill="{magenta}" font-family="monospace" font-size="14">
    Extracting colors...
  </text>
  
  <text x="20" y="180" fill="{foreground}" font-family="monospace" font-size="14">
    Selected colors:
  </text>
  
  <text x="40" y="210" fill="{foreground}" font-family="monospace" font-size="14">
    Accent: <tspan fill="{accent}">████████</tspan> {accent}
  </text>
  
  <text x="40" y="240" fill="{foreground}" font-family="monospace" font-size="14">
    Background: <tspan fill="{background}" stroke="{foreground}" stroke-width="0.5">████████</tspan> {background}
  </text>
  
  <text x="40" y="270" fill="{foreground}" font-family="monospace" font-size="14">
    Foreground: <tspan fill="{foreground}">████████</tspan> {foreground}
  </text>
  
  <!-- Terminal Colors Display -->
  <text x="20" y="310" fill="{foreground}" font-family="monospace" font-size="14">
    Terminal Colors:
  </text>
  
  <!-- Normal Colors -->
  <rect x="40" y="325" width="25" height="25" fill="{black}" stroke="{foreground}" stroke-width="0.5"/>
  <rect x="70" y="325" width="25" height="25" fill="{red}"/>
  <rect x="100" y="325" width="25" height="25" fill="{green}"/>
  <rect x="130" y="325" width="25" height="25" fill="{yellow}"/>
  <rect x="160" y="325" width="25" height="25" fill="{blue}"/>
  <rect x="190" y="325" width="25" height="25" fill="{magenta}"/>
  <rect x="220" y="325" width="25" height="25" fill="{cyan}"/>
  <rect x="250" y="325" width="25" height="25" fill="{white}"/>
  
  <!-- Bright Colors -->
  <rect x="40" y="355" width="25" height="25" fill="{brblack}"/>
  <rect x="70" y="355" width="25" height="25" fill="{brred}"/>
  <rect x="100" y="355" width="25" height="25" fill="{brgreen}"/>
  <rect x="130" y="355" width="25" height="25" fill="{bryellow}"/>
  <rect x="160" y="355" width="25" height="25" fill="{brblue}"/>
  <rect x="190" y="355" width="25" height="25" fill="{brmagenta}"/>
  <rect x="220" y="355" width="25" height="25" fill="{brcyan}"/>
  <rect x="250" y="355" width="25" height="25" fill="{brwhite}"/>
  
  <!-- Accent color representation in action - search highlight and selection -->
  <rect x="350" y="325" width="400" height="55" fill="{background}" stroke="{accent}" stroke-width="2" rx="5" ry="5"/>
  <text x="360" y="345" fill="{foreground}" font-family="monospace" font-size="14">Code with <tspan fill="{accent}">highlighted</tspan> search results</text>
  <text x="360" y="370" fill="{foreground}" font-family="monospace" font-size="14">Selected <tspan fill="{background}" style="background:{accent}"> text with accent background </tspan> color</text>
  
  <!-- Command Prompt -->
  <rect x="0" y="400" width="800" height="2" fill="{accent}" opacity="0.5"/>
  <text x="20" y="430" fill="{foreground}" font-family="monospace" font-size="14">
    <tspan fill="{accent}">➜</tspan>  <tspan fill="{green}">~/project</tspan> <tspan fill="{cyan}">|</tspan>
  </text>
  
  <!-- Blinking cursor with accent color -->
  <rect x="200" y="417" width="10" height="18" fill="{accent}" opacity="0.8"/>
</svg>'''


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