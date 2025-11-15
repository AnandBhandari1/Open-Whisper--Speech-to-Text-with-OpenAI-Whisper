@echo off
REM ============================================
REM   FastSimple - Windows Launcher
REM ============================================

echo.
echo ==========================================
echo    FastSimple - Speech to Text (Windows)
echo ==========================================
echo.

REM Check if uv is installed
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] uv is not installed!
    echo Please run setup.bat first
    echo.
    pause
    exit /b 1
)

echo Starting FastSimple...
echo.
echo Tips:
echo   - Press F8 to start/stop recording
echo   - The window will appear in bottom-right corner
echo   - Drag to reposition it
echo   - Text auto-inserts at your cursor
echo.
echo ==========================================
echo.

REM Run the application
uv run python app.py

REM If app exits with error, pause so user can see the error
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application exited with error code: %errorlevel%
    echo.
    pause
)
