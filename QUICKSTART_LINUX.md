# Audio Visualiser - Quick Start Guide (Linux/WSL)

## 🚀 Quick Start

### Simple 3-Step Setup (Ubuntu/Debian)
```bash
# 1. Install system packages
sudo apt-get update
sudo apt-get install -y python3-dev python3-venv python3-tk portaudio19-dev pulseaudio pavucontrol

# 2. Create virtual environment and install Python packages
cd ~/audiovisualiser
python3 -m venv venv
venv/bin/pip install -r requirements-linux.txt

# 3. Run the app
venv/bin/python3 main_linux.py

# Or use the launcher script
./run.sh
```

### Automated Setup (Alternative)
```bash
cd ~/audiovisualiser
chmod +x setup_linux.sh
./setup_linux.sh
source venv/bin/activate
python3 main_linux.py
```

## 💡 Why Not Just `pip install`?

Linux (especially Ubuntu 24.04+) uses "externally-managed environments" to protect system Python packages. You **cannot** run `pip install` directly without using:
- `python3 -m venv venv` (recommended - creates isolated environment)
- OR `--break-system-packages` flag (not recommended - can break your system)

The virtual environment (`venv`) keeps all packages isolated and clean.

## 🔊 Audio Setup (Important!)

The app needs to capture system audio. Here's how:

### During First Run:
1. Start the app: `python3 main_linux.py`
2. Open PulseAudio Volume Control: `pavucontrol`
3. Go to the **"Recording"** tab
4. Find the Python/Audio Visualiser entry
5. Select a **monitor device** (e.g., "Monitor of Built-in Audio Analog Stereo")
6. Play some music and watch it visualize!

### Enable Audio Loopback:
```bash
# Load loopback module (allows capturing system audio)
pactl load-module module-loopback
```

## ⌨️ Controls

- **Q** - Quit
- **R** - Reload audio device
- **F4** - Fullscreen
- **O** - Options
- **Left/Right** - Change font

## 🐛 Troubleshooting

### No audio visualization?
```bash
# Check if PulseAudio is running
pulseaudio --check
pulseaudio --start

# Open audio mixer and select monitor source
pavucontrol
```

### Module import errors?
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# If venv is broken, recreate it
sudo apt-get install -y python3-venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-linux.txt
```

### No window appears (WSL)?
**This is the most common WSL issue!** See **[WSL_GUI_SETUP.md](WSL_GUI_SETUP.md)** for detailed fix.

**Quick checks:**
```bash
# 1. Check if display is configured
echo $DISPLAY  # Should show ":0" or similar

# 2. Test GUI with simple app
sudo apt-get install -y x11-apps
xeyes  # Should show a window with eyes

# 3. If xeyes doesn't work:
#    - Windows 11/10 22H2+: Run 'wsl --update' in PowerShell
#    - Older Windows: Install VcXsrv (see WSL_GUI_SETUP.md)
```

### PulseAudio timeout errors?
```bash
# Start PulseAudio
pulseaudio --start

# Or restart it
pulseaudio -k && pulseaudio --start

# Alternative: Run without audio (just visual)
SDL_AUDIODRIVER=dummy venv/bin/python3 main_linux.py
```

## 📝 Notes

- **Config file**: Edit `config.cfg` to customize settings
- **Media mode**: Use `"None"` or `"Spotify"` (not `"winsdk"`)
  - **WSL users**: Set to `"None"` - Spotify auth requires browser which doesn't work well in WSL
  - If you want Spotify in WSL, you'll need to manually copy/paste URLs for authentication
- **WSL**: Works best with WSL2 + WSLg (Windows 11)

## 📚 Full Documentation

See [README_LINUX.md](README_LINUX.md) for complete documentation.

---

## 📋 Cheat Sheet

```bash
# First time setup
sudo apt-get install -y python3-dev python3-venv python3-tk portaudio19-dev pulseaudio pavucontrol
python3 -m venv venv
venv/bin/pip install -r requirements-linux.txt

# Run the app
venv/bin/python3 main_linux.py
# OR
./run.sh

# If packages missing
venv/bin/pip install -r requirements-linux.txt

# If venv broken
sudo apt-get install -y python3-venv
rm -rf venv && python3 -m venv venv
venv/bin/pip install -r requirements-linux.txt
```
