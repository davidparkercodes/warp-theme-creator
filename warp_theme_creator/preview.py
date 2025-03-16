"""SVG Preview generation module.

This module generates SVG and PNG preview images for Warp terminal themes.
"""

import os
from typing import Dict, Any, List, Optional, Tuple, Union
import yaml
import io

try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False


# Enhanced SVG template for theme preview - showcases all terminal colors in practical contexts
DEFAULT_SVG_TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 600">
  <!-- Terminal Window with Warp-like styling -->
  <defs>
    <linearGradient id="accentGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0.2"/>
    </linearGradient>
    <filter id="dropShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
      <feOffset dx="2" dy="2" result="offsetblur"/>
      <feComponentTransfer>
        <feFuncA type="linear" slope="0.2"/>
      </feComponentTransfer>
      <feMerge>
        <feMergeNode/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Main Terminal Window -->
  <rect width="1000" height="600" fill="{background}" rx="10" ry="10"/>
  
  <!-- Window Controls Bar -->
  <rect x="0" y="0" width="1000" height="30" fill="#111111" rx="10" ry="10"/>
  <text x="20" y="20" fill="{brwhite}" font-family="monospace" font-size="14">Warp Terminal - {name}</text>
  <circle cx="950" cy="15" r="7" fill="#FF5F56"/>
  <circle cx="925" cy="15" r="7" fill="#FFBD2E"/>
  <circle cx="900" cy="15" r="7" fill="#27C93F"/>
  
  <!-- Accent color indicator - vertical bar on left side -->
  <rect x="0" y="30" width="4" height="570" fill="{accent}"/>
  
  <!-- Top Command with accent color in prompt -->
  <text x="20" y="55" fill="{foreground}" font-family="monospace" font-size="14">
    <tspan fill="{accent}">➜</tspan>  <tspan fill="{green}">~/projects</tspan> <tspan fill="{brblue}">git:(</tspan><tspan fill="{brred}">feature/enhanced-previews</tspan><tspan fill="{brblue}">)</tspan> 
  </text>
  
  <!-- Standard Command Execution Section -->
  <text x="20" y="80" fill="{foreground}" font-family="monospace" font-size="14">
    $ warp-theme-creator https://example.com --generate-preview --all-colors
  </text>
  
  <text x="20" y="105" fill="{magenta}" font-family="monospace" font-size="14">
    Fetching HTML content from https://example.com...
  </text>
  
  <text x="20" y="130" fill="{magenta}" font-family="monospace" font-size="14">
    Extracting colors...
  </text>

  <!-- Success Message -->
  <text x="20" y="155" fill="{green}" font-family="monospace" font-size="14">
    ✓ Theme generated successfully!
  </text>
  
  <!-- Warning Message Example -->
  <text x="20" y="180" fill="{yellow}" font-family="monospace" font-size="14">
    ⚠ Warning: Some images could not be processed, using default fallbacks.
  </text>

  <!-- Error Message Example -->
  <text x="20" y="205" fill="{red}" font-family="monospace" font-size="14">
    ✗ Error: Unable to extract background image. Using solid background instead.
  </text>

  <!-- Debug Message Example -->
  <text x="20" y="230" fill="{cyan}" font-family="monospace" font-size="14">
    [DEBUG] Processing 5 CSS files and 3 images for color extraction...
  </text>
  
  <!-- Command Result Section (showing the theme colors) -->
  <text x="20" y="265" fill="{foreground}" font-family="monospace" font-size="14">
    Selected colors:
  </text>
  
  <text x="40" y="290" fill="{foreground}" font-family="monospace" font-size="14">
    Accent: <tspan fill="{accent}">████████</tspan> {accent}
  </text>
  
  <text x="40" y="315" fill="{foreground}" font-family="monospace" font-size="14">
    Background: <tspan fill="{background}" stroke="{foreground}" stroke-width="0.5">████████</tspan> {background}
  </text>
  
  <text x="40" y="340" fill="{foreground}" font-family="monospace" font-size="14">
    Foreground: <tspan fill="{foreground}">████████</tspan> {foreground}
  </text>
  
  <!-- Terminal Colors Display Section -->
  <text x="20" y="375" fill="{foreground}" font-family="monospace" font-size="16" font-weight="bold">
    Terminal Colors:
  </text>
  
  <!-- Normal Colors -->
  <g transform="translate(40, 390)">
    <rect x="0" y="0" width="30" height="30" fill="{black}" stroke="{foreground}" stroke-width="0.5"/>
    <text x="40" y="20" fill="{foreground}" font-family="monospace" font-size="14">Black</text>
    
    <rect x="150" y="0" width="30" height="30" fill="{red}"/>
    <text x="190" y="20" fill="{foreground}" font-family="monospace" font-size="14">Red</text>
    
    <rect x="300" y="0" width="30" height="30" fill="{green}"/>
    <text x="340" y="20" fill="{foreground}" font-family="monospace" font-size="14">Green</text>
    
    <rect x="450" y="0" width="30" height="30" fill="{yellow}"/>
    <text x="490" y="20" fill="{foreground}" font-family="monospace" font-size="14">Yellow</text>
  </g>
  
  <g transform="translate(40, 430)">
    <rect x="0" y="0" width="30" height="30" fill="{blue}"/>
    <text x="40" y="20" fill="{foreground}" font-family="monospace" font-size="14">Blue</text>
    
    <rect x="150" y="0" width="30" height="30" fill="{magenta}"/>
    <text x="190" y="20" fill="{foreground}" font-family="monospace" font-size="14">Magenta</text>
    
    <rect x="300" y="0" width="30" height="30" fill="{cyan}"/>
    <text x="340" y="20" fill="{foreground}" font-family="monospace" font-size="14">Cyan</text>
    
    <rect x="450" y="0" width="30" height="30" fill="{white}"/>
    <text x="490" y="20" fill="{foreground}" font-family="monospace" font-size="14">White</text>
  </g>
  
  <!-- Bright Colors -->
  <g transform="translate(40, 480)">
    <rect x="0" y="0" width="30" height="30" fill="{brblack}"/>
    <text x="40" y="20" fill="{foreground}" font-family="monospace" font-size="14">Bright Black</text>
    
    <rect x="150" y="0" width="30" height="30" fill="{brred}"/>
    <text x="190" y="20" fill="{foreground}" font-family="monospace" font-size="14">Bright Red</text>
    
    <rect x="300" y="0" width="30" height="30" fill="{brgreen}"/>
    <text x="340" y="20" fill="{foreground}" font-family="monospace" font-size="14">Bright Green</text>
    
    <rect x="450" y="0" width="30" height="30" fill="{bryellow}"/>
    <text x="490" y="20" fill="{foreground}" font-family="monospace" font-size="14">Bright Yellow</text>
  </g>
  
  <g transform="translate(40, 520)">
    <rect x="0" y="0" width="30" height="30" fill="{brblue}"/>
    <text x="40" y="20" fill="{foreground}" font-family="monospace" font-size="14">Bright Blue</text>
    
    <rect x="150" y="0" width="30" height="30" fill="{brmagenta}"/>
    <text x="190" y="20" fill="{foreground}" font-family="monospace" font-size="14">Bright Magenta</text>
    
    <rect x="300" y="0" width="30" height="30" fill="{brcyan}"/>
    <text x="340" y="20" fill="{foreground}" font-family="monospace" font-size="14">Bright Cyan</text>
    
    <rect x="450" y="0" width="30" height="30" fill="{brwhite}"/>
    <text x="490" y="20" fill="{foreground}" font-family="monospace" font-size="14">Bright White</text>
  </g>
  
  <!-- Application examples section - right side panel -->
  <rect x="600" y="265" width="380" height="285" fill="{background}" stroke="{accent}" stroke-width="2" rx="5" ry="5"/>
  
  <!-- Terminal Application Examples -->
  <text x="610" y="285" fill="{brwhite}" font-family="monospace" font-size="14" font-weight="bold">Terminal in Action:</text>
  
  <!-- Code Example -->
  <text x="610" y="310" fill="{foreground}" font-family="monospace" font-size="13">
    <tspan fill="{blue}">def</tspan> <tspan fill="{green}">extract_colors</tspan><tspan fill="{foreground}">(url):</tspan>
  </text>
  <text x="630" y="330" fill="{foreground}" font-family="monospace" font-size="13">
    <tspan fill="{red}">try</tspan><tspan fill="{foreground}">:</tspan>
  </text>
  <text x="650" y="350" fill="{foreground}" font-family="monospace" font-size="13">
    <tspan fill="{foreground}">response = requests.</tspan><tspan fill="{cyan}">get</tspan><tspan fill="{foreground}">(url)</tspan>
  </text>
  <text x="650" y="370" fill="{foreground}" font-family="monospace" font-size="13">
    <tspan fill="{magenta}">colors</tspan> <tspan fill="{foreground}">= analyze_content(response.text)</tspan>
  </text>
  <text x="650" y="390" fill="{foreground}" font-family="monospace" font-size="13">
    <tspan fill="{green}">print</tspan><tspan fill="{foreground}">(</tspan><tspan fill="{yellow}">"Found colors:"</tspan><tspan fill="{foreground}">, colors)</tspan>
  </text>
  <text x="650" y="410" fill="{foreground}" font-family="monospace" font-size="13">
    <tspan fill="{bryellow}">return</tspan> <tspan fill="{magenta}">colors</tspan>
  </text>
  <text x="630" y="430" fill="{foreground}" font-family="monospace" font-size="13">
    <tspan fill="{red}">except</tspan> <tspan fill="{brred}">Exception</tspan> <tspan fill="{red}">as</tspan> <tspan fill="{brred}">e</tspan><tspan fill="{foreground}">:</tspan>
  </text>
  <text x="650" y="450" fill="{foreground}" font-family="monospace" font-size="13">
    <tspan fill="{green}">print</tspan><tspan fill="{foreground}">(</tspan><tspan fill="{red}">f"Error: {e}"</tspan><tspan fill="{foreground}">)</tspan>
  </text>
  
  <!-- Search and Selection Example -->
  <rect x="610" y="470" width="360" height="25" fill="{background}" stroke="{accent}" stroke-width="1"/>
  <text x="620" y="487" fill="{foreground}" font-family="monospace" font-size="13">
    <tspan>Search: </tspan><tspan fill="{accent}">extract</tspan><tspan> (2 matches found)</tspan>
  </text>
  
  <!-- Selected Text Example -->
  <rect x="610" y="500" width="180" height="20" fill="{accent}" opacity="0.3"/>
  <text x="620" y="515" fill="{foreground}" font-family="monospace" font-size="13">Selected text example</text>
  
  <!-- Current Line Indicator -->
  <rect x="610" y="525" width="360" height="20" fill="{accent}" opacity="0.1"/>
  <text x="620" y="540" fill="{foreground}" font-family="monospace" font-size="13">Current line with accent color</text>
  
  <!-- Command Prompt -->
  <rect x="0" y="570" width="1000" height="2" fill="{accent}" opacity="0.5"/>
  <text x="20" y="590" fill="{foreground}" font-family="monospace" font-size="14">
    <tspan fill="{accent}">➜</tspan>  <tspan fill="{green}">~/projects</tspan> <tspan fill="{cyan}">|</tspan>
  </text>
  
  <!-- Blinking cursor with accent color -->
  <rect x="200" y="578" width="10" height="18" fill="{accent}" opacity="0.8"/>
</svg>'''


class ThemePreviewGenerator:
    """Generate SVG and PNG previews for Warp terminal themes."""

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
        
        # Add name for title
        color_dict["name"] = theme.get("name", "Generated Theme")
        
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
        
        # Set defaults for any missing colors
        default_colors = {
            "black": "#000000", "red": "#FF0000", "green": "#00FF00", "yellow": "#FFFF00",
            "blue": "#0000FF", "magenta": "#FF00FF", "cyan": "#00FFFF", "white": "#FFFFFF",
            "brblack": "#808080", "brred": "#FF8080", "brgreen": "#80FF80", "bryellow": "#FFFF80",
            "brblue": "#8080FF", "brmagenta": "#FF80FF", "brcyan": "#80FFFF", "brwhite": "#FFFFFF"
        }
        
        for color_name, default_value in default_colors.items():
            if color_name not in color_dict:
                color_dict[color_name] = default_value
        
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
    
    def svg_to_png(self, svg_content: str, width: int = 1000, height: int = 600) -> bytes:
        """Convert SVG content to PNG image data.
        
        Args:
            svg_content: SVG content string
            width: Width of the output PNG
            height: Height of the output PNG
            
        Returns:
            PNG image data as bytes
            
        Raises:
            ImportError: If cairosvg is not available
        """
        if not CAIROSVG_AVAILABLE:
            raise ImportError("The cairosvg library is required for PNG conversion. "
                             "Install it with: pip install cairosvg")
        
        png_data = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            write_to=None,
            output_width=width,
            output_height=height
        )
        
        return png_data
    
    def save_previews(self, theme: Dict[str, Any], output_path: str, 
                     generate_png: bool = True) -> Tuple[str, Optional[str]]:
        """Generate and save SVG and optionally PNG previews for a theme.
        
        Args:
            theme: Theme configuration dictionary
            output_path: Directory path to save the previews
            generate_png: Whether to also generate a PNG preview
            
        Returns:
            Tuple of (svg_path, png_path or None)
        """
        # Create sanitized filename from theme name
        theme_name = theme.get("name", "generated_theme")
        sanitized_name = ''.join(c for c in theme_name.lower() if c.isalnum() or c == '_')
        svg_filename = f"{sanitized_name}_preview.svg"
        png_filename = f"{sanitized_name}_preview.png"
        
        # Create previews directory if it doesn't exist
        previews_dir = os.path.join(output_path, "previews")
        os.makedirs(previews_dir, exist_ok=True)
        
        # Full paths to save the previews
        svg_path = os.path.join(previews_dir, svg_filename)
        png_path = os.path.join(previews_dir, png_filename) if generate_png else None
        
        # Generate SVG content
        svg_content = self.generate_svg(theme)
        
        # Write SVG to file
        with open(svg_path, 'w') as f:
            f.write(svg_content)
        
        # Generate and save PNG if requested
        if generate_png and CAIROSVG_AVAILABLE:
            try:
                png_data = self.svg_to_png(svg_content)
                with open(png_path, 'wb') as f:
                    f.write(png_data)
            except Exception as e:
                print(f"Error generating PNG preview for {theme_name}: {str(e)}")
                png_path = None
        elif generate_png and not CAIROSVG_AVAILABLE:
            print(f"Warning: Cannot generate PNG preview for {theme_name} - cairosvg is not available")
            png_path = None
        
        return svg_path, png_path
    
    def generate_previews_for_directory(self, themes_dir: str, 
                                       generate_png: bool = True) -> List[Tuple[str, Optional[str]]]:
        """Generate previews for all themes in a directory.
        
        Args:
            themes_dir: Directory containing theme files
            generate_png: Whether to also generate PNG previews
            
        Returns:
            List of tuples with (svg_path, png_path or None)
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
                
                # Generate and save previews
                preview_paths = self.save_previews(theme, themes_dir, generate_png)
                generated_previews.append(preview_paths)
                
            except Exception as e:
                print(f"Error generating previews for {theme_file}: {str(e)}")
        
        return generated_previews
        
    def save_preview(self, theme: Dict[str, Any], output_path: str) -> str:
        """Generate and save SVG preview for a theme (backward compatibility).
        
        Args:
            theme: Theme configuration dictionary
            output_path: Directory path to save the preview
            
        Returns:
            Path to the saved SVG file
        """
        svg_path, _ = self.save_previews(theme, output_path, generate_png=False)
        return svg_path