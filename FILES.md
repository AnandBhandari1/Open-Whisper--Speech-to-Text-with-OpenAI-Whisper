# FastSimple - File Structure

Complete list of all files and their purposes.

## Documentation Files

| File | Purpose |
|------|---------|
| **README.md** | Main README (Linux-focused, general info) |
| **WINDOWS_SETUP.md** | Complete Windows setup guide with all commands |
| **QUICKSTART.md** | Super quick start guide (5 minutes) |
| **FILES.md** | This file - lists all files and purposes |

## Application Files

| File | Purpose | Size |
|------|---------|------|
| **app.py** | Main application code | ~30KB |
| **pyproject.toml** | Python dependencies configuration | <1KB |
| **uv.lock** | Dependency lock file (auto-generated) | ~280KB |

## Windows Batch Scripts

| File | Purpose | When to Use |
|------|---------|-------------|
| **setup.bat** | Main setup script | Run once on new PC |
| **run_win.bat** | Full launcher with status info | Recommended launcher |
| **start.bat** | Simple launcher | Double-click to start |
| **run.bat** | Alternative launcher | Also works |
| **find_paths.bat** | Find CUDA/ffmpeg paths | For troubleshooting |
| **setup_cuda.bat** | CUDA setup helper | If GPU not detected |

## Linux Shell Scripts

| File | Purpose |
|------|---------|
| **setup.sh** | Linux setup script |
| **run.sh** | Linux launcher |

## Auto-Generated Files

| File | Purpose | Size | Notes |
|------|---------|------|-------|
| **ffmpeg.exe** | Bundled ffmpeg binary | ~84MB | Auto-created on first run |
| **.venv/** | Python virtual environment | ~6GB | Created by `uv sync` |
| **temp_audio.wav** | Temporary recording file | <1MB | Auto-deleted after use |

## Configuration Files

| File | Purpose |
|------|---------|
| **.gitignore** | Git ignore rules |

## Quick Reference

### First Time Setup
```
1. setup.bat           → Run this first
2. run_win.bat         → Then run this
```

### Daily Usage
```
start.bat              → Just double-click this
```

### Troubleshooting
```
find_paths.bat         → Find CUDA/ffmpeg locations
setup_cuda.bat         → Setup CUDA manually
```

### Updates
```
uv sync --upgrade      → Update all dependencies
```

## File Sizes Summary

- **Source code**: <100KB (app.py + pyproject.toml)
- **Documentation**: ~150KB (all .md files)
- **Batch scripts**: ~20KB (all .bat files)
- **Shell scripts**: ~10KB (all .sh files)
- **ffmpeg.exe**: ~84MB (auto-created)
- **.venv folder**: ~6-7GB (dependencies + models)
- **Total disk usage**: ~7GB

## What Gets Downloaded

When you run `setup.bat`:

1. **PyTorch with CUDA**: ~2.7GB
2. **Whisper models**: ~3GB (large-v3-turbo)
3. **Other Python packages**: ~500MB
4. **imageio-ffmpeg**: ~30MB

**Total download**: ~6-7GB

## What's in .venv

```
.venv/
├── Lib/
│   └── site-packages/
│       ├── torch/              (~2.7GB - PyTorch CUDA)
│       ├── whisper/            (~3GB - Whisper models)
│       ├── imageio_ffmpeg/     (~30MB - bundled ffmpeg)
│       ├── customtkinter/      (~5MB - UI)
│       ├── sounddevice/        (~1MB - audio)
│       └── ... (other packages)
└── Scripts/
    ├── python.exe
    └── uv.exe
```

## Dependencies from pyproject.toml

```toml
dependencies = [
    "openai-whisper>=20231117",
    "customtkinter",
    "sounddevice",
    "torch",                    # CUDA 12.8 version
    "torchaudio",
    "pynput",
    "pyautogui",
    "pyperclip",
    "numpy",
    "imageio-ffmpeg",
]
```

## Don't Commit These Files

Listed in `.gitignore`:

- `.venv/` - Virtual environment
- `uv.lock` - Lock file
- `ffmpeg.exe` - Binary
- `temp_audio.wav` - Temp file
- `__pycache__/` - Python cache
- `*.pyc` - Compiled Python

## Essential Files for Distribution

If sharing the project:

**Must include:**
- app.py
- pyproject.toml
- setup.bat
- run_win.bat
- start.bat
- README.md
- WINDOWS_SETUP.md

**Don't include:**
- .venv/
- uv.lock
- ffmpeg.exe
- temp_audio.wav

Users run `setup.bat` to generate the rest.

## Minimum Files to Run

After setup, you only need:

```
fast_simple/
├── app.py                 (required)
├── pyproject.toml         (required)
├── ffmpeg.exe             (required, auto-created)
├── .venv/                 (required, created by setup)
└── run_win.bat            (optional, can run directly)
```

## Commands Cheat Sheet

```batch
# Setup (once)
setup.bat

# Run app
run_win.bat
start.bat
uv run python app.py

# Update
uv sync --upgrade

# Clean reinstall
rmdir /s /q .venv
del uv.lock
del ffmpeg.exe
setup.bat

# Troubleshoot
find_paths.bat
setup_cuda.bat
nvidia-smi
```

---

**Last Updated**: 2025-11-15
