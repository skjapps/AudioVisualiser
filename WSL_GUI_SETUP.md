# WSL GUI Setup for Audio Visualiser

## TL;DR - Quick Fix

**The window isn't showing?** Here's what to do:

```bash
# 1. Test if WSLg GUI works
./test_wsl.sh

# 2. Fix PulseAudio (run in Windows PowerShell as admin):
wsl --update
wsl --shutdown
# Then restart WSL

# 3. Try running in silent mode (window shows but no audio):
SDL_AUDIODRIVER=dummy venv/bin/python3 main_linux.py
```

## Why the Window Doesn't Show

The pygame app requires two things to work in WSL:
1. **GUI/Display** - to show the window (WSLg or X server)
2. **Audio** - to capture sound (PulseAudio)

If audio fails, the app crashes **before** the window appears, making it seem like the window isn't showing when actually the app crashes during audio initialization.

## The Real Problem: WSLg PulseAudio Issues

WSLg provides PulseAudio at `/mnt/wslg/PulseServer`, but it sometimes refuses connections. This causes the app to crash before creating the window.

### Solution: Updated App with Silent Mode

The app now has failsafe handling - if audio fails, it runs in "silent mode" where the window shows but doesn't visualize audio.

## Problem: Window Not Showing in WSL

If the pygame window doesn't appear, you have a **WSL GUI configuration issue**. Here's how to fix it:

## Solution 1: WSLg (Windows 11 or Windows 10 22H2+)

WSLg is the easiest solution - it's built into modern Windows.

### Check if WSLg is Working:
```bash
# Check if DISPLAY is set
echo $DISPLAY
# Should show something like ":0" or ":1"

# Check if Wayland is available  
echo $WAYLAND_DISPLAY
# Should show something like "wayland-0"

# Test with a simple GUI app
sudo apt-get install -y x11-apps
xeyes
```

If `xeyes` shows a window, WSLg is working! The audio visualiser should work too.

### If WSLg Not Working:

1. **Update WSL** (run in PowerShell/CMD as Administrator):
```powershell
wsl --update
wsl --shutdown
```

2. **Ensure you're using WSL2** (not WSL1):
```powershell
wsl -l -v
# Should show "VERSION 2" next to your distro

# If it shows version 1, upgrade:
wsl --set-version Ubuntu 2
```

3. **Windows version check**: WSLg requires:
   - Windows 11, OR
   - Windows 10 Build 19044+ (run `winver` in Windows to check)

## Solution 2: X Server (VcXsrv) - For Older Windows

If you can't use WSLg, install an X server on Windows:

### Install VcXsrv:
1. Download from: https://sourceforge.net/projects/vcxsrv/
2. Install and run **XLaunch**
3. Choose settings:
   - Display: **Multiple windows**
   - Start no client: **✓**
   - Clipboard: **✓**
   - **Disable access control**: ✓ (IMPORTANT!)

### Configure WSL to Use VcXsrv:
```bash
# Add to ~/.bashrc
echo 'export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk "{print \$2}"):0' >> ~/.bashrc
source ~/.bashrc

# Test
echo $DISPLAY
xeyes  # Should show a window
```

## Solution 3: Fix PulseAudio Timeout

The app is also crashing because PulseAudio can't connect. This is separate from the GUI issue.

### For WSL2 with WSLg:
```bash
# PulseAudio should work automatically
# Check if it's running:
pulseaudio --check && echo "Running" || echo "Not running"

# If not running, start it:
pulseaudio --start

# Or restart it:
pulseaudio -k
pulseaudio --start
```

### For WSL1 or without WSLg:
You'll need PulseAudio server on Windows (more complex). **Alternative**: Run the app with a dummy audio input:

```bash
# Run with SDL audio backend (may work better):
SDL_AUDIODRIVER=dummy venv/bin/python3 main_linux.py
```

## Quick Diagnostic Commands

```bash
# Check WSL version
grep -i microsoft /proc/version

# Check display variables
env | grep -E "DISPLAY|WAYLAND"

# Test GUI
sudo apt-get install -y x11-apps
xeyes

# Check audio
pulseaudio --check && echo "PulseAudio running" || echo "PulseAudio not running"
pactl info 2>/dev/null || echo "PulseAudio not accessible"
```

## Common Issues

### "gio: Operation not supported" when using Spotify
This happens in WSL when the app tries to open a browser for Spotify authentication.

**Fix**: Disable Spotify in `config.cfg`:
```ini
media_mode = None
```

Or manually authenticate:
1. The app will print a URL in the terminal
2. Copy the URL and paste it in a Windows browser
3. After authorizing, copy the redirect URL from the browser
4. Paste it back in the terminal

**Note**: The redirect URI has been updated to use `127.0.0.1:8080` instead of deprecated `localhost:8080`.

### "PulseAudio: Unable to connect: Timeout"
- PulseAudio isn't running or accessible
- **Quick fix**: Start PulseAudio with `pulseaudio --start`
- **Alternative**: Use dummy audio driver (won't capture sound but window will show):
  ```bash
  SDL_AUDIODRIVER=dummy venv/bin/python3 main_linux.py
  ```

### "No window appears at all"
- DISPLAY not set → Configure WSLg or X server (see above)
- Wrong WSL version → Upgrade to WSL2
- Windows too old → Update Windows or use VcXsrv

### "Window flickers and closes immediately"
- App crashed before window fully initialized
- Check terminal output for Python errors
- Try running with verbose output to see where it fails

## Test Plan

1. **First, verify GUI works**:
   ```bash
   sudo apt-get install -y x11-apps
   xeyes  # Should see a window with eyes
   ```

2. **Then verify PulseAudio**:
   ```bash
   pulseaudio --start
   pactl info  # Should show server info
   ```

3. **Finally, run the app**:
   ```bash
   venv/bin/python3 main_linux.py
   ```

## Still Not Working?

Run the app with diagnostic output:
```bash
# Set debug flags
export LIBGL_ALWAYS_INDIRECT=1
export SDL_VIDEODRIVER=x11
export AUDIODEV=pulse

# Run with Python warnings
venv/bin/python3 -W all main_linux.py
```

For more help, check:
- **WSL GUI docs**: https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps
- **PulseAudio WSL**: https://github.com/microsoft/wslg
