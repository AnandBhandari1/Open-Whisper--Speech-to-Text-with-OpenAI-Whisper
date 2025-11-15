@echo off
REM Quick launcher - just double-click this file
cd /d "%~dp0"
uv run python app.py
if %errorlevel% neq 0 pause
