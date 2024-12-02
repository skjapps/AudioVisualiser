# AudioVisualiser
A Python (PyGame) based Graphical Audio spectrum visualiser for Windows with Spotify support. Inspired by the [Wallpaper Engine](https://www.wallpaperengine.io/en) wallpaper [Monstercat Visualiser](https://steamcommunity.com/sharedfiles/filedetails/?id=1278092907), but as a standalone app (so i can have it on my work laptop lol). 

## "Installation"
There is none! Just go to releases, download the latest (+config), load and enjoy!
- Press "O" for live options, F4 to fullscreen.
- Try changing the config, most of the settings work
- If you don't use spotify, put `media_mode = None` instead to just see the visualiser
- Put GIF backgrounds in a folder named `backgrounds` next to the app to use cool animated backgrounds

## Featured Python Libraries
(Latest: Python 3.10)
- Spotipy: Spotify api connections
- PyAudioWPatch: Using Windows WASAPI audio capture to loopback and record audio device
- Pygame: All the graphics for the app
- Numpy: FFT, Audio processing and colour recognition, etc.

(All packages required are listed in requirements.)

## Build: 
Using PyInstaller, probably something like:
`PyInstaller --onefile --noconsole --icon="assets/ico/ico.png" --name=AudioVisualiser .\AudioVisualiserSpotipyWindows.py`
Feel free to use whatever settings, it should always work. Check notes for .env setup.
