import math
import pygame
import io
import os
import ctypes
import random
import configparser
import cProfile
import pstats
import re
import win32api
import win32con
import win32gui
import webbrowser
import threading
import sdl2
import sdl2.ext
import OpenGL.GL as gl
import numpy as np

from Default import Functions
from Graphics.GifSprite import GifSprite
from Graphics.VisualiserGraphics import Visualiser
# from BackgroundManager import BackgroundManager
from Graphics.ImageFlipper import ImageFlipper
from Graphics.OptionsScreen import OptionsScreen
from Graphics.Oscilloscope import Oscilloscope
from Graphics.DotField import DotField
from Graphics.HUD import HUD
from API.MediaInfoWrapper import MediaInfoWrapper
from Audio.PyAudioWrapper import PyAudioWrapper
from Audio.AudioProcess import AudioProcess

from pathlib import Path

#####################################
#            Functions              #
#####################################
def transparent_on_top(background_colour):
    hwnd = pygame.display.get_wm_info()["window"]
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
    # Set window transparency color
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(
        *background_colour), 0, win32con.LWA_COLORKEY)
    # NOMOVE|NOSIZE...
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 1 | 2)

def load_background(background_path, background_fps, app_resolution, background_scale, backgrounds):
    try:
        background = GifSprite(
            background_path, (0, 0), fps=background_fps, background_scale=background_scale)
        background.resize_frames(
            app_resolution[0] / background.size[0], app_resolution[1] / background.size[1])
        backgrounds.append(background)
    except Exception as e:
        print(f"Error loading {background_path}: {e}")

def load_backgrounds(background_folder, background_fps, app_resolution, background_scale):
    backgrounds = []
    threads = []

    for filename in os.listdir(background_folder):
        if filename.endswith('.gif'):
            background_path = os.path.join(background_folder, filename)
            thread = threading.Thread(target=load_background, args=(background_path, background_fps, app_resolution, background_scale, backgrounds))
            threads.append(thread)
            thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    return backgrounds

def getIdleTime():
    return (win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000.0

class AudioVisualiser():

    """Create and run the audiovisualiser
    """
    def __init__(self):
        self.re_run = True
        # while self.re_run:
        self.main()

    def main(self):
        #####################################
        #              Config               #
        #####################################
        # Initialize the parser
        config = configparser.ConfigParser()
        # Read the configuration file
        config.read('.\\config.cfg')

        #####################################
        #               Debug               #
        #####################################
        performanceDebug = config.getboolean('Customisation', 'performanceDebug')

        profiler = cProfile.Profile()
        if performanceDebug:
            profiler.enable()
        #####################################
        #             Constants             #
        #####################################
        OriginalAppResolution = (960, 480)

        #####################################
        #           Customisation           #
        #####################################

        # Access the settings
        CHUNK = config.getint('Customisation', 'CHUNK')
        sleep_time = config.getfloat('Customisation', 'sleep_time')
        cache_limit = config.getint('Customisation', 'cache_limit')
        media_mode = config.get('Customisation', 'media_mode')
        media_update_rate = config.getint('Customisation', 'MediaUpdateRate')

        # Graphics Customisation
        num_of_bars = config.getint('Customisation', 'NumOfBars')
        smoothing_factor = config.getfloat('Customisation', 'SmoothingFactor')
        low_pass_bass_reading = config.getfloat('Customisation', 'BassLowPass')
        frame_rate = config.getint('Customisation', 'FrameRate')
        background_style = config.get('Customisation', 'BackgroundStyle')
        background_colour = tuple(
            map(int, config.get('Customisation', 'BackgroundColour').split(',')))
        background_fps = config.getint('Customisation', 'BackgroundFPS')
        Colour = tuple(map(int, config.get('Customisation', 'Colour').split(',')))
        visualiser_position = tuple(map(float, config.get(
            'Customisation', 'VisualiserPosition').split(',')))
        visualiser_size = tuple(map(float, config.get(
            'Customisation', 'VisualiserSize').split(',')))
        visualiser_image = config.get('Customisation', 'VisualiserImage')
        bar_thickness = config.getfloat('Customisation', 'BarThickness')
        bar_height = config.getfloat('Customisation', 'BarHeight')

        oscilloscope_position = tuple(map(float, config.get(
            'Customisation', 'OscilloscopePosition').split(',')))
        oscilloscope_size = tuple(map(float, config.get(
            'Customisation', 'OscilloscopeSize').split(',')))
        oscilloscope_time_frame = config.getfloat(
            'Customisation', 'OscilloscopeTimeFrame')
        oscilloscope_gain = config.getfloat('Customisation', 'OscilloscopeGain')
        oscilloscope_normalisation = config.getboolean('Customisation', 'OscilloscopeNormalisation')
        oscilloscope_acdc = config.get('Customisation', 'OscilloscopeACDC')

        no_frame = config.getboolean('Customisation', 'NOFRAME')
        fullscreen = config.getboolean('Customisation', 'FULLSCREEN')
        background_scale = config.get('Customisation', 'BackgroundScale')
        background_fade_duration = config.getfloat(
            'Customisation', 'BackgroundFadeDuration')
        bass_pump = config.getfloat('Customisation', 'BassPump')

        # Song Data Graphics Config
        random_font_swap = config.getboolean('Customisation', 'RandomFontSwap')
        artist_name_position = tuple(map(float, config.get(
            'Customisation', 'ArtistNamePosition').split(',')))
        artist_name_font_size = config.getint('Customisation', 'ArtistNameFontSize')
        song_name_position = tuple(map(float, config.get(
            'Customisation', 'SongNamePosition').split(',')))
        song_name_font_size = config.getint('Customisation', 'SongNameFontSize')
        song_name_short = config.getboolean('Customisation', 'ShortSongName')
        album_art_position = tuple(map(float, config.get(
            'Customisation', 'AlbumArtPosition').split(',')))
        album_art_size = config.getfloat('Customisation', 'AlbumArtSize')
        album_art_colouring = config.getboolean('Customisation', 'AlbumArtColouring')
        album_art_colour_vibrancy = config.getfloat(
            'Customisation', 'AlbumArtColourVibrancy')
        album_art_flip_interval = config.getfloat(
            'Customisation', 'AlbumArtFlipInterval')
        album_art_flip_duration = config.getfloat(
            'Customisation', 'AlbumArtFlipDuration')

        ResizedArtistNameFontSize = config.getint(
            'Customisation', 'ArtistNameFontSize')
        ResizedSongNameFontSize = config.getint('Customisation', 'SongNameFontSize')
        ResizedAlbumArtSize = 0.3

        #####################################
        #               AUDIO               #
        #####################################
        # Initialize PyAudio Object
        p = PyAudioWrapper(CHUNK)

        #####################################
        #             GRAPHICS              #
        #####################################
        #####################################
        #              Pygame               #
        #####################################
        # Window Sizing in windows...
        if os.name == 'nt':
            ctypes.windll.user32.SetProcessDPIAware()
        # Initialize Pygame
        # Set these first so it shows correctly
        pygame.display.set_caption("Audio Visualiser")
        icon_path = Functions.resource_path('assets/ico/ico.png')
        pygame.display.set_icon(pygame.image.load(icon_path))
        # Init pygame graphics engine
        pygame.init()
        
        # screen = pygame.display.set_mode(OriginalAppResolution, flags=(pygame.RESIZABLE | (pygame.NOFRAME * no_frame) | (pygame.FULLSCREEN * fullscreen)))

        # Initialize SDL2 and create an OpenGL context
        sdl2.ext.init()
        window = sdl2.SDL_CreateWindow(b"Audio Visualizer", sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, 960, 480, sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_RESIZABLE)
        sdl2.SDL_GL_CreateContext(window)

        #####################################
        #             Main loop             #
        #####################################
        # Objects:
        audio_processor = AudioProcess()
        visualiser = Visualiser(visualiser_size, visualiser_width=w, visualiser_height=h)
        # Create a DotField instance
        dot_field = DotField(dot_field_width=w, dot_field_height=h, dot_count=100, dot_size_range=(2, 5), speed_factor=5, direction="left", dot_color=(0,0,0), opacity=64)
        # Program variables:
        running = True
        song_name_text = ""
        background_index = 0
        font = 'Arial'  # Initialised to default font
        font_index = 0  # Counting font change index
        swap_font = False  # Flag to swap font when pressed left/right
        change_background = False  # Flag to change background when pressed up/down
        scalar = 0  # colour scaling
        # rainbow visualiser mask
        rainbow_animate = GifSprite('assets/img/rainbow.gif', (0, 0), fps=30, background_scale="Stretch")
        rainbow_animate.resize_frames(w / rainbow_animate.size[0], h / rainbow_animate.size[1])
        options_counter = 1
        visualiser_options = ["None", "Rainbow", "Artist", "Album"]
        visualiser_option_counter = visualiser_options.index(visualiser_image)
        oscilloscope_options = ["ac", "dc"]
        oscilloscope_option_counter = oscilloscope_options.index(oscilloscope_acdc)
        dot_field_options = ["left", "right"]
        dot_field_option_counter = dot_field_options.index(dot_field.direction)
        # Main Loop
        while running:

            # Pygame Events (Quit, Window Resize)
            for event in pygame.event.get():
                # Quit
                if event.type == pygame.QUIT:
                    running = False

            # AUDIO PROCESSING
            log_fft_data, max_value, bass_reading = audio_processor.perform_FFT(CHUNK, num_of_bars, bass_pump, smoothing_factor, low_pass_bass_reading, p)

