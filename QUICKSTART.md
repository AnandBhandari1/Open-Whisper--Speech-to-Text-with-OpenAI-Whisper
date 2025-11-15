# FastSimple - Quick Start (Windows)

Super simple guide to get started in 5 minutes.

## What You Need

- Windows 10/11
- 10GB free disk space
- Internet connection

## Installation (3 commands)

### 1. Install Python
```batch
winget install Python.Python.3.12
```

### 2. Install uv
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Close and reopen your terminal after this step!**

### 3. Run Setup
```batch
cd path\to\fast_simple
setup.bat
```

Wait 5-10 minutes for downloads (~6GB).

## Usage

### Start the App
```batch
run_win.bat
```

Or double-click: **start.bat**

### Record Speech
1. Press **F8** (anywhere on your PC)
2. Speak
3. Press **F8** again
4. Text appears at your cursor!

## That's It!

For detailed guide: See **WINDOWS_SETUP.md**

For troubleshooting: See **WINDOWS_SETUP.md** → Troubleshooting section

## Common Issues

**"uv not found"**
- Restart your terminal after installing uv

**"CUDA not available"**
- You need NVIDIA GPU for GPU mode
- App works fine in CPU mode too (just slower)

**"Processing error"**
- First run creates ffmpeg.exe (84MB)
- Just try recording again
