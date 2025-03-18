#!/bin/bash
# Warp Theme Creator Development Helper Script

# Print colored output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Ensure the virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}Virtual environment not activated. Activating now...${NC}"
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo -e "${RED}Virtual environment not found. Run ./setup.sh first.${NC}"
        exit 1
    fi
fi

# Parse command line arguments
if [ $# -eq 0 ]; then
    echo -e "${BLUE}=== Warp Theme Creator Development Helper ===${NC}"
    echo -e "Usage: ./dev.sh [command]"
    echo -e ""
    echo -e "Available commands:"
    echo -e "  ${GREEN}test${NC}             - Run all tests"
    echo -e "  ${GREEN}lint${NC}             - Run code linting and formatting checks"
    echo -e "  ${GREEN}format${NC}           - Format code with black"
    echo -e "  ${GREEN}coverage${NC}         - Run tests with coverage report"
    echo -e "  ${GREEN}clean${NC}            - Clean up cache and build files"
    echo -e "  ${GREEN}run${NC} [url]        - Run the tool with the specified URL (default: example.com)"
    echo -e "  ${GREEN}screenshot${NC} [url] - Run with screenshot-based extraction (default: example.com)"
    echo -e "  ${GREEN}install-deps${NC}     - Install/update dependencies from requirements.txt"
    exit 0
fi

command=$1
shift

case $command in
    test)
        echo -e "${BLUE}Running tests...${NC}"
        python -m pytest
        ;;
    lint)
        echo -e "${BLUE}Running linters...${NC}"
        echo -e "${YELLOW}Running flake8...${NC}"
        python -m flake8 warp_theme_creator
        echo -e "${YELLOW}Running mypy...${NC}"
        python -m mypy warp_theme_creator
        ;;
    format)
        echo -e "${BLUE}Formatting code with black...${NC}"
        python -m black warp_theme_creator
        ;;
    coverage)
        echo -e "${BLUE}Running tests with coverage...${NC}"
        python -m pytest --cov=warp_theme_creator --cov-report=term-missing
        ;;
    clean)
        echo -e "${BLUE}Cleaning up cache and build files...${NC}"
        rm -rf __pycache__ .pytest_cache .coverage build dist *.egg-info
        find . -name "__pycache__" -type d -exec rm -rf {} +
        find . -name "*.pyc" -delete
        echo -e "${GREEN}Clean complete!${NC}"
        ;;
    run)
        url=${1:-"https://example.com"}
        shift # Remove the URL from the argument list
        echo -e "${BLUE}Running warp-theme-creator with URL: ${url} $@${NC}"
        python -m warp_theme_creator.main "${url}" "$@"
        echo -e "${GREEN}Theme generated in themes/ directory.${NC}"
        ;;
    screenshot)
        url=${1:-"https://example.com"}
        shift # Remove the URL from the argument list
        echo -e "${BLUE}Running warp-theme-creator with screenshot-based extraction for URL: ${url} $@${NC}"
        python -m warp_theme_creator.main "${url}" --use-screenshot --save-screenshot "$@"
        echo -e "${GREEN}Theme generated in themes/ directory.${NC}"
        ;;
    install-deps)
        echo -e "${BLUE}Installing dependencies from requirements.txt...${NC}"
        pip install -r requirements.txt
        echo -e "${GREEN}Dependencies installed.${NC}"
        ;;
    *)
        echo -e "${RED}Unknown command: ${command}${NC}"
        echo -e "Run ./dev.sh without arguments to see available commands."
        exit 1
        ;;
esac