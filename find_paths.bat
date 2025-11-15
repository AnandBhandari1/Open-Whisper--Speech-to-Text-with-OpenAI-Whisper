@echo off
setlocal enabledelayedexpansion

echo ============================================
echo    Finding CUDA and FFmpeg Paths
echo ============================================
echo.

set CUDA_FOUND=0
set FFMPEG_FOUND=0
set CUDA_INSTALL_PATH=
set FFMPEG_PATH=

echo [1/4] Searching for CUDA installation...
echo.

REM Check standard CUDA installation location
if exist "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA" (
    echo Found CUDA toolkit directory!
    echo.
    echo Available CUDA versions:
    for /f %%i in ('dir /b /o-n "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA" 2^>nul') do (
        if !CUDA_FOUND! equ 0 (
            set "CUDA_INSTALL_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\%%i"
            set "CUDA_VERSION=%%i"
            set CUDA_FOUND=1
            echo   * %%i [WILL USE THIS]
        ) else (
            echo   * %%i
        )
    )
    echo.
)

REM Also check Program Files (x86)
if !CUDA_FOUND! equ 0 (
    if exist "C:\Program Files (x86)\NVIDIA GPU Computing Toolkit\CUDA" (
        echo Found CUDA toolkit directory in Program Files (x86)!
        echo.
        for /f %%i in ('dir /b /o-n "C:\Program Files (x86)\NVIDIA GPU Computing Toolkit\CUDA" 2^>nul') do (
            if !CUDA_FOUND! equ 0 (
                set "CUDA_INSTALL_PATH=C:\Program Files (x86)\NVIDIA GPU Computing Toolkit\CUDA\%%i"
                set "CUDA_VERSION=%%i"
                set CUDA_FOUND=1
            )
        )
    )
)

if !CUDA_FOUND! equ 1 (
    echo [OK] CUDA found at: !CUDA_INSTALL_PATH!
) else (
    echo [!] CUDA not found in standard locations
)
echo.

echo [2/4] Searching for FFmpeg...
echo.

REM Check if ffmpeg is in PATH
where ffmpeg >nul 2>nul
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('where ffmpeg 2^>nul') do (
        if !FFMPEG_FOUND! equ 0 (
            set "FFMPEG_FULL_PATH=%%i"
            for %%j in ("%%i") do set "FFMPEG_PATH=%%~dpj"
            set FFMPEG_FOUND=1
        )
    )
)

REM If not in PATH, check common locations
if !FFMPEG_FOUND! equ 0 (
    echo FFmpeg not in PATH, checking common locations...

    REM Check common installation directories
    for %%p in (
        "C:\ffmpeg\bin"
        "C:\Program Files\ffmpeg\bin"
        "C:\Program Files (x86)\ffmpeg\bin"
        "%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source*\ffmpeg*\bin"
        "%ProgramFiles%\ffmpeg\bin"
    ) do (
        if exist %%p (
            if exist "%%~p\ffmpeg.exe" (
                if !FFMPEG_FOUND! equ 0 (
                    set "FFMPEG_PATH=%%~p"
                    set "FFMPEG_FULL_PATH=%%~p\ffmpeg.exe"
                    set FFMPEG_FOUND=1
                )
            )
        )
    )

    REM Check WinGet packages location (expanded)
    if exist "%LOCALAPPDATA%\Microsoft\WinGet\Packages" (
        for /d %%d in ("%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*") do (
            if exist "%%d" (
                for /f "tokens=*" %%f in ('dir /s /b "%%d\ffmpeg.exe" 2^>nul') do (
                    if !FFMPEG_FOUND! equ 0 (
                        set "FFMPEG_FULL_PATH=%%f"
                        for %%x in ("%%f") do set "FFMPEG_PATH=%%~dpx"
                        set FFMPEG_FOUND=1
                    )
                )
            )
        )
    )
)

if !FFMPEG_FOUND! equ 1 (
    REM Remove trailing backslash
    if "!FFMPEG_PATH:~-1!"=="\" set "FFMPEG_PATH=!FFMPEG_PATH:~0,-1!"
    echo [OK] FFmpeg found at: !FFMPEG_FULL_PATH!
    echo [OK] FFmpeg bin directory: !FFMPEG_PATH!
) else (
    echo [!] FFmpeg not found
)
echo.

echo [3/4] Checking current environment variables...
echo.
echo Current settings:
echo   CUDA_HOME = %CUDA_HOME%
echo   CUDA_PATH = %CUDA_PATH%
echo.

echo [4/4] Checking PATH variable...
echo   (Checking if CUDA and FFmpeg are in PATH...)
where nvcc >nul 2>nul
if %errorlevel% equ 0 (
    echo   [OK] nvcc (CUDA compiler) found in PATH
) else (
    echo   [!] nvcc (CUDA compiler) NOT in PATH
)

where ffmpeg >nul 2>nul
if %errorlevel% equ 0 (
    echo   [OK] ffmpeg found in PATH
) else (
    echo   [!] ffmpeg NOT in PATH
)
echo.

echo ============================================
echo    COPY-PASTE INSTRUCTIONS
echo ============================================
echo.

if !CUDA_FOUND! equ 1 (
    echo STEP 1: Add these SYSTEM ENVIRONMENT VARIABLES:
    echo -----------------------------------------------
    echo.
    echo Variable Name: CUDA_HOME
    echo Value to copy: !CUDA_INSTALL_PATH!
    echo.
    echo Variable Name: CUDA_PATH
    echo Value to copy: !CUDA_INSTALL_PATH!
    echo.
    echo.
) else (
    echo [!] CUDA not found - skipping CUDA variables
    echo.
)

echo STEP 2: Add these to your PATH variable:
echo -----------------------------------------------
echo (Edit the PATH variable and add each line as a new entry)
echo.

if !CUDA_FOUND! equ 1 (
    echo Copy this line:
    echo !CUDA_INSTALL_PATH!\bin
    echo.
    echo Copy this line:
    echo !CUDA_INSTALL_PATH!\libnvvp
    echo.
)

if !FFMPEG_FOUND! equ 1 (
    echo Copy this line:
    echo !FFMPEG_PATH!
    echo.
) else (
    echo [!] FFmpeg not found - install it first with: winget install ffmpeg
    echo.
)

echo.
echo ============================================
echo    HOW TO SET ENVIRONMENT VARIABLES
echo ============================================
echo.
echo 1. Press Win + X
echo 2. Select "System"
echo 3. Click "Advanced system settings" (on the right)
echo 4. Click "Environment Variables" button (at bottom)
echo.
echo 5. Under "System variables" section:
echo    - Click "New" to add CUDA_HOME and CUDA_PATH
echo    - Select "Path" and click "Edit" to add the paths above
echo    - Click "New" for each path entry
echo.
echo 6. Click OK on all dialogs
echo 7. RESTART your terminal/command prompt
echo.

REM Create a text file with the values for easy copying
echo Creating paths.txt with all values for easy copying...
echo.

(
    echo ============================================
    echo   Environment Variable Values
    echo ============================================
    echo.
    if !CUDA_FOUND! equ 1 (
        echo CUDA_HOME:
        echo !CUDA_INSTALL_PATH!
        echo.
        echo CUDA_PATH:
        echo !CUDA_INSTALL_PATH!
        echo.
    )
    echo ============================================
    echo   PATH Entries to Add
    echo ============================================
    echo.
    if !CUDA_FOUND! equ 1 (
        echo !CUDA_INSTALL_PATH!\bin
        echo !CUDA_INSTALL_PATH!\libnvvp
    )
    if !FFMPEG_FOUND! equ 1 (
        echo !FFMPEG_PATH!
    )
    echo.
) > paths.txt

echo [OK] Created paths.txt - open it to copy the values easily!
echo.

pause
