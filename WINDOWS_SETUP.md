# FastSimple - Windows Setup Guide

Complete guide for installing and running FastSimple on Windows with GPU acceleration.

## Table of Contents
- [Quick Start](#quick-start)
- [Detailed Installation](#detailed-installation)
- [All Commands Used](#all-commands-used)
- [Troubleshooting](#troubleshooting)
- [Technical Details](#technical-details)

---

## Quick Start

### For Fresh Windows PC

1. **Install Python**
   ```batch
   winget install Python.Python.3.12
   ```

2. **Install uv package manager**
   ```powershell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Restart your terminal** (close and reopen Command Prompt/PowerShell)

4. **Navigate to project directory**
   ```batch
   cd C:\Users\YourName\Documents\myprojects\fast_simple
   ```

5. **Run setup**
   ```batch
   setup.bat
   ```

6. **Run the app**
   ```batch
   run_win.bat
   ```

**That's it!** Press F8 to record.

---

## Detailed Installation

### Step 1: Install Prerequisites

#### 1.1 Install Python 3.12

**Option A: Using winget (Recommended)**
```batch
winget install Python.Python.3.12
```

**Option B: Manual Download**
1. Go to https://www.python.org/downloads/
2. Download Python 3.12 (64-bit)
3. Run installer
4. ✅ **Check "Add Python to PATH"**
5. Click "Install Now"

**Verify installation:**
```batch
python --version
```
Should output: `Python 3.12.x`

#### 1.2 Install uv Package Manager

**Run in PowerShell:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify installation:**
```batch
uv --version
```

**Important:** If `uv` is not recognized, restart your terminal or add to PATH manually:
- Path: `C:\Users\YourName\.local\bin`

### Step 2: Download/Clone Project

Place project in a directory like:
```
C:\Users\YourName\Documents\myprojects\fast_simple
```

### Step 3: Run Setup Script

Open Command Prompt or PowerShell in the project directory:

```batch
setup.bat
```

**What it does:**
1. ✅ Checks Python version (requires >=3.10)
2. ✅ Detects NVIDIA GPU (if present)
3. ✅ Installs PyTorch with CUDA 12.8 (for GPU)
4. ✅ Installs all Python dependencies
5. ✅ Downloads Whisper models (~3GB)
6. ✅ Sets up bundled ffmpeg locally
7. ✅ Verifies GPU/CUDA setup

**Expected output:**
```
============================================
   FastSimple - Setup Script
============================================

Step 1: Checking system requirements...

Checking for uv package manager...
[OK] Found (uv 0.x.x)

Checking for ffmpeg...
[INFO] System ffmpeg not found
[OK] Will use bundled ffmpeg (imageio-ffmpeg)

Checking for CUDA/GPU support...
[OK] Found (NVIDIA GeForce RTX 5070 Ti)

Checking Python version...
[OK] 3.12.10

============================================
[OK] All system requirements met!

Step 2: Installing Python dependencies...

[OK] NVIDIA GPU detected - installing PyTorch with CUDA support...
This may take a few minutes (downloading PyTorch CUDA ~3GB + Whisper models ~3GB)...

Resolved 72 packages in 1.5s
...
Installed XX packages in XXs

[OK] Dependencies installed successfully!

Step 3: Verifying GPU setup...

PyTorch version: 2.9.1+cu128
CUDA available: True
GPU: NVIDIA GeForce RTX 5070 Ti

[OK] PyTorch and GPU check complete

============================================
[OK] Setup completed successfully!
============================================
```

**Total time:** 5-15 minutes (depending on internet speed)
**Total download:** ~6-7GB

### Step 4: Run the Application

**Option 1: Full launcher with info**
```batch
run_win.bat
```

**Option 2: Simple double-click launcher**
- Double-click `start.bat`

**Option 3: Direct run**
```batch
uv run python app.py
```

**Expected output:**
```
==========================================
   FastSimple - Speech to Text (Windows)
==========================================

Starting FastSimple...

Tips:
  - Press F8 to start/stop recording
  - The window will appear in bottom-right corner
  - Drag to reposition it
  - Text auto-inserts at your cursor

==========================================

[OK] Using bundled ffmpeg: C:\...\ffmpeg.exe
Loading model: large-v3-turbo
[OK] Model loaded successfully on CUDA
```

---

## All Commands Used

### Installation Commands

```batch
# Install Python
winget install Python.Python.3.12

# Install uv (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Check installations
python --version
uv --version

# Run setup
setup.bat
```

### Running the App

```batch
# Method 1: Full launcher
run_win.bat

# Method 2: Simple launcher
start.bat

# Method 3: Direct run
uv run python app.py

# Force CPU mode
set FORCE_CPU=1
run_win.bat
```

### GPU/CUDA Commands

```batch
# Check GPU
nvidia-smi

# Check CUDA version
nvcc --version

# Find CUDA installation
where nvcc

# Test PyTorch CUDA
uv run python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"

# Test GPU computation
uv run python -c "import torch; x = torch.randn(1000, 1000).cuda(); print('GPU works!')"
```

### Dependency Management

```batch
# Sync dependencies (after pyproject.toml changes)
uv sync

# Update all dependencies
uv sync --upgrade

# Install specific package
uv pip install package-name

# Uninstall package
uv pip uninstall package-name

# List installed packages
uv pip list

# Show package details
uv pip show torch
```

### Troubleshooting Commands

```batch
# Clean reinstall
rmdir /s /q .venv
del uv.lock
del ffmpeg.exe
setup.bat

# Check audio devices
uv run python -c "import sounddevice; print(sounddevice.query_devices())"

# Verify bundled ffmpeg
dir ffmpeg.exe

# Check if app is using GPU
nvidia-smi
```

---

## File Structure

```
fast_simple/
├── app.py                  # Main application code
├── pyproject.toml          # Python dependencies config
├── uv.lock                 # Dependency lock file (auto-generated)
│
├── setup.bat               # Windows setup script
├── run_win.bat            # Windows launcher (detailed)
├── start.bat              # Simple launcher
├── run.bat                # Alternative launcher
│
├── setup.sh               # Linux setup script
├── run.sh                 # Linux launcher
│
├── find_paths.bat         # CUDA/ffmpeg path finder
├── setup_cuda.bat         # CUDA setup helper
│
├── ffmpeg.exe             # Bundled ffmpeg (auto-created, 84MB)
├── .venv/                 # Virtual environment (auto-created)
│   ├── Lib/
│   │   └── site-packages/
│   │       ├── imageio_ffmpeg/  # Contains bundled ffmpeg
│   │       ├── torch/           # PyTorch with CUDA
│   │       ├── whisper/         # OpenAI Whisper
│   │       └── ...
│   └── Scripts/
│
├── .gitignore             # Git ignore rules
├── README.md              # Main README (Linux-focused)
├── WINDOWS_SETUP.md       # This file
│
└── temp_audio.wav         # Temporary recording file (auto-deleted)
```

---

## Dependencies

### Python Packages (from pyproject.toml)

```toml
[project]
name = "fast-simple"
version = "1.0.0"
requires-python = ">=3.10"
dependencies = [
    "openai-whisper>=20231117",  # Speech recognition
    "customtkinter",              # Modern UI
    "sounddevice",                # Audio recording
    "torch",                      # PyTorch (CUDA version)
    "torchaudio",                 # Audio processing
    "pynput",                     # Global hotkey
    "pyautogui",                  # Text insertion
    "pyperclip",                  # Clipboard
    "numpy",                      # Numerical ops
    "imageio-ffmpeg",             # Bundled ffmpeg
]

# PyTorch CUDA 12.8 configuration
[[tool.uv.index]]
name = "pytorch-cu128"
url = "https://download.pytorch.org/whl/cu128"
explicit = true

[tool.uv.sources]
torch = { index = "pytorch-cu128" }
torchaudio = { index = "pytorch-cu128" }
torchvision = { index = "pytorch-cu128" }
```

### Package Sizes
- **torch (CUDA 12.8)**: ~2.7GB
- **openai-whisper + models**: ~3GB
- **torchaudio**: ~2MB
- **customtkinter**: ~5MB
- **imageio-ffmpeg**: ~30MB (includes ffmpeg binary)
- **Other packages**: ~100MB

**Total**: ~6-7GB

---

## GPU Configuration

### Supported GPUs

Works with any NVIDIA GPU with CUDA support:
- ✅ RTX 50 series (5090, 5080, 5070 Ti, etc.) - Blackwell
- ✅ RTX 40 series (4090, 4080, 4070, etc.) - Ada Lovelace
- ✅ RTX 30 series (3090, 3080, 3070, etc.) - Ampere
- ✅ RTX 20 series (2080 Ti, 2070, etc.) - Turing
- ✅ GTX 16 series (1660 Ti, etc.)
- ✅ GTX 10 series (1080 Ti, 1070, etc.) - Pascal

### CUDA Version Requirements

| GPU Series | Recommended CUDA | PyTorch Version |
|-----------|------------------|----------------|
| RTX 50 (Blackwell) | CUDA 12.8+ | PyTorch 2.9.1+cu128 ✅ |
| RTX 40 (Ada) | CUDA 12.4+ | PyTorch 2.6.0+cu124 or cu128 |
| RTX 30 (Ampere) | CUDA 11.8+ | Any recent version |
| RTX 20/GTX 16 | CUDA 11.0+ | Any recent version |

**Current setup uses:** PyTorch 2.9.1+cu128 (best compatibility)

### Performance Expectations

| GPU | Model | Speed (typical 5s audio) |
|-----|-------|-------------------------|
| RTX 5070 Ti | large-v3-turbo | ~1-2s |
| RTX 4090 | large-v3-turbo | ~1-2s |
| RTX 3080 | large-v3-turbo | ~2-3s |
| RTX 2070 | large-v3-turbo | ~3-5s |
| CPU (i7-12700) | large-v3-turbo | ~10-15s |

---

## Troubleshooting

### 1. "uv is not installed" or "uv not recognized"

**Solution:**
```batch
# Reinstall uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Restart terminal
# Try again
uv --version
```

If still not working, add to PATH manually:
1. Windows Search → "Environment Variables"
2. Edit "Path" variable
3. Add: `C:\Users\YourName\.local\bin`
4. Click OK
5. Restart terminal

### 2. "CUDA not available" but I have NVIDIA GPU

**Check drivers:**
```batch
nvidia-smi
```

If this fails:
1. Install/update NVIDIA drivers: https://www.nvidia.com/download/index.aspx
2. Restart PC
3. Run `setup.bat` again

**Check CUDA toolkit:**
```batch
nvcc --version
```

If not found:
- Install CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
- Choose your Windows version
- Install
- Restart terminal

**Verify PyTorch sees GPU:**
```batch
uv run python -c "import torch; print(torch.cuda.is_available())"
```

Should print `True`. If `False`:
```batch
# Clean reinstall
rmdir /s /q .venv
del uv.lock
setup.bat
```

### 3. "Processing error: file not found"

This means ffmpeg is missing. Solution:

```batch
# Delete existing ffmpeg (if any)
del ffmpeg.exe

# Restart app - it will auto-recreate
run_win.bat
```

Or manually create:
```batch
uv run python -c "import imageio_ffmpeg, shutil; shutil.copy2(imageio_ffmpeg.get_ffmpeg_exe(), 'ffmpeg.exe')"
```

### 4. App is slow even with GPU

**Check if GPU is actually being used:**

While transcribing, run in another terminal:
```batch
nvidia-smi
```

Look for `python.exe` in the process list with GPU usage.

If not using GPU:
```batch
# Verify CUDA is available
uv run python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'Device: {next(iter(torch.cuda.get_device_properties(0)))}' if torch.cuda.is_available() else '')"
```

### 5. "UnicodeEncodeError" or emoji errors

This is fixed in the latest version. Make sure you have the updated `app.py` with ASCII characters instead of emojis in print statements.

Check:
```batch
findstr /C:"[OK]" app.py
```
Should find matches (new version uses `[OK]` instead of ✅)

### 6. F8 hotkey not working

**Windows uses standard hotkey** (works globally).

If not working:
1. Check if another app is using F8
2. Run app as Administrator
3. Check terminal for errors

**Alternative:** Use the "Record" button in the app window

### 7. Text not inserting at cursor

**Automatic insertion may fail in:**
- Some UWP apps
- Virtual machines
- Remote desktop
- Some games

**Fallback:** Text is automatically copied to clipboard. Just press `Ctrl+V` to paste.

### 8. Setup fails during dependency installation

**Try verbose mode:**
```batch
uv sync --verbose
```

**Check Python version:**
```batch
python --version
```
Must be 3.10 or higher.

**Clean reinstall:**
```batch
rmdir /s /q .venv
del uv.lock
setup.bat
```

### 9. "No module named 'torch'"

Dependencies not installed. Run:
```batch
uv sync
```

### 10. Out of memory (GPU)

**Solution 1:** Use smaller model
Edit `app.py` line ~101:
```python
self.model_name = "medium"  # Instead of large-v3-turbo
```

**Solution 2:** Force CPU mode
```batch
set FORCE_CPU=1
run_win.bat
```

---

## Advanced Configuration

### Change Whisper Model

Edit `app.py` around line 101:

```python
self.model_name = "large-v3-turbo"  # Change this
```

**Options:**
- `large-v3-turbo` - Best quality, fast (1.5GB) ✅ Default
- `large-v3` - Highest quality, slower (3GB)
- `medium` - Good balance (1.5GB)
- `small` - Faster (500MB)
- `base` - Fastest (150MB)
- `tiny` - Very fast, lower quality (75MB)

Then run:
```batch
uv run python app.py
```

First run will download the new model.

### Force CPU Mode

**Temporary:**
```batch
set FORCE_CPU=1
run_win.bat
```

**Permanent:** Edit `app.py` around line 497:
```python
force_cpu = True  # Change to True
```

### Change Recording Hotkey

Edit `app.py` - search for `Key.f8` and replace with desired key:
```python
# Line ~428
if key == keyboard.Key.f9:  # Change from f8 to f9
```

### Custom Audio Settings

Edit `app.py` around line 93-95:
```python
self.samplerate = 44100  # Sample rate (Hz)
self.channels = 1        # Mono (1) or Stereo (2)
```

---

## System Requirements

### Minimum
- Windows 10 (64-bit)
- Python 3.10+
- 8GB RAM
- 10GB free disk space
- Internet connection (for setup)

### Recommended for GPU
- Windows 11
- NVIDIA GPU (4GB+ VRAM)
- 16GB RAM
- SSD
- CUDA 12.8+

### Tested On
- ✅ Windows 11 Pro (Build 26200)
- ✅ RTX 5070 Ti (16GB VRAM)
- ✅ CUDA 12.9
- ✅ Python 3.12.10
- ✅ PyTorch 2.9.1+cu128

---

## Performance Tips

1. **Use GPU mode** - 5-10x faster than CPU
2. **Close GPU apps** while using (Chrome, games, etc.)
3. **Keep recordings under 30s** - Faster processing
4. **Use SSD** - Faster model loading
5. **Sufficient VRAM** - 4GB+ recommended for large models
6. **Updated drivers** - Latest NVIDIA drivers

---

## Updates and Maintenance

### Update Dependencies
```batch
uv sync --upgrade
```

### Update PyTorch (if needed)
```batch
uv pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

### Clean Cache
```batch
# Clear Python cache
del /s /q __pycache__
del /s /q *.pyc

# Clear uv cache
uv cache clean
```

---

## Useful Resources

- **PyTorch**: https://pytorch.org/
- **CUDA Toolkit**: https://developer.nvidia.com/cuda-downloads
- **NVIDIA Drivers**: https://www.nvidia.com/download/index.aspx
- **OpenAI Whisper**: https://github.com/openai/whisper
- **uv Documentation**: https://github.com/astral-sh/uv

---

## Quick Reference Card

```
┌─────────────────────────────────────────┐
│        FastSimple Quick Reference        │
├─────────────────────────────────────────┤
│ Setup:           setup.bat              │
│ Run:             run_win.bat            │
│ Quick Start:     start.bat              │
│                                         │
│ Record:          Press F8               │
│ Stop:            Press F8 again         │
│                                         │
│ Force CPU:       set FORCE_CPU=1        │
│ Check GPU:       nvidia-smi             │
│ Test CUDA:       (see commands above)   │
│                                         │
│ Update:          uv sync --upgrade      │
│ Clean Install:   (delete .venv, run     │
│                   setup.bat)            │
└─────────────────────────────────────────┘
```

---

**Last Updated:** 2025-11-15
**Version:** 1.0.0
