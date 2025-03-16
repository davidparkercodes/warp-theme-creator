# Warp Theme Creator

A Python tool to automatically generate Warp terminal themes from website color schemes.

## Overview

Warp Theme Creator extracts colors from websites and generates custom themes for the [Warp Terminal](https://www.warp.dev/). Simply provide a URL, and the tool will analyze the website's color palette to create a personalized theme.

## Features

- Extract dominant colors from websites (both CSS and images)
- Generate Warp-compatible theme files in YAML format
- Support for background images extraction
- Customizable color adjustments
- Preview generation for created themes
- Simple command-line interface

## Installation

```bash
# Clone the repository
git clone https://github.com/davidparkercodes/warp-theme-creator.git
cd warp-theme-creator

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Usage

```bash
# Basic usage with a URL
warp-theme-creator https://example.com

# Customize theme name
warp-theme-creator https://example.com --name "My Custom Theme"

# Adjust colors
warp-theme-creator https://example.com --brightness 1.2 --saturation 0.9

# Extract background image
warp-theme-creator https://example.com --extract-background

# Save to specific location
warp-theme-creator https://example.com --output ~/warp/themes/
```

## Development

Please refer to the [Development Plan](DEVELOPMENT_PLAN.md) for more information about the project structure and roadmap.

### Development Workflow

1. Create a feature branch for your work
2. Make atomic, well-described commits
3. Create a pull request for code review
4. Ensure all tests pass before submitting your PR

For detailed contribution guidelines, please see [UPDATE_RULES.md](UPDATE_RULES.md).

## License

MIT