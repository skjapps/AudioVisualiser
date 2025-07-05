# Audio Visualiser

A cross-platform audio visualization application that creates real-time visual effects based on audio input.

## Features

- **Real-time Audio Visualization**: Visualizes audio from your default input device
- **Multiple Visual Effects**: 
  - Frequency spectrum bars
  - Oscilloscope display
  - Particle field effects
  - Background GIF animations
- **Spotify Integration**: Display current song information and album art (when using Spotify mode)
- **Customizable**: Extensive configuration options for colors, positions, and effects
- **Cross-platform**: Works on Windows, macOS, and Linux

## Universal Version Changes

This version has been modified for cross-platform compatibility:

### Removed Windows-specific Features:
- Transparent window overlay (Windows-only)
- Always-on-top window behavior
- Windows Media Control integration
- Audio loopback recording (Windows-specific)

### Cross-platform Features:
- Uses standard PyAudio for audio input
- Works with any audio input device (microphone, line-in, etc.)
- Standard window management
- Spotify integration only (removed Windows Media Control)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd AudioVisualiser
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Configuration

The application uses `config.cfg` for configuration. Key settings include:

- **Audio Settings**: CHUNK size, sleep time, media mode
- **Visual Settings**: Number of bars, colors, positions, effects
- **Spotify Integration**: Update rate, album art settings

## Usage

### Controls:
- **R**: Reinitialize audio
- **Q**: Quit application
- **O**: Open options window
- **F4**: Toggle fullscreen
- **Left/Right**: Change font
- **1-9**: Select different option categories
- **+/-**: Adjust selected options

### Audio Input:
The application uses your system's default audio input device. Make sure your microphone or audio input is properly configured and selected as the default input device.

### Spotify Mode:
To use Spotify integration:
1. Set `media_mode = Spotify` in the config
2. The first time you run the app, it will open a browser for Spotify authorization
3. Authorize the application to access your Spotify account
4. The app will display current song information and album art

## Requirements

- Python 3.7+
- PyAudio
- Pygame
- NumPy
- Spotipy (for Spotify integration)
- Pillow (for image processing)

## Troubleshooting

### Audio Issues:
- Ensure your default audio input device is properly configured
- Check that PyAudio is correctly installed for your platform
- On macOS, you may need to grant microphone permissions

### Spotify Issues:
- Make sure you have an active Spotify account
- Check that the Spotify app is running and playing music
- Verify your internet connection

## Platform Notes

### Windows:
- Standard PyAudio installation should work
- No special configuration needed

### macOS:
- May need to install PyAudio via Homebrew: `brew install portaudio`
- Grant microphone permissions in System Preferences
- Spotify integration works normally

### Linux:
- Install system audio dependencies: `sudo apt-get install portaudio19-dev python3-pyaudio`
- May need to configure audio permissions
- Spotify integration works normally

## Contributing

This is a universal version of the original Windows-specific audio visualizer. Contributions to improve cross-platform compatibility are welcome!
