# WhisperTalk 🎤

**Simple, Fast Speech-to-Text with OpenAI Whisper**

A lightweight, GPU-accelerated speech recognition application that transcribes your voice and automatically inserts text at your cursor position. Built with OpenAI Whisper for high-quality transcription.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/badge/uv-package%20manager-blue)](https://github.com/astral-sh/uv)

---

## ✨ Features

- 🎯 **Global Hotkey** - Press `F8` from anywhere to start/stop recording
- 🚀 **GPU Acceleration** - Automatic CUDA support for fast transcription (with CPU fallback)
- 📊 **Real-time Waveform** - Visual feedback with animated waveform bars
- ⚡ **Instant Text Insertion** - Transcribed text appears automatically at cursor
- 🎨 **Modern UI** - Clean, draggable floating window
- 🧠 **Smart Punctuation** - Automatically adds punctuation and capitalization
- 🖥️ **Cross-Platform** - Works on X11 and Wayland (Linux)
- 📦 **One-Click Setup** - Simple installation with automated dependency management

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.10 or higher
- **ffmpeg** for audio processing
- **NVIDIA GPU** (optional, for GPU acceleration)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AnandBhandari1/fast_simple.git
   cd fast_simple
   ```

2. **Install ffmpeg** (if not already installed)
   ```bash
   # Ubuntu/Debian
   sudo apt install ffmpeg

   # Fedora
   sudo dnf install ffmpeg

   # Arch
   sudo pacman -S ffmpeg
   ```

3. **Run setup script**
   ```bash
   ./setup.sh
   ```

   This will:
   - Install `uv` package manager (if needed)
   - Check system requirements
   - Install Python dependencies (~3GB download for Whisper models)
   - Verify GPU support

4. **Launch the app**
   ```bash
   ./run.sh
   ```

---

## 🎮 Usage

### Recording Audio

**Method 1: Global Hotkey (Recommended)**
- Press `F8` from anywhere to start recording
- Speak clearly into your microphone
- Press `F8` again to stop and transcribe

**Method 2: App Button**
- Click the "Record" button in the app window
- Speak into your microphone
- Click "Stop" to transcribe

### Understanding the Status

| Status | Meaning |
|--------|---------|
| **Loading...** | Model is loading (wait 10-30 seconds on first start) |
| **Ready • GPU/CPU** | Ready to record |
| **Recording...** | Currently recording (waveform active) |
| **Processing...** | Saving audio file |
| **Transcribing...** | Converting speech to text |
| **Adding punctuation...** | Formatting text |
| **Inserting...** | Typing text at cursor |
| **Inserted!** | Done! |

### Window Controls

- **Drag** - Click and drag anywhere on the window to move it
- **Always on Top** - Window stays visible above other apps
- **Close** - Click X or use Alt+F4

---

## ⚙️ Configuration

### Force CPU Mode

If you want to disable GPU and use CPU only:

```bash
FORCE_CPU=1 ./run.sh
```

### Change Whisper Model

Edit `app.py` line 101 to change the model:

```python
self.model_name = "large-v3-turbo"  # or "medium", "small", "base"
```

**Available models:**
- `large-v3-turbo` - Best quality, fastest large model (default, ~1.5GB)
- `large-v3` - Highest quality, slower (~3GB)
- `medium` - Good balance (~1.5GB)
- `small` - Faster, lower quality (~500MB)
- `base` - Fastest, lowest quality (~150MB)

### Wayland Setup (GNOME/KDE)

On Wayland, the F8 hotkey requires system configuration:

1. Open **Settings** → **Keyboard** → **Keyboard Shortcuts**
2. Click **Add Shortcut** or **+**
3. Configure:
   - **Name**: `FastSimple Toggle`
   - **Command**: `python3 /tmp/faststt_toggle.py`
   - **Shortcut**: Press `F8`
4. Click **Add** or **Save**

The app will create the toggle script automatically on first run.

---

## 🛠️ Troubleshooting

### "Model not loaded yet!"

**Solution:** Wait 10-30 seconds after starting the app. The Whisper model takes time to load.

### No audio captured

**Possible causes:**
- Microphone not set as default input
- Missing microphone permissions
- PulseAudio/PipeWire issues

**Solutions:**
```bash
# Check available audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Test microphone
arecord -d 3 test.wav && aplay test.wav
```

### F8 hotkey not working

**On X11:**
- The app should work automatically
- Check terminal for error messages

**On Wayland:**
- Follow the Wayland setup instructions above
- Or use the in-app Record button

### GPU not detected

**Check NVIDIA drivers:**
```bash
nvidia-smi
```

**Install CUDA toolkit (if needed):**
```bash
sudo apt install nvidia-cuda-toolkit
```

**Use CPU mode as fallback:**
```bash
FORCE_CPU=1 ./run.sh
```

### Text not inserting

**Fallback method:**
- The app copies text to clipboard automatically
- Paste manually with `Ctrl+V` (or `Ctrl+Shift+V` in terminals)

### Dependencies installation fails

**Try manual sync:**
```bash
uv sync --verbose
```

**Check Python version:**
```bash
python3 --version  # Should be 3.10 or higher
```

---

## 📋 System Requirements

### Required

- **OS**: Linux (Ubuntu 20.04+, Fedora 35+, Arch, etc.)
- **Python**: 3.10 or higher
- **ffmpeg**: Audio codec support
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 5GB free space (for models and dependencies)

### Optional (for GPU acceleration)

- **GPU**: NVIDIA GPU with CUDA support
- **VRAM**: 4GB+ recommended for large models
- **CUDA**: 11.8 or higher
- **Driver**: NVIDIA driver 520+

### Tested On

- ✅ Ubuntu 22.04 / 24.04
- ✅ Pop!_OS 22.04
- ✅ Fedora 39 / 40
- ✅ Arch Linux
- ✅ X11 and Wayland sessions

---

## 🏗️ Project Structure

```
fast_simple/
├── app.py              # Main application
├── pyproject.toml      # Dependencies configuration
├── setup.sh            # One-click setup script
├── run.sh              # Launch script
├── README.md           # This file
├── LICENSE             # MIT License
├── .gitignore          # Git ignore rules
└── .env.example        # Environment variables template
```

---

## 🧰 Tech Stack

- **[OpenAI Whisper](https://github.com/openai/whisper)** - Speech recognition
- **[PyTorch](https://pytorch.org/)** - Deep learning framework
- **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** - Modern UI framework
- **[sounddevice](https://python-sounddevice.readthedocs.io/)** - Audio I/O
- **[pynput](https://pynput.readthedocs.io/)** - Global hotkey detection
- **[pyautogui](https://pyautogui.readthedocs.io/)** - Text insertion automation
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager

---

## 📝 Development

### Dependencies

All dependencies are managed via `pyproject.toml`:

```toml
[project]
dependencies = [
    "openai-whisper>=20231117",
    "customtkinter",
    "sounddevice",
    "torch",
    "torchaudio",
    "pynput",
    "pyautogui",
    "pyperclip",
    "numpy",
]
```

### Manual Installation

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run directly
uv run python app.py
```

### Running in Development Mode

```bash
# Enable verbose logging
uv run python app.py --verbose

# Force CPU mode for testing
FORCE_CPU=1 uv run python app.py
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Areas for Contribution

- 🐛 Bug fixes
- ✨ New features (language selection, custom hotkeys, etc.)
- 📚 Documentation improvements
- 🌍 Platform support (macOS, Windows)
- 🎨 UI/UX enhancements

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

- **OpenAI Whisper** - Speech recognition model
- **Astral** - uv package manager
- All the amazing open-source contributors

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

## 📬 Contact

- **Issues**: [GitHub Issues](https://github.com/AnandBhandari1/fast_simple/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AnandBhandari1/fast_simple/discussions)

---

<div align="center">


[Report Bug](https://github.com/AnandBhandari1/fast_simple/issues) · [Request Feature](https://github.com/AnandBhandari1/fast_simple/issues)

</div>
