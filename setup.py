from setuptools import setup, Extension
from Cython.Build import cythonize

setup(
    ext_modules=cythonize([
        Extension("API.MediaInfoWrapper", ["API/MediaInfoWrapper.py"]),

        Extension("Audio.AudioProcess", ["Audio/AudioProcess.py"]),
        Extension("Audio.PyAudioWrapper", ["Audio/PyAudioWrapper.py"]),

        Extension("Graphics.GifSprite", ["Graphics/GifSprite.py"]),
        Extension("Graphics.HUD", ["Graphics/HUD.py"]),
        Extension("Graphics.ImageFlipper", ["Graphics/ImageFlipper.py"]),
        Extension("Graphics.OptionsScreen", ["Graphics/OptionsScreen.py"]),
        Extension("Graphics.Oscilloscope", ["Graphics/Oscilloscope.py"]),
        Extension("Graphics.VisualiserGraphics", ["Graphics/VisualiserGraphics.py"]),

        Extension("main", ["main.py"]),
    ]),
)