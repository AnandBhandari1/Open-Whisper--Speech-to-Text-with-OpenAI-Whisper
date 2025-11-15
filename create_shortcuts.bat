@echo off
setlocal enabledelayedexpansion

echo ============================================
echo    FastSimple - Create Windows Shortcuts
echo ============================================
echo.

REM Get the current directory (project directory)
set "PROJECT_DIR=%~dp0"
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

REM Path to the launcher
set "LAUNCHER=%PROJECT_DIR%\run_win.bat"

REM Check if launcher exists
if not exist "%LAUNCHER%" (
    echo [ERROR] run_win.bat not found!
    echo Please run this script from the FastSimple directory.
    pause
    exit /b 1
)

echo Current project directory:
echo %PROJECT_DIR%
echo.

REM Create shortcuts using PowerShell
echo Creating shortcuts...
echo.

REM 1. Desktop Shortcut
echo [1/3] Creating Desktop shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\FastSimple.lnk'); $Shortcut.TargetPath = '%LAUNCHER%'; $Shortcut.WorkingDirectory = '%PROJECT_DIR%'; $Shortcut.Description = 'FastSimple - Speech to Text'; $Shortcut.Save()"

if exist "%USERPROFILE%\Desktop\FastSimple.lnk" (
    echo [OK] Desktop shortcut created
) else (
    echo [!] Failed to create Desktop shortcut
)

REM 2. Start Menu Shortcut
echo [2/3] Creating Start Menu shortcut...

REM Create Start Menu folder if it doesn't exist
if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\FastSimple" (
    mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\FastSimple"
)

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\FastSimple\FastSimple.lnk'); $Shortcut.TargetPath = '%LAUNCHER%'; $Shortcut.WorkingDirectory = '%PROJECT_DIR%'; $Shortcut.Description = 'FastSimple - Speech to Text'; $Shortcut.Save()"

if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\FastSimple\FastSimple.lnk" (
    echo [OK] Start Menu shortcut created
) else (
    echo [!] Failed to create Start Menu shortcut
)

REM 3. Create shortcut to open project folder
echo [3/3] Creating 'Open Project Folder' shortcut in Start Menu...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\FastSimple\Open Project Folder.lnk'); $Shortcut.TargetPath = '%PROJECT_DIR%'; $Shortcut.Description = 'Open FastSimple Project Folder'; $Shortcut.Save()"

if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\FastSimple\Open Project Folder.lnk" (
    echo [OK] Project folder shortcut created
) else (
    echo [!] Failed to create project folder shortcut
)

echo.
echo ============================================
echo [OK] Shortcuts created successfully!
echo ============================================
echo.
echo You can now access FastSimple from:
echo   1. Desktop - Double-click 'FastSimple' icon
echo   2. Start Menu - Search for 'FastSimple'
echo   3. Win + S, type 'FastSimple'
echo.

REM Optional: Pin to Start
echo.
echo NOTE: To pin to Start Menu or Taskbar:
echo   1. Right-click the Desktop shortcut
echo   2. Select 'Pin to Start' or 'Pin to taskbar'
echo.

pause
