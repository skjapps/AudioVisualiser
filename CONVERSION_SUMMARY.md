# Audio Visualiser - Linux Conversion Summary

## Overview
Successfully converted the Windows-based audiovisualiser to work on Linux (including WSL) by replacing Windows-specific audio capture and window management with cross-platform alternatives.

## Files Created

### 1. Audio/PyAudioWrapperLinux.py
**Purpose**: Linux-compatible audio capture using PulseAudio/PipeWire

**Key Features**:
- Uses standard PyAudio instead of pyaudiowpatch
- Automatically detects PulseAudio monitor devices
- Falls back to pactl commands to find default sink monitors
- Compatible with both PulseAudio and PipeWire (via compatibility layer)
- Handles mono/stereo audio conversion

**Technical Details**:
- Searches for "monitor" or "loopback" devices
- Uses `pactl get-default-sink` to find system audio output
- Appends `.monitor` to sink name to find capture source
- Graceful fallback to best available input device

### 2. Default/AudioVisualiserLinux.py
**Purpose**: Linux-compatible main application file

**Changes from Windows Version**:
- Removed win32api, win32con, win32gui imports
- Platform detection for audio wrapper selection
- Linux-compatible `getIdleTime()` using xprintidle
- Simplified transparency function (notes compositor requirement)
- Updated fullscreen handling for Linux
- Fixed file path handling (removed backslashes)
- Added proper error handling for missing resources
- Platform-aware DPI handling

### 3. main_linux.py
**Purpose**: Entry point for Linux version

**Features**:
- Platform detection (automatically uses Linux version on non-Windows)
- Can still use Windows version if run on Windows
- Clean separation of concerns

### 4. requirements-linux.txt
**Purpose**: Linux-specific Python dependencies

**Packages**:
- requests (HTTP library)
- numpy (numerical computations)
- pygame-ce (cross-platform game library)
- spotipy (Spotify API wrapper)
- Pillow (image processing)
- PyAudio (audio I/O)

**Removed from Windows version**:
- pyaudiowpatch (Windows-only)
- winsdk (Windows-only)
- pywin32 (Windows-only)

### 5. setup_linux.sh
**Purpose**: Automated setup script for Linux/WSL

**Features**:
- Detects WSL vs native Linux
- Detects package manager (apt, dnf, pacman)
- Installs system dependencies automatically
- Sets up PulseAudio/PipeWire
- Creates Python virtual environment
- Installs Python packages
- Configures WSL-specific settings
- Tests audio devices
- Provides helpful next steps

**System Dependencies Installed**:
- Python development headers
- PortAudio (audio library)
- PulseAudio/PipeWire
- SDL2 libraries (for pygame)
- Image libraries (JPEG, PNG, FreeType)
- Build tools
- xprintidle (idle time detection)

### 6. README_LINUX.md
**Purpose**: Comprehensive Linux documentation

**Sections**:
- Changes from Windows version
- System requirements
- Installation instructions (automated + manual)
- Audio setup and configuration
- WSL-specific setup
- Keyboard shortcuts
- Configuration guide
- Troubleshooting
- Known limitations
- Development info

### 7. QUICKSTART_LINUX.md
**Purpose**: Quick reference for getting started

**Content**:
- Two setup options (automated/manual)
- Audio setup instructions
- Basic controls
- Common troubleshooting
- Quick tips

## Key Technical Changes

### Audio Capture
**Windows (Original)**:
```python
import pyaudiowpatch as pyaudio
# Uses WASAPI loopback device
```

**Linux (New)**:
```python
import pyaudio
# Uses PulseAudio/PipeWire monitor sources
```

### Window Transparency
**Windows (Original)**:
```python
import win32gui, win32api, win32con
win32gui.SetLayeredWindowAttributes(...)
```

**Linux (New)**:
```python
# Simplified - requires compositor
print("Transparency requires compositor (Picom, KWin, etc.)")
```

### Idle Time Detection
**Windows (Original)**:
```python
import win32api
idle = (win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000.0
```

**Linux (New)**:
```python
import subprocess
result = subprocess.run(['xprintidle'], capture_output=True)
idle = int(result.stdout.strip()) / 1000.0
```

### DPI Awareness
**Windows (Original)**:
```python
ctypes.windll.user32.SetProcessDPIAware()
```

**Linux (New)**:
```python
# Not needed - handled by SDL2/pygame
```

## Audio Architecture

### PulseAudio Flow
```
System Audio Output → Default Sink → Monitor Source → PyAudio → App
```

### PipeWire Flow
```
System Audio Output → PipeWire Node → PulseAudio Compat → Monitor → PyAudio → App
```

## Platform Compatibility

### Tested On
- ✅ WSL2 (Ubuntu 22.04)
- ✅ Native Ubuntu 20.04+
- ✅ Debian-based distributions
- ⚠️ Should work on Fedora/Arch (untested)

### Requirements
- **OS**: Linux kernel 4.x+, WSL2
- **Python**: 3.8+
- **Audio**: PulseAudio 12.0+ or PipeWire 0.3+
- **Display**: X11 or Wayland (WSLg)

## Installation Methods

### Method 1: Automated (Recommended)
```bash
./setup_linux.sh
source venv/bin/activate
python3 main_linux.py
```

### Method 2: Manual
```bash
# Install system packages
sudo apt-get install python3-dev portaudio19-dev pulseaudio ...

# Setup Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-linux.txt

# Run
python3 main_linux.py
```

## Audio Configuration

### Essential Setup
```bash
# Start PulseAudio
pulseaudio --start

# Load loopback module
pactl load-module module-loopback

# List monitor sources
pactl list sources short | grep monitor
```

### Using pavucontrol (GUI)
1. Run app: `python3 main_linux.py`
2. Open mixer: `pavucontrol`
3. Go to "Recording" tab
4. Select monitor source for the app

## WSL-Specific Configuration

### WSL2 with WSLg (Best)
- GUI and audio work out-of-the-box
- No additional configuration needed
- Best performance

### WSL2 without WSLg
- Requires X server on Windows (VcXsrv, Xming)
- Set DISPLAY environment variable
- Audio may need additional setup

### WSL1
- Limited support
- Recommend upgrading to WSL2

## Features Status

| Feature | Windows | Linux | Notes |
|---------|---------|-------|-------|
| Audio Visualization | ✅ | ✅ | Via PulseAudio monitors |
| FFT Analysis | ✅ | ✅ | Unchanged |
| Oscilloscope | ✅ | ✅ | Unchanged |
| GIF Backgrounds | ✅ | ✅ | Unchanged |
| Window Transparency | ✅ | ⚠️ | Requires compositor |
| Always-on-Top | ✅ | ⚠️ | WM-dependent |
| Spotify Integration | ✅ | ✅ | Via API |
| Windows SDK Media | ✅ | ❌ | Windows-only |
| Idle Detection | ✅ | ✅ | Via xprintidle |

## Known Limitations

1. **Transparency**: Not fully transparent without compositor
2. **Always-on-top**: Depends on window manager support
3. **WSL Audio**: May require manual configuration
4. **Media Integration**: No Windows SDK support

## Troubleshooting Guide

### No Audio
```bash
# Check PulseAudio
pulseaudio --check && echo "Running" || pulseaudio --start

# Use pavucontrol
pavucontrol  # Select monitor in Recording tab
```

### Import Errors
```bash
# Reinstall dependencies
pip uninstall pyaudio
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### Display Issues (WSL)
```bash
# Verify display
echo $DISPLAY  # Should show value like ":0"

# Test with simple app
xeyes
```

## Performance Optimization

1. **Lower CHUNK size** in config.cfg (faster response)
2. **Reduce NumOfBars** (better FPS)
3. **Disable GIF backgrounds** (lower CPU usage)
4. **Use native resolution** (better performance)

## Future Improvements

Potential enhancements:
- [ ] Native PipeWire API support (bypass PulseAudio compat)
- [ ] Jack audio server support
- [ ] Wayland native window management
- [ ] MPRIS integration for media info (Linux standard)
- [ ] systemd service file for background running
- [ ] AppImage or Flatpak packaging

## Testing Checklist

- [x] Audio capture from system audio
- [x] FFT visualization works
- [x] Oscilloscope displays waveform
- [x] Window resizing works
- [x] Fullscreen toggle works
- [x] Keyboard shortcuts functional
- [x] Configuration file loads correctly
- [x] Virtual environment setup
- [x] Dependency installation
- [ ] Spotify integration (requires API credentials)
- [ ] Multiple audio device switching
- [ ] Long-term stability testing

## Version Information

- **Original**: Windows-only (pyaudiowpatch + win32 APIs)
- **Linux Port**: Cross-platform (PyAudio + PulseAudio/PipeWire)
- **Compatibility**: Can run on both Windows and Linux

## Credits

- Original project: https://github.com/skjapps/audiovisualiser
- Linux adaptation: PulseAudio/PipeWire audio capture implementation
- WSL support: Tested on WSL2 with WSLg

---

## Quick Command Reference

```bash
# Setup
./setup_linux.sh

# Activate environment
source venv/bin/activate

# Run application
python3 main_linux.py

# Audio control
pavucontrol                                  # GUI mixer
pactl list sources short                     # List audio sources
pactl load-module module-loopback            # Enable loopback
pulseaudio -k && pulseaudio --start          # Restart audio

# Troubleshooting
pip install -r requirements-linux.txt        # Reinstall Python deps
sudo apt-get install portaudio19-dev         # Install audio libs
echo $DISPLAY                                # Check display (WSL)
```
