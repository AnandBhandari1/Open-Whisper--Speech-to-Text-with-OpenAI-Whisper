@echo off
setlocal

echo ==========================================
echo    FastSimple - Speech to Text
echo ==========================================
echo.
echo Features:
echo    * OpenAI Whisper (large-v3-turbo)
echo    * GPU acceleration (if available)
echo    * Real-time waveform visualization
echo    * Automatic text insertion
echo.

REM Check if uv is installed
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: uv is not installed.
    echo Please run setup.bat first
    exit /b 1
)

echo.

REM Check GPU availability
echo GPU Status:
uv run python -c "import torch; cuda = torch.cuda.is_available(); print(f'  GPU: {torch.cuda.get_device_name(0)}' if cuda else '  Mode: CPU (no GPU detected)')" 2>nul
if %errorlevel% neq 0 (
    echo   Checking...
)

echo.
echo Global Hotkey: F8
echo    Press F8 to start/stop recording
echo    Or use the Record button in the app
echo.
echo The app will appear as a floating window
echo    * Drag to move it around
echo    * Watch waveform bars while recording
echo    * Text auto-inserts at cursor when done
echo.

REM Optional: Set force CPU mode if FORCE_CPU env var is set
if "%FORCE_CPU%"=="1" (
    echo Warning: FORCE_CPU=1 - Running in CPU mode
    echo.
)

echo Starting FastSimple...
echo.
echo ==========================================
echo.

REM Run the app
uv run python app.py
