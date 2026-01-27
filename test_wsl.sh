#!/bin/bash
# WSL GUI and Audio Diagnostic Script

echo "================================================"
echo "  WSL GUI & Audio Diagnostics"
echo "================================================"
echo ""

# Check if running in WSL
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "✓ Running in WSL"
    IS_WSL=true
else
    echo "✓ Running in native Linux"
    IS_WSL=false
fi

echo ""
echo "--- Display Configuration ---"
if [ -n "$DISPLAY" ]; then
    echo "✓ DISPLAY is set: $DISPLAY"
else
    echo "✗ DISPLAY is NOT set"
    echo "  Fix: You need WSLg or an X server (VcXsrv)"
fi

if [ -n "$WAYLAND_DISPLAY" ]; then
    echo "✓ WAYLAND_DISPLAY is set: $WAYLAND_DISPLAY"
else
    echo "  WAYLAND_DISPLAY not set (this is OK if using X11)"
fi

echo ""
echo "--- Audio Configuration ---"
if pulseaudio --check 2>/dev/null; then
    echo "✓ PulseAudio is running"
else
    echo "✗ PulseAudio is NOT running"
    echo "  Fix: Run 'pulseaudio --start'"
fi

if command -v pactl >/dev/null 2>&1; then
    if pactl info >/dev/null 2>&1; then
        echo "✓ PulseAudio server is accessible"
        echo "  Server: $(pactl info 2>/dev/null | grep 'Server Name' | cut -d: -f2 | xargs)"
    else
        echo "✗ PulseAudio server not accessible"
        echo "  Fix: Run 'pulseaudio --start'"
    fi
fi

echo ""
echo "--- Python Environment ---"
if [ -d "venv" ]; then
    echo "✓ Virtual environment exists"
    if [ -f "venv/bin/python3" ]; then
        echo "✓ Python executable found"
        PYTHON_VER=$(venv/bin/python3 --version 2>&1)
        echo "  Version: $PYTHON_VER"
    else
        echo "✗ venv/bin/python3 not found"
        echo "  Fix: Run './setup_linux.sh' or recreate venv"
    fi
else
    echo "✗ Virtual environment not found"
    echo "  Fix: Run 'python3 -m venv venv'"
fi

echo ""
echo "--- GUI Test ---"
echo "Testing if GUI apps can open..."

if [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    if command -v xeyes >/dev/null 2>&1; then
        echo "Running xeyes test (a window with eyes should appear)..."
        echo "Press Ctrl+C after verifying the window shows"
        timeout 5 xeyes 2>/dev/null &
        XEYES_PID=$!
        sleep 2
        if ps -p $XEYES_PID > /dev/null 2>&1; then
            echo "✓ xeyes is running - GUI should be working!"
            kill $XEYES_PID 2>/dev/null
        else
            echo "✗ xeyes failed to run"
        fi
    else
        echo "xeyes not installed. Install with: sudo apt-get install -y x11-apps"
    fi
else
    echo "✗ Cannot test GUI - no display configured"
fi

echo ""
echo "================================================"
echo "  Recommendations"
echo "================================================"

ISSUES=0

if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
    echo "⚠ CRITICAL: No display configured"
    if [ "$IS_WSL" = true ]; then
        echo "  → Run 'wsl --update' in Windows PowerShell"
        echo "  → Or install VcXsrv - see WSL_GUI_SETUP.md"
    fi
    ISSUES=$((ISSUES+1))
fi

if ! pulseaudio --check 2>/dev/null; then
    echo "⚠ WARNING: PulseAudio not running"
    echo "  → Run: pulseaudio --start"
    echo "  → Or run app with: SDL_AUDIODRIVER=dummy venv/bin/python3 main_linux.py"
    ISSUES=$((ISSUES+1))
fi

if [ ! -d "venv" ]; then
    echo "⚠ WARNING: Virtual environment missing"
    echo "  → Run: python3 -m venv venv"
    echo "  → Then: venv/bin/pip install -r requirements-linux.txt"
    ISSUES=$((ISSUES+1))
fi

if [ $ISSUES -eq 0 ]; then
    echo "✓ All checks passed! The app should work."
    echo ""
    echo "Run the app with:"
    echo "  venv/bin/python3 main_linux.py"
else
    echo ""
    echo "Found $ISSUES issue(s). Fix them and try again."
    echo "For detailed help, see: WSL_GUI_SETUP.md"
fi

echo ""
echo "================================================"
