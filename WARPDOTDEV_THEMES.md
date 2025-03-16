# Warp Themes Reference

This directory contains a copy of the [Warp Terminal Themes](https://github.com/warpdotdev/themes) repository that serves as a reference for our theme generator application. The themes in this directory help us understand the structure and format of Warp themes.

## Structure

The `warpdotdev-themes` directory is organized into several categories:

- **base16**: Themes following the [base16](https://github.com/chriskempson/base16) specification, providing a carefully chosen syntax highlighting using a base of sixteen colors.
- **standard**: Popular themes from other tools, including Solarized, Dracula, and others.
- **special_edition**: Themes with special background images.
- **warp_bundled**: Themes that ship directly with Warp.

## Theme Format

Warp themes are YAML files with the following structure:

```yaml
accent: "#0087D7"          # Accent color for UI elements
background: "#1E1E1E"      # Terminal background color
foreground: "#FFFFFF"      # Terminal text color
details: "darker"          # UI styling (darker or lighter)
terminal_colors:           # ANSI terminal colors
  normal:
    black: "#000000"
    red: "#FF5555"
    green: "#50FA7B"
    yellow: "#F1FA8C"
    blue: "#0087D7"
    magenta: "#FF79C6"
    cyan: "#8BE9FD"
    white: "#BFBFBF"
  bright:
    black: "#4D4D4D"
    red: "#FF6E67"
    green: "#5AF78E"
    yellow: "#F4F99D"
    blue: "#6FC1FF"
    magenta: "#FF92D0"
    cyan: "#9AEDFE"
    white: "#FFFFFF"
```

## Custom Background Images

Warp supports background images in themes. To use a background image, add it to your theme YAML:

```yaml
background_image:
  path: "path/to/image.jpg"  # Path relative to ~/.warp/themes/ or absolute path
  opacity: 0.7              # Optional: opacity value (0.0 to 1.0)
```

The path can be:
- A relative path from `~/.warp/themes/` (e.g., `"my_image.jpg"`)
- An absolute path (e.g., `"/Users/username/Pictures/background.jpg"`)

## Using in Our Project

This reference repository helps us:

1. Understand the theme format structure
2. Analyze color schemes and relationships
3. Test our theme generator against existing themes
4. Use the SVG preview generation script as a reference

## Theme Preview Generation

To generate theme previews, the original repository includes a Python script:

```bash
python3 ./warpdotdev-themes/scripts/gen_theme_previews.py standard
```

This can be helpful for testing our generated themes.