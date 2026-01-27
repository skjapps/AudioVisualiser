#!/usr/bin/env python3
"""
Audio Visualiser - Linux Setup Test
Tests if all dependencies are correctly installed
"""

import sys
import subprocess

def test_import(module_name, package_name=None):
    """Test if a Python module can be imported"""
    package_name = package_name or module_name
    try:
        __import__(module_name)
        print(f"✓ {package_name} installed")
        return True
    except ImportError as e:
        print(f"✗ {package_name} NOT installed: {e}")
        return False

def test_command(command, description):
    """Test if a system command is available"""
    try:
        result = subprocess.run([command, '--version'], 
                              capture_output=True, 
                              timeout=2)
        print(f"✓ {description} available")
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        try:
            # Some commands don't support --version
            result = subprocess.run([command], 
                                  capture_output=True, 
                                  timeout=2)
            print(f"✓ {description} available")
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print(f"✗ {description} NOT available")
            return False

def test_pulseaudio():
    """Test if PulseAudio/PipeWire is running"""
    try:
        # Check if PulseAudio server is running
        result = subprocess.run(['pulseaudio', '--check'], 
                              capture_output=True, 
                              timeout=2)
        if result.returncode == 0:
            print("✓ PulseAudio is running")
            return True
        
        # Check for PipeWire with PulseAudio compat
        result = subprocess.run(['pgrep', 'pipewire'], 
                              capture_output=True, 
                              timeout=2)
        if result.returncode == 0:
            print("✓ PipeWire is running (provides PulseAudio compatibility)")
            return True
            
        print("✗ No audio server detected (PulseAudio/PipeWire)")
        return False
    except Exception as e:
        print(f"✗ Could not check audio server: {e}")
        return False

def test_audio_sources():
    """Test if audio sources (monitors) are available"""
    try:
        result = subprocess.run(['pactl', 'list', 'sources', 'short'], 
                              capture_output=True, 
                              text=True,
                              timeout=2)
        if result.returncode == 0:
            sources = result.stdout.strip().split('\n')
            monitor_sources = [s for s in sources if 'monitor' in s.lower()]
            
            if monitor_sources:
                print(f"✓ Found {len(monitor_sources)} monitor source(s)")
                for source in monitor_sources[:3]:  # Show first 3
                    print(f"  - {source.split()[1]}")
                return True
            else:
                print("⚠ No monitor sources found (audio capture may not work)")
                print("  Run: pactl load-module module-loopback")
                return False
        else:
            print("✗ Could not list audio sources")
            return False
    except Exception as e:
        print(f"✗ Could not check audio sources: {e}")
        return False

def test_display():
    """Test if display is available (important for WSL)"""
    display = subprocess.os.environ.get('DISPLAY') or subprocess.os.environ.get('WAYLAND_DISPLAY')
    if display:
        print(f"✓ Display configured: {display}")
        return True
    else:
        print("⚠ No display configured (GUI may not work)")
        print("  For WSL: Ensure WSLg is installed or set DISPLAY variable")
        return False

def main():
    print("=" * 60)
    print("Audio Visualiser - Linux Setup Test")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Test Python version
    print("Python Environment:")
    print("-" * 60)
    version = sys.version_info
    if version >= (3, 8):
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (need 3.8+)")
        all_passed = False
    print()
    
    # Test Python packages
    print("Python Packages:")
    print("-" * 60)
    packages = [
        ('numpy', 'NumPy'),
        ('pygame', 'Pygame'),
        ('pyaudio', 'PyAudio'),
        ('requests', 'Requests'),
        ('PIL', 'Pillow'),
        ('spotipy', 'Spotipy'),
    ]
    
    for module, name in packages:
        if not test_import(module, name):
            all_passed = False
    print()
    
    # Test system commands
    print("System Tools:")
    print("-" * 60)
    if not test_command('pulseaudio', 'PulseAudio'):
        all_passed = False
    if not test_command('pactl', 'PulseAudio Control'):
        all_passed = False
    test_command('pavucontrol', 'PulseAudio Volume Control')  # Optional
    test_command('xprintidle', 'Idle time detection')  # Optional
    print()
    
    # Test audio server
    print("Audio Server:")
    print("-" * 60)
    if not test_pulseaudio():
        all_passed = False
    print()
    
    # Test audio sources
    print("Audio Sources:")
    print("-" * 60)
    test_audio_sources()  # Warning only, not critical
    print()
    
    # Test display
    print("Display Server:")
    print("-" * 60)
    test_display()  # Warning only for WSL
    print()
    
    # Test custom modules
    print("Application Modules:")
    print("-" * 60)
    try:
        sys.path.insert(0, '.')
        from Audio import PyAudioWrapperLinux
        print("✓ PyAudioWrapperLinux module found")
    except ImportError as e:
        print(f"✗ PyAudioWrapperLinux module NOT found: {e}")
        all_passed = False
    
    try:
        from Default import AudioVisualiserLinux
        print("✓ AudioVisualiserLinux module found")
    except ImportError as e:
        print(f"✗ AudioVisualiserLinux module NOT found: {e}")
        all_passed = False
    print()
    
    # Summary
    print("=" * 60)
    if all_passed:
        print("✓ ALL CRITICAL TESTS PASSED!")
        print("\nYou can now run the application:")
        print("  python3 main_linux.py")
    else:
        print("✗ SOME TESTS FAILED")
        print("\nPlease install missing dependencies:")
        print("  ./setup_linux.sh")
        print("\nOr manually:")
        print("  pip install -r requirements-linux.txt")
        print("  sudo apt-get install portaudio19-dev pulseaudio")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
