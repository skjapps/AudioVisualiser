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
- Cython: Compiling Python


## The build command
FIRST replace the keys from env, to hide it in the actual python files
`.\.venv\Scripts\python.exe -m PyInstaller --onefile --noconsole --icon="assets/ico/ico.png" --name=AudioVisualiser --add-data "assets/ico;assets/ico" --add-data "assets/img;assets/img" .\main.py`
hiding my keeeys!!

new nuitka trying out this:
`nuitka --onefile --windows-console-mode=disable --windows-icon-from-ico="assets/ico/ico.png" --output-filename=AudioVisualiser.exe --include-data-dir=assets/ico=assets/ico --include-data-dir=assets/img=assets/img .\main.py`

# If the application is run as a bundle, the PyInstaller bootloader
# extends the sys module by a flag frozen=True and sets the app 
# path into variable _MEIPASS'.


# Cython
1. Compiling .py Files Directly (Minimal Rewriting):

Effort: Very little. You only need to change your setup.py to use cythonize on your .py files.
Performance Gain: Small to moderate. You get some speedup from compiling to native code, but Cython can't do much optimization without type information.
When to Use: If you have a large codebase and want a quick, easy performance boost without significant changes, or if your code is primarily I/O-bound (waiting for disk or network), this might be sufficient.
2. Renaming to .pyx and Adding Selective Type Annotations (Moderate Rewriting, Best Balance):

Effort: Moderate. You rename .py to .pyx and focus on adding type annotations in the performance-critical sections of your code.
Performance Gain: Significant. This is where Cython shines. By adding type information, you allow Cython to generate highly optimized C code.
When to Use: This is the recommended approach for most cases. Identify the bottlenecks in your code (using profiling tools if necessary) and add type annotations there. You don't need to type everything; focus on loops, numerical computations, and function arguments/return values.
3. Complete Rewrite with Cython's Syntax (Major Rewriting):

Effort: Significant. You rewrite large portions of your code using Cython's specific syntax (e.g., cdef, cpdef, cimport).
Performance Gain: Potentially the highest, but often not worth the extra effort.
When to Use: Only necessary for extremely performance-critical applications where every last bit of optimization is needed.
Strategies to Minimize Rewriting:

Start with Profiling: Use Python's profiling tools (e.g., cProfile, line_profiler) to identify the performance bottlenecks in your code. This tells you exactly where to focus your Cython efforts.
Incremental Cythonization: Don't try to convert everything at once. Start with the most performance-critical functions or classes. Gradually convert more code as needed.
Focus on Numerical Code: Cython is most effective for numerical computations, loops, and array operations. If your code is mostly string manipulation or I/O, the benefits might be smaller.
Use NumPy Effectively: NumPy is already highly optimized. If you're using NumPy correctly (vectorized operations instead of loops), you might not need much Cythonization for those parts. However, adding type annotations to NumPy arrays in Cython can still provide further improvements.
--annotate Feature: Use the --annotate flag with cythonize (e.g., cythonize("your_module.pyx", annotate=True)). This generates an HTML file that highlights which parts of your code were successfully translated to C and which parts are still using Python's object model. This helps you identify areas where adding type annotations would be most beneficial.



## Useful Links (the tabs i have open)
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

