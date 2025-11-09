#!/bin/bash

echo "=========================================="
echo "   FastSimple - Speech to Text"
echo "=========================================="
echo ""
echo "✨ Features:"
echo "   • OpenAI Whisper (large-v3-turbo)"
echo "   • GPU acceleration (if available)"
echo "   • Real-time waveform visualization"
echo "   • Automatic text insertion"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed."
    echo "Please run ./setup.sh first"
    exit 1
fi

# Detect display server
SESSION_TYPE=$(echo "${XDG_SESSION_TYPE:-}" | tr '[:upper:]' '[:lower:]')
WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-}"

if [[ "$SESSION_TYPE" == "wayland" ]] || [[ -n "$WAYLAND_DISPLAY" ]]; then
    echo "🔧 Detected: Wayland session"
else
    echo "🔧 Detected: X11 session"
fi

echo ""

# Check GPU availability
echo "🔍 GPU Status:"
if uv run python -c "import torch; cuda = torch.cuda.is_available(); print(f'  GPU: {torch.cuda.get_device_name(0)}' if cuda else '  Mode: CPU (no GPU detected)')" 2>/dev/null; then
    :
else
    echo "  Checking..."
fi

echo ""
echo "🎯 Global Hotkey: F8"
echo "   Press F8 to start/stop recording"
echo "   Or use the Record button in the app"
echo ""
echo "ℹ️  The app will appear as a floating window"
echo "   • Drag to move it around"
echo "   • Watch waveform bars while recording"
echo "   • Text auto-inserts at cursor when done"
echo ""

# Optional: Set force CPU mode if FORCE_CPU env var is set
if [ "${FORCE_CPU:-0}" == "1" ]; then
    echo "⚠️  FORCE_CPU=1 - Running in CPU mode"
    echo ""
fi

echo "🚀 Starting FastSimple..."
echo ""
echo "=========================================="
echo ""

# Run the app
uv run python app.py
