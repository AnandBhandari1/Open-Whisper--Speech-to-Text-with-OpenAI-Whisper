#!/bin/bash

echo "============================================"
echo "   FastSimple - Setup Script"
echo "============================================"
echo ""
echo "Simple speech-to-text with OpenAI Whisper"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track setup status
ISSUES=0

echo "🔍 Step 1: Checking system requirements..."
echo ""

# Check if uv is installed
echo -n "Checking for uv package manager... "
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version 2>&1 | head -n 1)
    echo -e "${GREEN}✓ Found${NC} ($UV_VERSION)"
else
    echo -e "${RED}✗ Not found${NC}"
    echo ""
    echo -e "${YELLOW}Installing uv package manager...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Source the shell config to get uv in PATH
    if [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
    fi

    # Check again
    if command -v uv &> /dev/null; then
        echo -e "${GREEN}✓ uv installed successfully${NC}"
    else
        echo -e "${RED}✗ Failed to install uv${NC}"
        echo "Please install manually: https://docs.astral.sh/uv/getting-started/installation/"
        ISSUES=$((ISSUES + 1))
    fi
fi

# Check for ffmpeg (required by openai-whisper)
echo -n "Checking for ffmpeg... "
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -n 1 | cut -d' ' -f3)
    echo -e "${GREEN}✓ Found${NC} ($FFMPEG_VERSION)"
else
    echo -e "${YELLOW}⚠ Not found${NC}"
    echo ""
    echo -e "${YELLOW}ffmpeg is required for audio processing.${NC}"
    echo "Install with: sudo apt install ffmpeg"
    ISSUES=$((ISSUES + 1))
fi

# Check for CUDA (optional, for GPU acceleration)
echo -n "Checking for CUDA/GPU support... "
if command -v nvidia-smi &> /dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -n 1)
    if [ -n "$GPU_NAME" ]; then
        echo -e "${GREEN}✓ Found${NC} ($GPU_NAME)"
    else
        echo -e "${YELLOW}⚠ nvidia-smi found but no GPU detected${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Not available${NC} (will use CPU mode)"
fi

# Check Python version
echo -n "Checking Python version... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
        echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"
    else
        echo -e "${RED}✗ $PYTHON_VERSION (requires >=3.10)${NC}"
        ISSUES=$((ISSUES + 1))
    fi
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    ISSUES=$((ISSUES + 1))
fi

echo ""
echo "============================================"

# Exit if critical issues found
if [ $ISSUES -gt 0 ]; then
    echo -e "${RED}⚠ Found $ISSUES critical issue(s)${NC}"
    echo "Please resolve the above issues before continuing."
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ All system requirements met!${NC}"
echo ""

# Install Python dependencies
echo "🔧 Step 2: Installing Python dependencies..."
echo ""
echo "This may take a few minutes (downloading Whisper models ~3GB)..."
echo ""

if uv sync; then
    echo ""
    echo -e "${GREEN}✓ Dependencies installed successfully!${NC}"
else
    echo ""
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    echo "Try running: uv sync --verbose"
    exit 1
fi

# Verify GPU availability with PyTorch
echo ""
echo "🔍 Step 3: Verifying GPU setup..."
echo ""

if uv run python -c "import torch; print(f'PyTorch version: {torch.__version__}'); cuda_available = torch.cuda.is_available(); print(f'CUDA available: {cuda_available}'); print(f'GPU: {torch.cuda.get_device_name(0)}' if cuda_available else 'CPU mode - No GPU detected')" 2>/dev/null; then
    echo ""
    echo -e "${GREEN}✓ PyTorch and GPU check complete${NC}"
else
    echo ""
    echo -e "${YELLOW}⚠ GPU check failed - will use CPU mode${NC}"
fi

# Success message
echo ""
echo "============================================"
echo -e "${GREEN}✓ Setup completed successfully!${NC}"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Run the app:  ${BLUE}./run.sh${NC}"
echo "  2. Press F8 or click 'Record' to start recording"
echo "  3. Speak, then press F8 again to transcribe"
echo ""
echo "Features:"
echo "  • Global F8 hotkey for recording"
echo "  • Real-time waveform visualization"
echo "  • Automatic text insertion at cursor"
echo "  • GPU acceleration (if available)"
echo ""
echo "For more info, see README.md"
echo ""
