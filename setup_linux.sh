#!/bin/bash

# Audio Visualiser - Linux/WSL Setup Script
# This script sets up the audio visualiser for Linux systems (including WSL)

set -e  # Exit on error

echo "=================================================="
echo "   Audio Visualiser - Linux/WSL Setup"
echo "=================================================="
echo ""

# Detect if running in WSL
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "Detected WSL environment"
    IS_WSL=true
else
    echo "Detected native Linux environment"
    IS_WSL=false
fi

echo ""
echo "Step 1: Checking system dependencies..."
echo "--------------------------------------------------"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Python
if ! command_exists python3; then
    echo "ERROR: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION found"

# Check for pip
if ! command_exists pip3; then
    echo "Installing pip..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi
echo "✓ pip found"

echo ""
echo "Step 2: Installing system packages..."
echo "--------------------------------------------------"

# Detect package manager
if command_exists apt-get; then
    PKG_MGR="apt-get"
    echo "Using apt-get package manager"
    
    # Update package list
    echo "Updating package list..."
    sudo apt-get update
    
    # Install required system packages
    echo "Installing required system packages..."
    sudo apt-get install -y \
        python3-dev \
        python3-venv \
        python3-tk \
        portaudio19-dev \
        libportaudio2 \
        pulseaudio \
        pulseaudio-utils \
        pavucontrol \
        libsdl2-dev \
        libsdl2-image-dev \
        libsdl2-mixer-dev \
        libsdl2-ttf-dev \
        libfreetype6-dev \
        libjpeg-dev \
        libpng-dev \
        xprintidle \
        build-essential
    
    echo "✓ System packages installed"
    
elif command_exists dnf; then
    PKG_MGR="dnf"
    echo "Using dnf package manager"
    
    sudo dnf install -y \
        python3-devel \
        portaudio-devel \
        pulseaudio \
        pulseaudio-utils \
        pavucontrol \
        SDL2-devel \
        SDL2_image-devel \
        SDL2_mixer-devel \
        SDL2_ttf-devel \
        freetype-devel \
        libjpeg-devel \
        libpng-devel \
        xprintidle \
        gcc \
        make
    
    echo "✓ System packages installed"
    
elif command_exists pacman; then
    PKG_MGR="pacman"
    echo "Using pacman package manager"
    
    sudo pacman -Syu --noconfirm \
        python \
        python-pip \
        portaudio \
        pulseaudio \
        pulseaudio-alsa \
        pavucontrol \
        sdl2 \
        sdl2_image \
        sdl2_mixer \
        sdl2_ttf \
        freetype2 \
        libjpeg-turbo \
        libpng \
        xprintidle \
        base-devel
    
    echo "✓ System packages installed"
else
    echo "WARNING: Could not detect package manager. You may need to install dependencies manually."
    echo "Required packages: portaudio, pulseaudio, SDL2, python3-dev, xprintidle"
fi

echo ""
echo "Step 3: Setting up PulseAudio/PipeWire..."
echo "--------------------------------------------------"

# Check if PipeWire is running (it provides PulseAudio compatibility)
if pgrep -x "pipewire" > /dev/null || pgrep -x "pulseaudio" > /dev/null; then
    echo "✓ Audio server (PulseAudio/PipeWire) is running"
else
    echo "Starting PulseAudio..."
    pulseaudio --start --log-target=syslog || echo "PulseAudio may already be running or needs manual configuration"
fi

# Load the loopback module for audio capture
echo "Setting up audio loopback for system audio capture..."
pactl load-module module-loopback 2>/dev/null || echo "Note: Loopback module may already be loaded or unavailable"

# Enable echo cancellation (optional, improves audio quality)
echo "Enabling echo cancellation source (optional)..."
pactl load-module module-echo-cancel 2>/dev/null || echo "Note: Echo cancel module may already be loaded or unavailable"

echo ""
echo "Step 4: Creating Python virtual environment..."
echo "--------------------------------------------------"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Step 5: Installing Python dependencies..."
echo "--------------------------------------------------"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python packages
echo "Installing Python packages from requirements-linux.txt..."
pip install -r requirements-linux.txt

echo "✓ Python dependencies installed"

echo ""
echo "Step 6: WSL-specific configuration..."
echo "--------------------------------------------------"

if [ "$IS_WSL" = true ]; then
    echo "Configuring for WSL environment..."
    
    # Check for WSLg (WSL2 with GUI support)
    if [ -n "$WAYLAND_DISPLAY" ] || [ -n "$DISPLAY" ]; then
        echo "✓ WSLg detected - GUI support available"
        echo "  Display: ${DISPLAY:-$WAYLAND_DISPLAY}"
    else
        echo "WARNING: No display detected. You may need to configure X11 forwarding."
        echo "  For WSL2, ensure you're using WSLg or have an X server (VcXsrv, Xming) running on Windows."
        echo "  You may need to set: export DISPLAY=:0"
    fi
    
    # PulseAudio for WSL
    echo ""
    echo "WSL Audio Setup Notes:"
    echo "  1. Ensure PulseAudio is running in WSL"
    echo "  2. For WSL1: You may need a Windows PulseAudio server"
    echo "  3. For WSL2 with WSLg: Audio should work out of the box"
    echo "  4. You can test audio with: speaker-test -t wav -c 2"
    
else
    echo "Native Linux detected - no additional WSL configuration needed"
fi

echo ""
echo "Step 7: Testing audio devices..."
echo "--------------------------------------------------"

echo "Available PulseAudio sinks (output devices):"
pactl list short sinks

echo ""
echo "Available PulseAudio sources (input devices, including monitors):"
pactl list short sources

echo ""
echo "=================================================="
echo "   Setup Complete!"
echo "=================================================="
echo ""
echo "To run the Audio Visualiser:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the application:"
echo "     python3 main_linux.py"
echo ""
echo "  3. If you encounter audio issues, try:"
echo "     - pavucontrol  (PulseAudio Volume Control - GUI mixer)"
echo "     - pactl list sources  (List available audio sources)"
echo "     - pulseaudio -k && pulseaudio --start  (Restart PulseAudio)"
echo ""
echo "Keyboard shortcuts in the visualiser:"
echo "  Q - Quit"
echo "  R - Reload audio device"
echo "  O - Open options"
echo "  F4 - Toggle fullscreen"
echo "  G - Toggle oscilloscope normalization"
echo "  Left/Right arrows - Change font"
echo ""
echo "For WSL users:"
echo "  - Ensure WSLg is installed (Windows 11 or Windows 10 with updates)"
echo "  - Or use an X server like VcXsrv on Windows"
echo "  - Audio capture works best with PipeWire or PulseAudio loopback"
echo ""
echo "=================================================="
