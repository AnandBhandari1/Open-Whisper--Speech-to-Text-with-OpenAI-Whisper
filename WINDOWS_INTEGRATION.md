# FastSimple - Windows Integration Guide

How to integrate FastSimple into Windows like a native app.

## Quick Setup (Automatic)

Run this once to create all shortcuts:

```batch
create_shortcuts.bat
```

This creates:
- ✅ Desktop shortcut
- ✅ Start Menu entry
- ✅ Searchable from Windows Search (Win + S)

## What You Get

### 1. Desktop Shortcut
- Icon on your desktop: **FastSimple**
- Double-click to launch

### 2. Start Menu
- Search "FastSimple" in Start Menu
- Or browse: All Apps → FastSimple

### 3. Windows Search
- Press `Win + S`
- Type "FastSimple"
- Click to launch

### 4. Project Folder Access
- In Start Menu: "FastSimple" → "Open Project Folder"
- Quick access to files

## Manual Installation

If you prefer to do it manually:

### Create Desktop Shortcut

1. Right-click Desktop → New → Shortcut
2. Location: `C:\Users\YourName\Documents\myprojects\fast_simple\run_win.bat`
3. Name: `FastSimple`
4. Click Finish

### Add to Start Menu

1. Copy the desktop shortcut
2. Open: `%APPDATA%\Microsoft\Windows\Start Menu\Programs`
3. Create folder: `FastSimple`
4. Paste the shortcut inside

## Advanced Options

### Pin to Start Menu

1. Find the Desktop shortcut
2. Right-click → "Pin to Start"

### Pin to Taskbar

1. Find the Desktop shortcut
2. Right-click → "Pin to taskbar"

### Launch at Startup (Auto-start)

If you want FastSimple to auto-start when Windows boots:

1. Press `Win + R`
2. Type: `shell:startup`
3. Press Enter
4. Copy the FastSimple shortcut into this folder

**Note:** The app will auto-start every time you login.

### Silent Launch (No Console Window)

Use the VBScript launcher for a cleaner experience:

**Option 1: Create shortcut to VBS file**
1. Right-click Desktop → New → Shortcut
2. Location: `C:\Users\YourName\Documents\myprojects\fast_simple\FastSimple.vbs`
3. Name: `FastSimple (Silent)`

**Option 2: Update existing shortcuts**
Edit `create_shortcuts.bat` to use `FastSimple.vbs` instead of `run_win.bat`

**Benefits:**
- No command prompt window
- Cleaner user experience
- Same functionality

## Remove Integration

To remove all shortcuts:

```batch
remove_shortcuts.bat
```

Or manually:
- Delete Desktop shortcut
- Delete Start Menu folder: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\FastSimple`

## Custom Keyboard Shortcut

You can assign a global keyboard shortcut (like Ctrl+Alt+F):

1. Right-click the Desktop shortcut
2. Click "Properties"
3. Click in "Shortcut key" field
4. Press your desired key combination (e.g., Ctrl+Alt+F)
5. Click OK

Now press `Ctrl+Alt+F` from anywhere to launch FastSimple!

**Note:** F8 is still for recording, this is just to launch the app.

## Add Custom Icon

To make it look more professional:

### If you have an icon file (.ico)

1. Right-click the shortcut
2. Properties → "Change Icon"
3. Browse to your .ico file
4. Click OK

### Create an icon from image

1. Get a PNG/JPG image (256x256 recommended)
2. Use online converter: https://convertio.co/png-ico/
3. Save the .ico file in project folder
4. Follow steps above to apply it

### Use Windows default icons

1. Right-click shortcut → Properties
2. "Change Icon"
3. Browse to: `C:\Windows\System32\shell32.dll`
4. Pick an icon
5. Click OK

## Run as Administrator

If you need admin privileges:

1. Right-click shortcut
2. Properties → Advanced
3. ✅ Check "Run as administrator"
4. Click OK

**Note:** Usually not needed for FastSimple.

## Send To Menu Integration

Add FastSimple to the "Send To" context menu:

1. Press `Win + R`
2. Type: `shell:sendto`
3. Press Enter
4. Copy FastSimple shortcut here

Now you can right-click any file → Send To → FastSimple

**Note:** This doesn't do anything special, but it's there if needed.

## Create Taskbar Shortcut

### Method 1: Pin existing shortcut
1. Create desktop shortcut first
2. Right-click → "Pin to taskbar"

### Method 2: Drag and drop
1. Open File Explorer
2. Navigate to project folder
3. Drag `run_win.bat` to taskbar

## Windows Terminal Integration

Add FastSimple to Windows Terminal profiles:

1. Open Windows Terminal
2. Settings (Ctrl + ,)
3. Add new profile:

```json
{
    "name": "FastSimple",
    "commandline": "cmd.exe /k \"cd C:\\Users\\YourName\\Documents\\myprojects\\fast_simple && run_win.bat\"",
    "icon": "C:\\Users\\YourName\\Documents\\myprojects\\fast_simple\\icon.ico",
    "startingDirectory": "C:\\Users\\YourName\\Documents\\myprojects\\fast_simple"
}
```

## File Association (Advanced)

Associate audio files with FastSimple for transcription:

**Not recommended** - FastSimple is for live recording, not file transcription.

## Uninstall

To completely remove FastSimple from Windows:

1. Run `remove_shortcuts.bat`
2. Delete project folder
3. Remove from Startup folder (if added)
4. Unpin from taskbar/start (if pinned)

## Verification

After running `create_shortcuts.bat`, verify:

```batch
# Check Desktop shortcut
dir "%USERPROFILE%\Desktop\FastSimple.lnk"

# Check Start Menu
dir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\FastSimple"

# Test search
# Press Win + S, type "FastSimple"
```

## Troubleshooting

### Shortcut doesn't work

1. Right-click shortcut → Properties
2. Check "Target" path is correct
3. Check "Start in" points to project folder
4. Click OK

### "Access Denied" when creating shortcuts

Run `create_shortcuts.bat` as Administrator:
1. Right-click `create_shortcuts.bat`
2. "Run as administrator"

### Shortcut opens wrong folder

Edit the shortcut:
1. Right-click → Properties
2. Change "Start in" to project folder
3. Click OK

### Can't find shortcut in Start Menu

1. Restart Windows Explorer:
   - Press Ctrl+Shift+Esc
   - Find "Windows Explorer"
   - Right-click → Restart

2. Or run:
   ```batch
   taskkill /f /im explorer.exe
   start explorer.exe
   ```

## Scripts Reference

| Script | Purpose |
|--------|---------|
| **create_shortcuts.bat** | Create all shortcuts (run once) |
| **remove_shortcuts.bat** | Remove all shortcuts |
| **FastSimple.vbs** | Silent launcher (no console) |
| **run_win.bat** | Regular launcher (with console) |
| **start.bat** | Simple launcher |

## Best Practices

1. **Use Start Menu** - Most convenient for daily use
2. **Pin to Taskbar** - If you use it frequently
3. **Use VBS launcher** - For cleaner experience (no console)
4. **Don't add to Startup** - Unless you need it at boot
5. **Create custom shortcut key** - For quick access

## Example Workflow

**After installation:**

1. Run `create_shortcuts.bat` once
2. Press Win + S
3. Type "FastSimple"
4. Pin to Start or Taskbar (optional)
5. Close terminal

**Daily use:**
- Click Start → FastSimple
- OR press Win + S → type "fast" → Enter
- OR use custom keyboard shortcut (if set)
- App opens → Press F8 to record

## Files Created

After running `create_shortcuts.bat`:

```
Desktop:
├── FastSimple.lnk          → Points to run_win.bat

Start Menu:
└── %APPDATA%\Microsoft\Windows\Start Menu\Programs\FastSimple\
    ├── FastSimple.lnk      → Points to run_win.bat
    └── Open Project Folder.lnk  → Opens project folder
```

## Quick Commands

```batch
# Create shortcuts
create_shortcuts.bat

# Remove shortcuts
remove_shortcuts.bat

# Launch app (silent)
FastSimple.vbs

# Launch app (with console)
run_win.bat

# Launch app (minimal)
start.bat

# Open project folder
explorer .
```

---

**Recommended Setup:**
1. Run `create_shortcuts.bat`
2. Search for "FastSimple" in Start Menu
3. Right-click → Pin to Start (or Taskbar)
4. Delete desktop shortcut if you don't need it
5. Done! Access from Start Menu or taskbar.

**For cleanest experience:**
- Use `FastSimple.vbs` instead of `run_win.bat` in shortcuts
- No console window will appear
- App just launches silently

---

**Last Updated:** 2025-11-15
