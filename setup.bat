@echo off
setlocal enabledelayedexpansion

echo ============================================
echo    FastSimple - Setup Script
echo ============================================
echo.
echo Simple speech-to-text with OpenAI Whisper
echo.

REM Track setup status
set ISSUES=0

echo Step 1: Checking system requirements...
echo.

REM Check if uv is installed
echo Checking for uv package manager...
where uv >nul 2>nul
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('uv --version 2^>nul') do set UV_VERSION=%%i
    echo [OK] Found (!UV_VERSION!)
) else (
    echo [X] Not found
    echo.
    echo Installing uv package manager...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

    REM Check again
    where uv >nul 2>nul
    if !errorlevel! equ 0 (
        echo [OK] uv installed successfully
    ) else (
        echo [X] Failed to install uv
        echo Please install manually: https://docs.astral.sh/uv/getting-started/installation/
        set /a ISSUES+=1
    )
)

REM Check for ffmpeg (optional - we bundle it with imageio-ffmpeg)
echo Checking for ffmpeg...
where ffmpeg >nul 2>nul
if %errorlevel% equ 0 (
    for /f "tokens=3" %%i in ('ffmpeg -version 2^>nul ^| findstr /C:"ffmpeg version"') do (
        echo [OK] System ffmpeg found (%%i)
        goto :ffmpeg_done
    )
    echo [OK] System ffmpeg found
    :ffmpeg_done
) else (
    echo [INFO] System ffmpeg not found
    echo [OK] Will use bundled ffmpeg (imageio-ffmpeg)
)

REM Check for CUDA (optional, for GPU acceleration)
echo Checking for CUDA/GPU support...
where nvidia-smi >nul 2>nul
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('nvidia-smi --query-gpu^=name --format^=csv^,noheader 2^>nul') do (
        echo [OK] Found (%%i)
        goto :cuda_done
    )
    echo [!] nvidia-smi found but no GPU detected
    :cuda_done
) else (
    echo [!] Not available (will use CPU mode)
)

REM Check Python version
echo Checking Python version...
where python >nul 2>nul
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
        set PYTHON_MAJOR=%%a
        set PYTHON_MINOR=%%b
    )

    if !PYTHON_MAJOR! geq 3 (
        if !PYTHON_MINOR! geq 10 (
            echo [OK] !PYTHON_VERSION!
        ) else (
            echo [X] !PYTHON_VERSION! (requires ^>=3.10)
            set /a ISSUES+=1
        )
    ) else (
        echo [X] !PYTHON_VERSION! (requires ^>=3.10)
        set /a ISSUES+=1
    )
) else (
    echo [X] Python not found
    set /a ISSUES+=1
)

echo.
echo ============================================

REM Exit if critical issues found
if %ISSUES% gtr 0 (
    echo [!] Found %ISSUES% critical issue(s)
    echo Please resolve the above issues before continuing.
    echo.
    exit /b 1
)

echo [OK] All system requirements met!
echo.

REM Install Python dependencies
echo Step 2: Installing Python dependencies...
echo.

REM Check if NVIDIA GPU is available
set INSTALL_CUDA=0
where nvidia-smi >nul 2>nul
if %errorlevel% equ 0 (
    nvidia-smi --query-gpu=name --format=csv,noheader >nul 2>nul
    if !errorlevel! equ 0 (
        set INSTALL_CUDA=1
    )
)

if !INSTALL_CUDA! equ 1 (
    echo [OK] NVIDIA GPU detected - installing PyTorch with CUDA 12.8 support...
    echo This may take a few minutes (downloading PyTorch CUDA ~3GB + Whisper models ~3GB)...
    echo.
) else (
    echo [INFO] No NVIDIA GPU detected - installing CPU-only version...
    echo This may take a few minutes (downloading Whisper models ~3GB)...
    echo.
)

REM Install all dependencies via uv sync (uses pyproject.toml configuration)
uv sync

if %errorlevel% equ 0 (
    echo.
    echo [OK] Dependencies installed successfully!
) else (
    echo.
    echo [X] Failed to install dependencies
    echo Try running: uv sync --verbose
    exit /b 1
)

REM Verify GPU availability with PyTorch
echo.
echo Step 3: Verifying GPU setup...
echo.

uv run python -c "import torch; print(f'PyTorch version: {torch.__version__}'); cuda_available = torch.cuda.is_available(); print(f'CUDA available: {cuda_available}'); print(f'GPU: {torch.cuda.get_device_name(0)}' if cuda_available else 'CPU mode - No GPU detected')" 2>nul
if %errorlevel% equ 0 (
    echo.
    echo [OK] PyTorch and GPU check complete
) else (
    echo.
    echo [!] GPU check failed - will use CPU mode
)

REM Success message
echo.
echo ============================================
echo [OK] Setup completed successfully!
echo ============================================
echo.
echo Next steps:
echo   1. Run the app:  run_win.bat  (or double-click start.bat)
echo   2. Press F8 or click 'Record' to start recording
echo   3. Speak, then press F8 again to transcribe
echo.
echo Features:
echo   * Global F8 hotkey for recording
echo   * Real-time waveform visualization
echo   * Automatic text insertion at cursor
echo   * GPU acceleration (if available)
echo.
echo For detailed Windows setup guide, see WINDOWS_SETUP.md
echo.
