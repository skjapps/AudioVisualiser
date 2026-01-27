# Linux Setup Fixes Summary

## Issues Fixed

### 1. Missing `python3-venv` Package
**Problem:** Virtual environment creation failed with "ensurepip is not available"
**Solution:** Added `python3-venv` to system dependencies
```bash
sudo apt-get install -y python3-venv
```

### 2. Missing `python3-tk` Package  
**Problem:** `ModuleNotFoundError: No module named 'tkinter'`
**Solution:** Added `python3-tk` to system dependencies
```bash
sudo apt-get install -y python3-tk
```

### 3. Missing `python-dotenv` Package
**Problem:** `ModuleNotFoundError: No module named 'dotenv'`
**Solution:** Added `python-dotenv` to `requirements-linux.txt`

### 4. Windows-only `winsdk` Import
**Problem:** `ModuleNotFoundError: No module named 'winsdk'` on Linux
**Solution:** Made imports platform-specific in `API/MediaInfoWrapper.py`:
```python
if sys.platform == 'win32':
    import winsdk.windows.media.control as wmc
    import winsdk.windows.storage.streams as streams
```

### 5. Externally-Managed Environment Error
**Problem:** Ubuntu 24.04+ prevents direct `pip install` to protect system Python
**Solution:** Documented the need to use virtual environments with proper explanation in QUICKSTART_LINUX.md

## Updated Files

1. **setup_linux.sh** - Added `python3-venv` and `python3-tk` to apt packages
2. **QUICKSTART_LINUX.md** - Simplified with clear 3-step setup and troubleshooting
3. **requirements-linux.txt** - Added `python-dotenv`
4. **API/MediaInfoWrapper.py** - Made winsdk imports conditional (Windows-only)
5. **README_LINUX.md** - Added quick start section at top
6. **run.sh** - Created simple launcher script

## Working Setup Commands

```bash
# One-time system setup
sudo apt-get update
sudo apt-get install -y python3-dev python3-venv python3-tk portaudio19-dev pulseaudio pavucontrol

# Create virtual environment and install packages
cd ~/audiovisualiser
python3 -m venv venv
venv/bin/pip install -r requirements-linux.txt

# Run the app
venv/bin/python3 main_linux.py
# OR
./run.sh
```

## Why Virtual Environments Are Required on Modern Linux

Starting with PEP 668 (Python Enhancement Proposal), modern Linux distributions like Ubuntu 24.04+ use "externally-managed environments" to prevent users from breaking system Python packages. You MUST use one of:

1. **Virtual environment** (recommended): `python3 -m venv venv`
2. **System packages**: `sudo apt install python3-<package>`
3. **Breaking the system** (NOT recommended): `pip install --break-system-packages`

The virtual environment approach keeps everything clean, isolated, and won't break your system.
