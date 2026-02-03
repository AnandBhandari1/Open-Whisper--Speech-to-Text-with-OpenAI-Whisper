# VoiceType AI 🎤

**AI-Powered Speech-to-Text with Grammar Correction & Multiple Tones**

A lightweight, GPU-accelerated speech recognition application that transcribes your voice and automatically inserts text at your cursor position. Features AI-powered grammar correction, multiple writing tones, and smart text processing using OpenAI Whisper, Ollama, and LanguageTool.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/badge/uv-package%20manager-blue)](https://github.com/astral-sh/uv)
[![Whisper](https://img.shields.io/badge/Whisper-OpenAI-green)](https://github.com/openai/whisper)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-purple)](https://ollama.com)

---

## ✨ Features

- 🎯 **Global Hotkey** - Press `F8` from anywhere to start/stop recording
- 🚀 **GPU Acceleration** - Automatic CUDA support for fast transcription (with CPU fallback)
- ✍️ **AI Grammar Correction** - Fix grammar, remove filler words using Ollama or LanguageTool
- 🎨 **Multiple Writing Tones** - Choose from Original, Grammar, Professional, Polite, or Rephrase
- ⚡ **Instant Text Insertion** - Transcribed text appears automatically at cursor
- 🖥️ **Compact UI** - Clean, rectangular floating window with tone selection dropdown
- 🧠 **Smart Punctuation** - Automatically adds punctuation and capitalization
- 🏠 **Local Processing** - All AI processing happens locally (no cloud required)
- 🎛️ **Three App Variants** - Choose the version that fits your workflow
- 📦 **One-Click Setup** - Simple installation with automated dependency management

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.10 or higher
- **ffmpeg** for audio processing
- **NVIDIA GPU** (optional, for GPU acceleration)
- **Java** (optional, for LanguageTool grammar correction)
- **Ollama** (optional, for AI tone processing)

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
   
   Choose the version that fits your needs:
   
   ```bash
   # Basic version - punctuation only
   ./run.sh
   
   # OR grammar correction via Ollama
   ./run_grammer.sh
   
   # OR full version with tone selection dropdown
   ./run_with_settings.sh
   ```

---

## 🎮 Usage

### Recording Audio

**Method 1: Global Hotkey (Recommended)**
- Press `F8` from anywhere to start recording
- Speak clearly into your microphone
- Press `F8` again to stop and transcribe

**Method 2: App Button**
- Click the "🎙" button in the app window
- Speak into your microphone
- Click "⏹" to stop and transcribe

### Understanding the Tones

| Tone | Description | Requirements |
|------|-------------|--------------|
| **Original** | Just punctuation and capitalization | None |
| **Grammar** | Fast grammar correction + filler word removal | LanguageTool (Java) |
| **Professional** | Grammar fix + simplify + concise writing | Ollama |
| **Polite** | Convert to courteous, formal language | Ollama |
| **Rephrase** | Complete rewording for clarity | Ollama |

### Setting Up Ollama (for Professional/Polite/Rephrase tones)

1. **Install Ollama**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Pull a model**
   ```bash
   ollama pull gemma3:latest
   # or
   ollama pull llama3.2:3b
   ```

3. **Start Ollama**
   ```bash
   ollama serve
   ```

### Window Controls

- **Drag** - Click and drag anywhere on the window to move it
- **Dropdown** - Select your preferred tone from the dropdown
- **Always on Top** - Window stays visible above other apps
- **Close** - Click X or use Alt+F4

---

## 🎛️ Three App Variants

### 1. Original (`app.py` / `run.sh`)
Basic speech-to-text with smart punctuation.

**Best for:** Quick transcription without AI processing

**Features:**
- Speech-to-text with Whisper
- Automatic punctuation
- Capitalization
- Global hotkey (F8)

### 2. Grammar (`app_with_grammer.py` / `run_grammer.sh`)
Grammar correction via Ollama with automatic fallback.

**Best for:** Users who want consistent grammar correction

**Features:**
- All Original features
- Grammar correction via Ollama
- Filler word removal (um, uh, like, etc.)
- Falls back to punctuation-only if Ollama unavailable

### 3. Settings (`app_with_settings.py` / `run_with_settings.sh`)
Full-featured version with tone selection dropdown.

**Best for:** Users who want flexibility in writing styles

**Features:**
- All Grammar features
- **5 Tones selectable via dropdown:**
  - **Original** - Punctuation only (fastest, no AI)
  - **Grammar** - Fast local grammar correction (LanguageTool)
  - **Professional** - Grammar + simplify (Ollama)
  - **Polite** - Courteous formal language (Ollama)
  - **Rephrase** - Complete rewording (Ollama)

---

## ⚙️ Configuration

### Force CPU Mode

If you want to disable GPU and use CPU only:

```bash
FORCE_CPU=1 ./run.sh
```

### Change Whisper Model

Edit the app file to change the model:

```python
self.model_name = "large-v3-turbo"  # or "medium", "small", "base"
```

**Available models:**
- `large-v3-turbo` - Best quality, fastest large model (default, ~1.5GB)
- `large-v3` - Highest quality, slower (~3GB)
- `medium` - Good balance (~1.5GB)
- `small` - Faster, lower quality (~500MB)
- `base` - Fastest, lowest quality (~150MB)

### Change Ollama Model

Set via environment variable:

```bash
export OLLAMA_MODEL="llama3.2:3b"
./run_with_settings.sh
```

Default is `gemma3:latest`.

### Wayland Setup (GNOME/KDE)

On Wayland, the F8 hotkey requires system configuration:

1. Open **Settings** → **Keyboard** → **Keyboard Shortcuts**
2. Click **Add Shortcut** or **+**
3. Configure:
   - **Name**: `VoiceType Toggle`
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

### LanguageTool not working (Grammar tone)

**Error:** "LanguageTool not available"

**Solution:** Install Java
```bash
# Ubuntu/Debian
sudo apt install default-jre

# Fedora
sudo dnf install java-latest-openjdk
```

### Ollama not working (Professional/Polite/Rephrase tones)

**Error:** "Ollama not available"

**Solutions:**
1. Make sure Ollama is running: `ollama serve`
2. Check if model is pulled: `ollama list`
3. Pull a model: `ollama pull gemma3:latest`

### Text not inserting

**Fallback method:**
- The app copies text to clipboard automatically
- Paste manually with `Ctrl+V` (or `Ctrl+Shift+V` in terminals)

---

## 📋 System Requirements

### Required

- **OS**: Linux (Ubuntu 20.04+, Fedora 35+, Arch, etc.)
- **Python**: 3.10 or higher
- **ffmpeg**: Audio codec support
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 5GB free space (for models and dependencies)

### Optional (for enhanced features)

- **GPU**: NVIDIA GPU with CUDA support (for faster transcription)
- **VRAM**: 4GB+ recommended for large models
- **Java**: For LanguageTool grammar correction
- **Ollama**: For AI-powered tone processing

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
├── app.py                   # Original: Basic speech-to-text
├── app_with_grammer.py      # Grammar: Ollama grammar correction
├── app_with_settings.py     # Settings: Full version with tone dropdown
├── pyproject.toml           # Dependencies configuration
├── setup.sh                 # One-click setup script (Linux/Mac)
├── setup.bat                # One-click setup script (Windows)
├── run.sh                   # Launch Original version
├── run_grammer.sh           # Launch Grammar version
├── run_with_settings.sh     # Launch Settings version
├── run.bat                  # Windows launcher
├── run_grammer.bat          # Windows Grammar launcher
├── run_with_settings.bat    # Windows Settings launcher
├── README.md                # This file
├── LICENSE                  # MIT License
├── .gitignore               # Git ignore rules
└── .env.example             # Environment variables template
```

---

## 🧰 Tech Stack

- **[OpenAI Whisper](https://github.com/openai/whisper)** - Speech recognition
- **[Ollama](https://ollama.com)** - Local AI for grammar and tone processing
- **[LanguageTool](https://languagetool.org)** - Fast local grammar correction
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
    "ollama",              # For AI tone processing
    "language-tool-python", # For fast grammar correction
]
```

### Manual Installation

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run directly
uv run python app_with_settings.py
```

### Running in Development Mode

```bash
# Enable verbose logging
uv run python app_with_settings.py --verbose

# Force CPU mode for testing
FORCE_CPU=1 uv run python app_with_settings.py
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
- 🔊 Audio processing improvements

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

- **OpenAI Whisper** - Speech recognition model
- **Ollama** - Local AI inference
- **LanguageTool** - Grammar correction engine
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
