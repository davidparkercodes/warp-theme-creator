"""Utility functions for the Warp Theme Creator.

This module provides helper functions used across the application.
"""

from typing import Tuple
import re


def is_valid_hex_color(color: str) -> bool:
    """Check if a string is a valid hex color code.

    Args:
        color: String to check

    Returns:
        True if valid hex color, False otherwise
    """
    pattern = r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$'
    return bool(re.match(pattern, color))


def adjust_color_brightness(hex_color: str, factor: float) -> str:
    """Adjust the brightness of a hex color.

    Args:
        hex_color: Hex color code
        factor: Brightness factor (>1 brightens, <1 darkens)

    Returns:
        Adjusted hex color
    """
    hex_color = hex_color.lstrip('#')
    
    if len(hex_color) == 3:
        r = int(hex_color[0] + hex_color[0], 16)
        g = int(hex_color[1] + hex_color[1], 16)
        b = int(hex_color[2] + hex_color[2], 16)
    else:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    
    r = min(255, max(0, int(r * factor)))
    g = min(255, max(0, int(g * factor)))
    b = min(255, max(0, int(b * factor)))
    
    return f'#{r:02x}{g:02x}{b:02x}'


def adjust_color_saturation(hex_color: str, factor: float) -> str:
    """Adjust the saturation of a hex color.

    Args:
        hex_color: Hex color code
        factor: Saturation factor (>1 increases, <1 decreases)

    Returns:
        Adjusted hex color
    """
    hex_color = hex_color.lstrip('#')
    
    if len(hex_color) == 3:
        r = int(hex_color[0] + hex_color[0], 16)
        g = int(hex_color[1] + hex_color[1], 16)
        b = int(hex_color[2] + hex_color[2], 16)
    else:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    
    h, s, l = rgb_to_hsl(r, g, b)
    
    s = min(1.0, max(0.0, s * factor))
    
    r, g, b = hsl_to_rgb(h, s, l)
    
    return f'#{r:02x}{g:02x}{b:02x}'


def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert RGB to HSL color space.

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        HSL tuple (h: 0-360, s: 0-1, l: 0-1)
    """
    r /= 255
    g /= 255
    b /= 255
    
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    delta = cmax - cmin
    
    h = 0
    if delta != 0:
        if cmax == r:
            h = ((g - b) / delta) % 6
        elif cmax == g:
            h = (b - r) / delta + 2
        else:
            h = (r - g) / delta + 4
    
    h = round(h * 60)
    if h < 0:
        h += 360
    
    l = (cmax + cmin) / 2
    
    s = 0
    if delta != 0:
        s = delta / (1 - abs(2 * l - 1))
    
    return h, s, l


def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[int, int, int]:
    """Convert HSL to RGB color space.

    Args:
        h: Hue (0-360)
        s: Saturation (0-1)
        l: Lightness (0-1)

    Returns:
        RGB tuple (r: 0-255, g: 0-255, b: 0-255)
    """
    def hue_to_rgb(p, q, t):
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1/6:
            return p + (q - p) * 6 * t
        if t < 1/2:
            return q
        if t < 2/3:
            return p + (q - p) * (2/3 - t) * 6
        return p
    
    h /= 360
    
    if s == 0:
        r = g = b = l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)
    
    r = round(r * 255)
    g = round(g * 255)
    b = round(b * 255)
    
    return r, g, b
