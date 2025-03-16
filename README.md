# Warp Theme Creator

Generate custom themes for the Warp terminal by extracting colors from websites.

## Overview

Warp Theme Creator is a command-line tool that creates custom themes for the Warp terminal. It works by analyzing the colors used on websites and generating a theme file that can be used with Warp.

## Features

- Extract colors from website CSS and images
- Generate YAML theme files compatible with Warp terminal
- Customize theme name and output location
- Adjust color brightness and saturation
- Optional background image extraction (coming soon)

## Installation

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/davidparkercodes/warp-theme-creator.git
   cd warp-theme-creator
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   # venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install in development mode:
   ```bash
   pip install -e .
   ```

### Regular Installation

Once the package is published to PyPI (coming soon):
```bash
pip install warp-theme-creator
```

## Usage

### Basic Usage

```bash
# Using the module directly
python -m warp_theme_creator.main https://example.com

# Or using the console script (if installed)
warp-theme-creator https://example.com
```

### Options

```bash
# Custom theme name
warp-theme-creator https://example.com --name "My Custom Theme"

# Custom output directory
warp-theme-creator https://example.com --output ~/warp-themes

# Adjust color brightness and saturation
warp-theme-creator https://example.com --brightness 1.2 --saturation 0.9
```

### Installing Themes in Warp

After generating a theme, copy it to Warp's themes directory:
```bash
cp themes/example.yaml ~/.warp/themes/
```

Then select the theme in Warp's settings.

## Development

### Running Tests

```bash
pytest
```

### Code Formatting and Linting

```bash
black warp_theme_creator
flake8 warp_theme_creator
mypy warp_theme_creator
```

## License

MIT

## Credits

Created by David Parker