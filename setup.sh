#!/bin/bash
# Warp Theme Creator Setup Script

# Print colored output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Warp Theme Creator Setup ===${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    VENV_CREATED=true
else
    echo -e "${YELLOW}Virtual environment already exists.${NC}"
    VENV_CREATED=false
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Install package in development mode
echo -e "${YELLOW}Installing package in development mode...${NC}"
pip install -e .

# Create .envrc if it doesn't exist
if [ ! -f ".envrc" ]; then
    echo -e "${YELLOW}Creating .envrc file for direnv...${NC}"
    echo 'source venv/bin/activate' > .envrc
    
    # Check if direnv is installed
    if command -v direnv &> /dev/null; then
        direnv allow .
        echo -e "${GREEN}Direnv configuration created and allowed.${NC}"
    else
        echo -e "${YELLOW}Direnv not found. Install direnv to automatically activate the environment:${NC}"
        echo -e "  Homebrew: brew install direnv"
        echo -e "  Then add 'eval \"\$(direnv hook bash)\"' or 'eval \"\$(direnv hook zsh)\"' to your shell configuration."
    fi
else
    echo -e "${YELLOW}.envrc file already exists.${NC}"
fi

echo -e "${GREEN}Setup complete!${NC}"

if [ "$VENV_CREATED" = true ]; then
    echo -e "${YELLOW}Virtual environment has been created and activated.${NC}"
else
    echo -e "${YELLOW}Using existing virtual environment.${NC}"
fi

echo -e "${BLUE}=== Quick Start Guide ===${NC}"
echo -e "1. The virtual environment is ${GREEN}activated${NC}."
echo -e "2. Try running: ${GREEN}warp-theme-creator https://example.com${NC}"
echo -e "3. Check output in the ${GREEN}themes/${NC} directory."
echo -e "4. Next time you open this project, direnv will automatically activate the environment."
echo -e "5. To deactivate manually, run: ${GREEN}deactivate${NC}"