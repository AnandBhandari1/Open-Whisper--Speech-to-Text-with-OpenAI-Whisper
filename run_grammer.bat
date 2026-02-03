@echo off
echo ==========================================
echo  Fast Simple with Grammar Correction
echo  Using Local Ollama (gemma3:latest)
echo ==========================================
echo.

REM Check if uv is available
where uv >nul 2>&1
if errorlevel 1 (
    echo ERROR: uv not found! Please install uv first.
    echo Visit: https://docs.astral.sh/uv/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to install dependencies.
    pause
    exit /b 1
)

REM Install ollama Python client if not already installed
echo Checking for ollama Python package...
.venv\Scripts\python.exe -c "import ollama" 2>nul
if errorlevel 1 (
    echo Installing ollama Python client...
    uv pip install ollama
    echo.
    echo [OK] Ollama Python client installed!
) else (
    echo [OK] Ollama Python client already installed
)

echo.
echo Configuration:
echo   Ollama Model: gemma3:latest (or set OLLAMA_MODEL)
echo   Ollama Host:  http://localhost:11434 (or set OLLAMA_HOST)
echo.
echo Starting Fast Simple with Grammar Correction...
echo Press F8 to toggle recording
echo.

REM Run the grammar-enabled app using uv run
uv run python app_with_grammer.py
