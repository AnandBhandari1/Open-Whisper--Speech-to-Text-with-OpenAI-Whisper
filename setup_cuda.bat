@echo off
setlocal enabledelayedexpansion

echo ============================================
echo    CUDA Setup Helper for FastSimple
echo ============================================
echo.

REM Check for NVIDIA GPU
echo Checking for NVIDIA GPU...
where nvidia-smi >nul 2>nul
if %errorlevel% neq 0 (
    echo [X] nvidia-smi not found - NVIDIA drivers may not be installed
    echo Please install NVIDIA drivers first: https://www.nvidia.com/download/index.aspx
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('nvidia-smi --query-gpu^=name --format^=csv^,noheader 2^>nul') do (
    echo [OK] Found GPU: %%i
)
echo.

REM Check current CUDA environment variables
echo Current CUDA environment variables:
echo -----------------------------------
if defined CUDA_HOME (
    echo CUDA_HOME = %CUDA_HOME%
) else (
    echo CUDA_HOME = [NOT SET]
)

if defined CUDA_PATH (
    echo CUDA_PATH = %CUDA_PATH%
) else (
    echo CUDA_PATH = [NOT SET]
)
echo.

REM Try to find CUDA installation
echo Searching for CUDA installation...
set CUDA_FOUND=0
set CUDA_INSTALL_PATH=

if exist "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA" (
    echo [OK] Found CUDA toolkit directory
    echo.
    echo Available CUDA versions:
    dir /b "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA" 2>nul
    echo.

    REM Try to find the newest version
    for /f %%i in ('dir /b /o-n "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA" 2^>nul') do (
        if !CUDA_FOUND! equ 0 (
            set CUDA_INSTALL_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\%%i
            set CUDA_VERSION=%%i
            set CUDA_FOUND=1
        )
    )

    if !CUDA_FOUND! equ 1 (
        echo Recommended CUDA path: !CUDA_INSTALL_PATH!
        echo.
    )
) else (
    echo [!] CUDA toolkit not found in standard location
    echo If you have CUDA installed elsewhere, note its path
    echo.
)

REM Check if CUDA is in PATH
echo Checking if CUDA is in PATH...
where nvcc >nul 2>nul
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('nvcc --version 2^>nul ^| findstr "release"') do (
        echo [OK] nvcc found in PATH: %%i
    )
) else (
    echo [!] nvcc not found in PATH
)
echo.

REM Check PyTorch CUDA availability
echo Checking PyTorch CUDA detection...
where python >nul 2>nul
if %errorlevel% equ 0 (
    python -c "import torch; print(f'PyTorch version: {torch.__version__}'); cuda = torch.cuda.is_available(); print(f'CUDA available: {cuda}'); print(f'CUDA version (PyTorch): {torch.version.cuda}' if cuda else 'CPU mode'); print(f'GPU: {torch.cuda.get_device_name(0)}' if cuda else '')" 2>nul
    if !errorlevel! neq 0 (
        echo [!] Could not check PyTorch (may not be installed yet)
    )
) else (
    echo [!] Python not found in PATH
)
echo.

echo ============================================
echo.
echo MANUAL SETUP INSTRUCTIONS:
echo -----------------------------------
echo.
echo If CUDA_HOME is not set, follow these steps:
echo.
echo 1. Press Win + X, select "System"
echo 2. Click "Advanced system settings"
echo 3. Click "Environment Variables"
echo 4. Under "System variables", click "New":
echo    - Variable: CUDA_HOME
if defined CUDA_INSTALL_PATH (
    echo    - Value: !CUDA_INSTALL_PATH!
) else (
    echo    - Value: [Your CUDA installation path]
)
echo.
echo 5. Add another variable:
echo    - Variable: CUDA_PATH
if defined CUDA_INSTALL_PATH (
    echo    - Value: !CUDA_INSTALL_PATH!
) else (
    echo    - Value: [Same as CUDA_HOME]
)
echo.
echo 6. Edit the "Path" variable and add these entries:
echo    - %%CUDA_HOME%%\bin
echo    - %%CUDA_HOME%%\libnvvp
echo.
echo 7. Click OK on all dialogs
echo 8. RESTART your command prompt/terminal
echo 9. Run setup.bat again
echo.
echo ============================================
echo.

REM Offer to set for current session only
if !CUDA_FOUND! equ 1 (
    echo.
    echo Would you like to set CUDA variables for THIS SESSION ONLY?
    echo This is temporary and for testing - you still need to set them permanently.
    echo.
    choice /C YN /M "Set CUDA_HOME for this session"
    if !errorlevel! equ 1 (
        set "CUDA_HOME=!CUDA_INSTALL_PATH!"
        set "CUDA_PATH=!CUDA_INSTALL_PATH!"
        set "PATH=!CUDA_INSTALL_PATH!\bin;!CUDA_INSTALL_PATH!\libnvvp;!PATH!"
        echo.
        echo [OK] CUDA variables set for this session:
        echo CUDA_HOME = !CUDA_HOME!
        echo CUDA_PATH = !CUDA_PATH!
        echo.
        echo You can now run setup.bat in this same window.
        echo Remember to set these permanently using the instructions above.
        echo.
    )
)

pause
