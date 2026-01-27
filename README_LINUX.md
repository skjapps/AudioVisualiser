# Audio Visualiser - Linux/WSL Version

This is a Linux-compatible version of the Audio Visualiser that uses PulseAudio/PipeWire for system audio capture instead of Windows-specific libraries.

## 🚀 Quick Start

**New to Linux setup?** See [QUICKSTART_LINUX.md](QUICKSTART_LINUX.md) for the simplest installation steps!

```bash
# Ubuntu/Debian quick install:
sudo apt-get install -y python3-dev python3-venv python3-tk portaudio19-dev pulseaudio pavucontrol
python3 -m venv venv
venv/bin/pip install -r requirements-linux.txt
venv/bin/python3 main_linux.py
```

---

## Changes from Windows Version

### Audio Capture
- **Replaced**: `pyaudiowpatch` (Windows WASAPI loopback)
- **With**: `PyAudio` with PulseAudio/PipeWire monitor sources
- **New file**: `Audio/PyAudioWrapperLinux.py` - Linux-compatible audio wrapper

### Window Management
- **Removed**: Windows-specific transparency using `win32gui`, `win32api`, `win32con`
- **Replaced**: Platform-independent window handling
- **Note**: Full transparency requires a compositor (Picom, Compton, KWin, etc.)

### Dependencies
- **Removed**: `pyaudiowpatch`, `winsdk`, `pywin32`
- **Added**: `PyAudio` (with PulseAudio/PipeWire support)

### Other Changes
- Cross-platform idle time detection (uses `xprintidle` on Linux)
- Modified fullscreen handling for Linux
- Updated file paths to use forward slashes
- Platform detection to load appropriate modules

## Requirements

### System Dependencies
- Python 3.8+
- PulseAudio or PipeWire (with PulseAudio compatibility layer)
- SDL2 libraries
- PortAudio
- Build tools (gcc, make)

### For WSL (Windows Subsystem for Linux)
- WSL2 recommended
- WSLg for GUI support (included in Windows 11 or Windows 10 with recent updates)
- PulseAudio or PipeWire for audio

## Installation

### Quick Setup (Recommended)
Run the automated setup script:
```bash
chmod +x setup_linux.sh
./setup_linux.sh
```

### Manual Setup

1. **Install system dependencies** (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip portaudio19-dev \
    libportaudio2 pulseaudio pulseaudio-utils pavucontrol \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libfreetype6-dev libjpeg-dev libpng-dev xprintidle build-essential
```

2. **For Fedora/RHEL**:
```bash
sudo dnf install python3-devel portaudio-devel pulseaudio \
    pulseaudio-utils pavucontrol SDL2-devel SDL2_image-devel \
    SDL2_mixer-devel SDL2_ttf-devel freetype-devel gcc make
```

3. **For Arch Linux**:
```bash
sudo pacman -S python python-pip portaudio pulseaudio pavucontrol \
    sdl2 sdl2_image sdl2_mixer sdl2_ttf base-devel xprintidle
```

4. **Create Python virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate
```

5. **Install Python dependencies**:
```bash
pip install --upgrade pip
pip install -r requirements-linux.txt
```

## Audio Setup

### PulseAudio Configuration
The application captures system audio using PulseAudio monitor sources (loopback devices).

1. **Start PulseAudio** (if not running):
```bash
pulseaudio --start
```

2. **Load loopback module** (for audio capture):
```bash
pactl load-module module-loopback
```

3. **List available audio sources**:
```bash
pactl list sources short
```

Look for sources with "monitor" in the name - these are what the app will use to capture system audio.

### PipeWire Configuration
If using PipeWire (modern Linux distributions):

```bash
# PipeWire provides PulseAudio compatibility automatically
# Check if PipeWire is running
systemctl --user status pipewire pipewire-pulse

# List audio devices
pw-cli list-objects | grep -A 10 "node.name"
```

### Audio Troubleshooting

**No audio detected?**
```bash
# Use PulseAudio Volume Control GUI
pavucontrol
# Go to "Recording" tab while app is running
# Select the monitor source for your speakers
```

**Monitor device not found?**
```bash
# Create a null sink with monitor
pactl load-module module-null-sink sink_name=visualiser
pactl load-module module-loopback source=visualiser.monitor
```

**Restart audio server**:
```bash
pulseaudio -k && pulseaudio --start
```

## WSL-Specific Setup

### WSL2 with WSLg (Recommended)
Windows 11 and recent Windows 10 updates include WSLg for native GUI and audio support.

1. **Update WSL**:
```powershell
# In PowerShell (Windows)
wsl --update
```

2. **Verify WSLg**:
```bash
# In WSL
echo $DISPLAY
echo $WAYLAND_DISPLAY
# Should show a display value
```

3. **Test audio**:
```bash
speaker-test -t wav -c 2
```

### WSL2 without WSLg
If WSLg is not available:

1. **Install VcXsrv or Xming** on Windows
2. **Set DISPLAY variable**:
```bash
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
```

3. **Add to ~/.bashrc**:
```bash
echo 'export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '\''{print $2}'\''):0' >> ~/.bashrc
```

### WSL1
WSL1 has limited audio support. Consider upgrading to WSL2:
```powershell
# Convert existing WSL1 distro to WSL2
wsl --set-version <distro-name> 2
```

## Running the Application

1. **Activate virtual environment**:
```bash
source venv/bin/activate
```

2. **Run the application**:
```bash
python3 main_linux.py
```

## Keyboard Shortcuts

- **Q** - Quit application
- **R** - Reload/reinitialize audio device
- **O** - Open options menu
- **F4** - Toggle fullscreen
- **G** - Toggle oscilloscope gain normalization
- **Left/Right arrows** - Change font
- **+/- (with number keys)** - Adjust various options
  - Press 1-9 to select option category, then +/- to adjust

## Configuration

Edit `config.cfg` to customize:
- Audio settings (chunk size, sample rate)
- Visual appearance (colors, bar count, styles)
- Window settings (resolution, fullscreen, frameless)
- Media integration (Spotify, etc.)

**Important for Linux**: Set `media_mode` to `None` or `Spotify` in config.cfg. The `winsdk` mode is Windows-only.

## Features Working on Linux

✅ Audio visualization from system audio
✅ FFT-based frequency analysis
✅ Oscilloscope view
✅ Multiple visualization styles
✅ GIF backgrounds
✅ Resizable window
✅ Fullscreen mode
✅ Spotify integration (if configured)
✅ Custom colors and themes

## Known Limitations

⚠️ **Transparency**: Full window transparency requires a compositor (Picom, Compton, KWin effects)
⚠️ **Always-on-top**: Limited support, depends on window manager
⚠️ **WSL audio**: May require additional configuration depending on WSL version
⚠️ **Media controls**: Windows SDK integration not available

## Performance Tips

1. **Lower chunk size** for faster response (may reduce quality)
2. **Reduce bar count** for better performance
3. **Disable GIF backgrounds** if experiencing lag
4. **Use native resolution** instead of fullscreen on lower-end systems

## Troubleshooting

### "No module named 'Audio.PyAudioWrapperLinux'"
Make sure you're running `main_linux.py` instead of `main.py`

### "ImportError: No module named '_portaudio'"
```bash
# Install PortAudio development files
sudo apt-get install portaudio19-dev
# Reinstall PyAudio
pip uninstall pyaudio
pip install pyaudio
```

### Pygame/SDL errors
```bash
# Install SDL2 development libraries
sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
```

### "ALSA lib ... Unknown PCM"
This is a warning from ALSA, usually harmless. To suppress:
```bash
# Create or edit ~/.asoundrc
echo "pcm.!default { type pulse }" >> ~/.asoundrc
echo "ctl.!default { type pulse }" >> ~/.asoundrc
```

### No window appears (WSL)
```bash
# Verify display is set
echo $DISPLAY

# Install and test with xeyes
sudo apt-get install x11-apps
xeyes  # Should show a GUI window
```

## Development

### File Structure
```
audiovisualiser/
├── Audio/
│   ├── PyAudioWrapper.py          # Windows version
│   ├── PyAudioWrapperLinux.py     # Linux version (NEW)
│   └── AudioProcess.py
├── Default/
│   ├── AudioVisualiser.py         # Windows version
│   └── AudioVisualiserLinux.py    # Linux version (NEW)
├── Graphics/
│   └── ... (unchanged)
├── main.py                        # Windows entry point
├── main_linux.py                  # Linux entry point (NEW)
├── requirements.txt               # Windows requirements
├── requirements-linux.txt         # Linux requirements (NEW)
├── setup_linux.sh                 # Linux setup script (NEW)
└── README_LINUX.md               # This file (NEW)
```

## Contributing

When contributing Linux-specific fixes:
1. Test on both native Linux and WSL2
2. Ensure backwards compatibility with Windows version
3. Document any new dependencies
4. Update this README with new features/fixes

## Credits

Original Windows version: https://github.com/skjapps/audiovisualiser
Linux port: Adapted for PulseAudio/PipeWire audio capture

## License

Same as original project.
