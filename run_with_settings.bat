@echo off
echo ==========================================
echo  Fast Simple with Settings & Tones
echo  Choose your writing style!
echo ==========================================
echo.

REM Check if uv is available
where uv >nul 2>&1
if errorlevel 1 (
    echo ERROR: uv not found! Please install uv first.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM Install required Python packages
echo Checking for required packages...

.venv\Scripts\python.exe -c "import ollama" 2>nul
if errorlevel 1 (
    echo Installing ollama...
    uv pip install ollama
)

.venv\Scripts\python.exe -c "import language_tool_python" 2>nul
if errorlevel 1 (
    echo Installing language-tool-python...
    uv pip install language-tool-python
    echo [OK] Packages installed!
) else (
    echo [OK] All packages installed
)

echo.
echo Available Tones:
echo   1. ORIGINAL     - Just punctuation, no grammar changes
echo   2. GRAMMAR      - Fast grammar correction (LanguageTool)
echo   3. PROFESSIONAL - Grammar fix + remove fillers + simplify (Ollama)
echo   4. POLITE       - Convert to polite, courteous language (Ollama)
echo   5. REPHRASE     - Reword and rephrase for clarity (Ollama)
echo.
echo Click the gear icon (⚙️) to change tone anytime!
echo.
echo Press F8 to toggle recording
echo.

uv run python app_with_settings.py
