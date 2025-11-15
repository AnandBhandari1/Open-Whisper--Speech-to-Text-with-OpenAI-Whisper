@echo off
echo ============================================
echo    FastSimple - Remove Windows Shortcuts
echo ============================================
echo.

REM Remove Desktop shortcut
if exist "%USERPROFILE%\Desktop\FastSimple.lnk" (
    del "%USERPROFILE%\Desktop\FastSimple.lnk"
    echo [OK] Removed Desktop shortcut
) else (
    echo [INFO] Desktop shortcut not found
)

REM Remove Start Menu folder
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\FastSimple" (
    rmdir /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\FastSimple"
    echo [OK] Removed Start Menu shortcuts
) else (
    echo [INFO] Start Menu shortcuts not found
)

echo.
echo ============================================
echo [OK] All shortcuts removed
echo ============================================
echo.
pause
