# To Do:
## Minor Fixes:
- ~~Make sure when songs are playing, it is showing the visualiser, house style songs do not work properly, sometimes cutting out when there is silence.~~ Changed to max value = 20, still to improve song playing detection...
- The stretching of window ruins the resolution of the image, mildly intentional, pixelated backgrounds run faster...
- Font selector maybe
- Spotify fetch to true async vs broken threading.
- Background loading speedup on launch with true cache of obj
- Fix the transparent background keying problems
- WORKAROUND PATCH: return default images for failed sp. (see init code in audiovisualiserspotipywindows)
- .spec build not working, i dunno how it works but idc.
## Big changes
- WindowsRT in WIP will allow any media titles and names to be recognised, allow both spotify and windows modes
- MacOS and Linux support somehow (WASAPI is the best loopback)
- Performance needs improvement. Threading spotify data collection and graphics could help.
- ...


## The build command
`.\.venv\Scripts\python.exe -m PyInstaller --onefile --noconsole --icon="assets/ico/ico.png" --name=AudioVisualiser --add-data ".env:." --hidden-import dotenv --add-data "assets/ico/ico.png:assets/ico" --add-data "assets/img/options.png:assets/img"  --add-data "assets/ico/spotify.png:assets/ico" .\main.py`
hiding my keeeys!!

# If the application is run as a bundle, the PyInstaller bootloader
# extends the sys module by a flag frozen=True and sets the app 
# path into variable _MEIPASS'.

~~This maybe the last time i commit (sad) it works well enough, good luck !~~ I just love this project too much i will keep going...

# Useful Links (the tabs i have open)
https://www.desmos.com/calculator

Could this work better...? fft that takes samples logarithmically than linearly
https://pyfftlog.readthedocs.io/en/latest/examples/fftlogtest.html#sphx-glr-examples-fftlogtest-py

os check:
https://stackoverflow.com/questions/1325581/how-do-i-check-if-im-running-on-windows-in-python

spotify:
https://spotipy.readthedocs.io/en/2.24.0/#getting-started
https://developer.spotify.com/documentation/web-api/concepts/rate-limits

pygame:
https://www.pygame.org/docs/ref/rect.html#pygame.Rect.inflate
https://www.pygame.org/docs/ref/transform.html
https://stackoverflow.com/questions/34013119/pygame-text-anchor-right

File Read:
https://stackoverflow.com/questions/5627425/what-is-a-good-way-to-handle-exceptions-when-trying-to-read-a-file-in-python

Windows currently playing:
https://stackoverflow.com/questions/65011660/how-can-i-get-the-title-of-the-currently-playing-media-in-windows-10-with-python

