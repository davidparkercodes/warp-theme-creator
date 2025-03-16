"""Theme generation module.

This module handles generating Warp terminal themes from extracted colors.
"""

import os
from typing import Dict, List, Optional, Any
import yaml


class ThemeGenerator:
    """Generate Warp terminal themes from extracted colors."""

    def __init__(self):
        """Initialize the theme generator."""
        self.template = {
            "accent": "#0087D7",
            "background": "#1E1E1E",
            "foreground": "#FFFFFF",
            "details": "darker",
            "terminal_colors": {
                "normal": {
                    "black": "#000000",
                    "red": "#FF5555",
                    "green": "#50FA7B",
                    "yellow": "#F1FA8C",
                    "blue": "#0087D7",
                    "magenta": "#FF79C6",
                    "cyan": "#8BE9FD",
                    "white": "#BFBFBF"
                },
                "bright": {
                    "black": "#4D4D4D",
                    "red": "#FF6E67",
                    "green": "#5AF78E",
                    "yellow": "#F4F99D",
                    "blue": "#6FC1FF",
                    "magenta": "#FF92D0",
                    "cyan": "#9AEDFE",
                    "white": "#FFFFFF"
                }
            }
        }
    
    def create_theme(self, 
                    accent: str, 
                    background: str, 
                    foreground: str, 
                    terminal_colors: Dict[str, str],
                    name: str = "Generated Theme", 
                    background_image: Optional[str] = None,
                    opacity: float = 1.0) -> Dict[str, Any]:
        """Create a Warp theme from the provided colors.

        Args:
            accent: Accent color as hex
            background: Background color as hex
            foreground: Foreground color as hex
            terminal_colors: Dictionary of terminal colors
            name: Name of the theme
            background_image: Optional path to background image
            opacity: Background opacity (0.0 to 1.0)

        Returns:
            Theme configuration as a dictionary
        """
        theme = self.template.copy()
        theme["accent"] = accent
        theme["background"] = background
        theme["foreground"] = foreground
        theme["name"] = name
        
        # Set terminal colors
        for color_type in ["normal", "bright"]:
            for color_name in theme["terminal_colors"][color_type]:
                if color_type == "normal" and color_name in terminal_colors:
                    theme["terminal_colors"][color_type][color_name] = terminal_colors[color_name]
                elif color_type == "bright" and f"bright_{color_name}" in terminal_colors:
                    theme["terminal_colors"][color_type][color_name] = terminal_colors[f"bright_{color_name}"]
        
        # Add background image if provided
        if background_image:
            theme["background_image"] = {
                "path": background_image,
                "opacity": opacity
            }
        
        return theme
    
    def generate_yaml(self, theme: Dict[str, Any]) -> str:
        """Generate YAML string from theme dictionary.

        Args:
            theme: Theme configuration dictionary

        Returns:
            YAML string representing the theme
        """
        return yaml.dump(theme, sort_keys=False, default_flow_style=False)
    
    def save_theme(self, theme: Dict[str, Any], output_path: str) -> str:
        """Save theme to a YAML file.

        Args:
            theme: Theme configuration dictionary
            output_path: Directory path to save the theme

        Returns:
            Path to the saved theme file
        """
        # Create sanitized filename from theme name
        theme_name = theme.get("name", "generated_theme")
        filename = self._sanitize_filename(theme_name) + ".yaml"
        
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Full path to save the theme
        full_path = os.path.join(output_path, filename)
        
        # Write theme to file
        with open(full_path, 'w') as f:
            f.write(self.generate_yaml(theme))
        
        return full_path
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize a string to be used as a filename.

        Args:
            name: Original string

        Returns:
            Sanitized string
        """
        # Replace spaces with underscores and remove special characters
        sanitized = ''
        for char in name:
            if char.isalnum() or char in '_-':
                sanitized += char
            elif char.isspace():
                sanitized += '_'
        
        # Ensure it's not empty and doesn't start with a dash
        if not sanitized or sanitized.startswith('-'):
            sanitized = 'theme_' + sanitized
        
        return sanitized.lower()
    
    def validate_theme(self, theme: Dict[str, Any]) -> bool:
        """Validate if a theme has all required fields.

        Args:
            theme: Theme configuration dictionary

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["accent", "background", "foreground", "terminal_colors"]
        
        if not all(field in theme for field in required_fields):
            return False
        
        # Check terminal colors structure
        if "normal" not in theme["terminal_colors"] or "bright" not in theme["terminal_colors"]:
            return False
        
        required_colors = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
        
        for color_type in ["normal", "bright"]:
            if not all(color in theme["terminal_colors"][color_type] for color in required_colors):
                return False
        
        return True
