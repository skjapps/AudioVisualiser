import numpy as np
import pygame
import io
import os
import ctypes
import random
import configparser
import cProfile
import pstats
import re
import sys

import GifSprite
from PyAudioWrapper import PyAudioWrapper
from MediaInfoWrapper import MediaInfoWrapper
from ImageFlipper import ImageFlipper
from OptionsScreen import OptionsWindow
# from FFTProcessor import FFTProcessor

from PIL import Image
from pathlib import Path

#####################################
#              Config               #
#####################################
# Initialize the parser
config = configparser.ConfigParser()
# Read the configuration file
config.read('config.cfg')

#####################################
#               Debug               #
#####################################
performanceDebug = config.getboolean('Customisation', 'performanceDebug')
timingDebug = False

profiler = cProfile.Profile()
if performanceDebug:
    profiler.enable()


#####################################
#             Constants             #
#####################################
OriginalAppResolution = (960,480)


#####################################
#           Customisation           #
#####################################

# Access the settings
CHUNK = config.getint('Customisation', 'CHUNK')
# fft_update_rate = config.getfloat('Customisation', 'fft_update_rate')
cache_limit = config.getint('Customisation', 'cache_limit')
media_mode = config.get('Customisation', 'media_mode')
media_update_rate = config.getint('Customisation', 'media_update_rate')

# Graphics Customisation
num_of_bars = config.getint('Customisation', 'NumOfBars')
smoothing_factor = config.getfloat('Customisation', 'smoothing_factor')
frame_rate = config.getint('Customisation', 'FrameRate')
background_style = config.get('Customisation', 'BackgroundStyle')
background_colour = tuple(map(int, config.get('Customisation', 'BackgroundColour').split(',')))
background_fps = config.getint('Customisation', 'BackgroundFPS')
colour = tuple(map(int, config.get('Customisation', 'Colour').split(',')))
visualiser_position = tuple(map(float, config.get('Customisation', 'VisualiserPosition').split(',')))
visualiser_size = tuple(map(float, config.get('Customisation', 'VisualiserSize').split(',')))
no_frame = config.getboolean('Customisation', 'NOFRAME')
fullscreen = config.getboolean('Customisation', 'FULLSCREEN')
background_scale = config.get('Customisation', 'BackgroundScale')
bass_pump = config.getfloat('Customisation', 'BassPump')

# Song Data Graphics Config
font_swap = config.getboolean('Customisation', 'FontSwap')
artist_name_position = tuple(map(float, config.get('Customisation', 'ArtistNamePosition').split(',')))
artist_name_font_size = config.getint('Customisation', 'ArtistNameFontSize')
song_name_position = tuple(map(float, config.get('Customisation', 'SongNamePosition').split(',')))
song_name_font_size = config.getint('Customisation', 'SongNameFontSize')
song_name_short = config.getboolean('Customisation', 'ShortSongName')
album_art_position = tuple(map(float, config.get('Customisation', 'AlbumArtPosition').split(',')))
album_art_size = config.getfloat('Customisation', 'AlbumArtSize')
album_art_colouring = config.getboolean('Customisation', 'AlbumArtColouring')
album_art_colour_vibrancy = config.getfloat('Customisation', 'AlbumArtColourVibrancy')
album_art_flip_interval = config.getfloat('Customisation', 'AlbumArtFlipInterval')
album_art_flip_duration = config.getfloat('Customisation', 'AlbumArtFlipDuration')              

ResizedArtistNameFontSize = config.getint('Customisation', 'ArtistNameFontSize')
ResizedSongNameFontSize = config.getint('Customisation', 'SongNameFontSize')
ResizedAlbumArtSize = 0.3

#####################################
#               PYGAME              #
#####################################
# Window Sizing in windows...
if os.name == 'nt' :
    ctypes.windll.user32.SetProcessDPIAware()
# Initialize Pygame
# Set these first so it shows correctly
pygame.display.set_caption("Audio Visualiser")
# Get the path to the icon file
if getattr(sys, 'frozen', False):
    base_path = Path(sys._MEIPASS)
else:
    base_path = Path(__file__).resolve().parent
icon_path = base_path / 'assets/ico/ico.png'
pygame.display.set_icon(pygame.image.load(icon_path))
# Init pygame graphics engine
pygame.init()
screen = pygame.display.set_mode(OriginalAppResolution, flags=(pygame.RESIZABLE | (pygame.NOFRAME * no_frame) | (pygame.FULLSCREEN * fullscreen)), vsync=1)
w, h = pygame.display.get_surface().get_size()
clock = pygame.time.Clock()
# Fonts setup
available_fonts = pygame.font.get_fonts()
font_song_name = pygame.font.SysFont('Arial', song_name_font_size, True)
font_artist_name = pygame.font.SysFont('Arial', artist_name_font_size, True)

#####################################
#              Options              #
#####################################
# Create an instance of OptionsWindow and close it
options_window = OptionsWindow()
options_window.close()
# Define a function to open the Tkinter window
def open_options():
    options_window.show()

# To initialise variables
album_art = None
artist_image = None

# Initialize PyAudio Object
p = PyAudioWrapper(CHUNK)

# Initialise FFTProcessor
# fft_processor = FFTProcessor(chunk_size=CHUNK, update_rate=1/fft_update_rate, stream=p.stream, sample_rate=p.default_speakers["defaultSampleRate"])

# Spotify #
if media_mode != None :
    sp = MediaInfoWrapper(media_mode, pygame.time.get_ticks(), cache_limit, media_update_rate)
    if sp.results != None:
        album_art = pygame.image.load(io.BytesIO(sp.album_art_data))
        album_art = pygame.transform.scale_by(album_art, ResizedAlbumArtSize)
        artist_image = pygame.image.load(io.BytesIO(sp.artist_image_data))
        artist_image = pygame.transform.scale_by(artist_image, ResizedAlbumArtSize)
        sp.updated = False

# Create an ImageFlipper instance
flipper = ImageFlipper(album_art, artist_image, flip_interval=(1000 * album_art_flip_interval), flip_duration=(1000 * album_art_flip_duration))


#####################################
#             Main loop             #
#####################################
# Calculation variables:
previous_log_fft_data = []
fft_data = None
# Program variables:
running = True
song_name_text = ""
random_font = 'Arial' # Initialised to default font
# options_shown = False
scalar = 0 # colour scaling
# Pick a random background from folder
try:
    random_background = str('backgrounds/' + random.choice(os.listdir('backgrounds/')))
    background = GifSprite.GifSprite(random_background, (0,0), fps=background_fps)
    background.resize_frames(OriginalAppResolution[0] / background.size[0],
                             OriginalAppResolution[1] / background.size[1])
except Exception as e:
    # print("Error:", e, "\n\n")
    background = None
while running:
    
    start_time = pygame.time.get_ticks()

    # Pygame Events (Quit, Window Resize)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_o:
                open_options()
            if event.key == pygame.K_F4:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((ctypes.windll.user32.GetSystemMetrics(0), 
                                                      ctypes.windll.user32.GetSystemMetrics(1)), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((OriginalAppResolution[0], OriginalAppResolution[1]),
                                                     pygame.RESIZABLE)
                # call a resize event
                pygame.event.post(pygame.event.Event(pygame.VIDEORESIZE))
        if event.type == pygame.VIDEORESIZE:
            #  Get canvas size when resized (on instant)
            w, h = pygame.display.get_surface().get_size()
        
            # Changes for resize
            # Info Font
            # Max instead of min for wider resolutions
            # Min instead of max for "phone" resolutions
            ResizedSongNameFontSize = int(song_name_font_size * min(w/OriginalAppResolution[0],
                                                                h/OriginalAppResolution[1]))
            ResizedArtistNameFontSize = int(artist_name_font_size * min(w/OriginalAppResolution[0],
                                                                h/OriginalAppResolution[1]))
            ResizedAlbumArtSize = album_art_size * max(w/OriginalAppResolution[0],
                                                            h/OriginalAppResolution[1]) * 0.3
            font_song_name = pygame.font.SysFont(random_font, ResizedSongNameFontSize)
            font_artist_name = pygame.font.SysFont(random_font, ResizedArtistNameFontSize)
            # Album art
            if sp.results != None:
                album_art = pygame.image.load(io.BytesIO(sp.album_art_data))
                album_art = pygame.transform.scale_by(album_art, ResizedAlbumArtSize)
                artist_image = pygame.image.load(io.BytesIO(sp.artist_image_data))
                artist_image = pygame.transform.scale_by(artist_image, ResizedAlbumArtSize)
                flipper.change_images(album_art, artist_image)
            # Background
            if background != None:
                background.resize_frames(w / background.size[0],
                                h / background.size[1])

    event_time = pygame.time.get_ticks()

    # AUDIO PROCESSING
    try:
        fft_data = np.abs(np.fft.fft(p.mono_data))[:CHUNK // 2]
        # fft_data = np.abs(fft_processor.get_smoothed_fft_result())
    except Exception as error:
        print("An error occurred:", error)

    audio_time_fft = pygame.time.get_ticks()

    # The new maths
    # Smooth interpretation
    log_freqs = np.logspace(np.log10(1), np.log10(CHUNK // 2), num=CHUNK // 2)
    linear_freqs = np.linspace(0, CHUNK // 2, CHUNK // 2)
    smooth_log_fft_data = np.interp(log_freqs, linear_freqs, fft_data)

    # Create evenly spaced bins for averaging
    bins = np.linspace(0, len(smooth_log_fft_data), num_of_bars + 1, dtype=int)

    # Averaging the smooth log fft data into bars
    log_fft_data = np.array([np.mean(smooth_log_fft_data[bins[i]:bins[i+1]]) for i in range(num_of_bars)])

    # Bass reduction 
    # log10 of a linear 1 to 10, for the right effect.
    logarithmic_multiplier = np.power(np.log10(np.linspace(1 + 1*bass_pump, 10, len(log_fft_data))), 2*(1-bass_pump))
    log_fft_data *= logarithmic_multiplier

    # Normalisation of values
    max_value = np.max(log_fft_data)
    if max_value > 0:
        log_fft_data = log_fft_data / (max_value * 0.8)

    if (previous_log_fft_data is not None) & (len(log_fft_data) == len(previous_log_fft_data)):
        log_fft_data = smoothing_factor * previous_log_fft_data + (1 - smoothing_factor) * log_fft_data
    previous_log_fft_data = log_fft_data

    audio_time = pygame.time.get_ticks()

    # SPOTIFY PROCESSING
    sp.update(pygame.time.get_ticks())
    if sp.updated & (sp.results != None):
        try:
            album_art = pygame.image.load(io.BytesIO(sp.album_art_data))
            album_art = pygame.transform.scale_by(album_art, ResizedAlbumArtSize)
            artist_image = pygame.image.load(io.BytesIO(sp.artist_image_data))
            artist_image = pygame.transform.scale_by(artist_image, ResizedAlbumArtSize)
            flipper.change_images(album_art, artist_image)
            sp.updated = False
        except Exception as error:
            print(error, "\n\n")

    spotify_time = pygame.time.get_ticks()

    # GRAPHICS PROCESSING

    # Background GIF
    if background != None:
        screen.blit(background.image, background.pos)
        background.update()
    else:
        screen.fill(background_colour)

    graphics_time_background = pygame.time.get_ticks()

    # Album Art colouring
    # Colour avg
    scalar = 255 - max(sp.avg_colour_album_art)
    Colour = (
                sp.avg_colour_album_art[0] + scalar * album_art_colour_vibrancy,
                sp.avg_colour_album_art[1] + scalar * album_art_colour_vibrancy, 
                sp.avg_colour_album_art[2] + scalar * album_art_colour_vibrancy
             )

    # Draw bars
    if sp.isPlaying or (max_value > 30) :
        bar_width = w // len(log_fft_data)
        for i in range(1, len(log_fft_data)):
            bar_height = log_fft_data[i] * h * 0.5 # Scale to screen height
            log_fft_data[i] = min(log_fft_data[i], 1)
            pygame.draw.rect(screen, (
                                        (Colour[0] * min(log_fft_data[i], 0.8) + album_art_colour_vibrancy * 50), 
                                        (Colour[1] * min(log_fft_data[i], 0.8) + album_art_colour_vibrancy * 50), 
                                        (Colour[2] * min(log_fft_data[i], 0.8) + album_art_colour_vibrancy * 50)
                                    ), 
                            (i * bar_width + (visualiser_position[0] * w), 
                            h - bar_height + (-visualiser_position[1] * h), 
                            bar_width * visualiser_size[0], 
                            bar_height * visualiser_size[1]))
            
    graphics_time_bars = pygame.time.get_ticks()
            
    # Render Spotify Data
    if sp.results != None :
        # Change font for fun when data changes
        if sp.changed & font_swap:
            random_font = random.choice(available_fonts)
            font_song_name = pygame.font.SysFont(random_font, ResizedSongNameFontSize, True)
            font_artist_name = pygame.font.SysFont(random_font, ResizedArtistNameFontSize, True)
            sp.changed = False
        # Render song name
        if song_name_short:
            song_name_text = re.split(r'[\(\-]', sp.song_name)[0].strip()
        else:
            song_name_text = sp.song_name
        song_name = font_song_name.render(song_name_text, 
                                          True, Colour)
        # Display song name
        screen.blit(song_name, (w * song_name_position[0], 
                                h - h * song_name_position[1]))

        # Render artist name
        artist_name = font_artist_name.render(sp.artist_name, 
                                              True, Colour)
        # Display artist name
        screen.blit(artist_name, (w * artist_name_position[0], 
                                  h - h * artist_name_position[1] + ResizedSongNameFontSize))

        # Display album art
        if (album_art != None) or (artist_image != None) :
            try:
                # Incase size changed
                ResizedAlbumArtSize = album_art_size * max(w/OriginalAppResolution[0],
                                                            h/OriginalAppResolution[1]) * 0.3
                
                # Update the flipper
                flipper.update()

                # Draw the current image
                flipper.draw(screen, (w * album_art_position[0],
                                        h - h * album_art_position[1]))
                # screen.blit(album_art, (w * album_art_position[0],
                #                         h - h * album_art_position[1]))
            except Exception as error:
                print(error)
                    
    graphics_time = pygame.time.get_ticks()
    
    clock_time = pygame.time.get_ticks() - start_time
    if timingDebug & (clock_time > 1000/frame_rate):
        print("WARN: Underperforming! update took: ", clock_time, "ms \n",
                "Timings: \n events: ", event_time - start_time, 
                "ms \n audio fft: ", audio_time_fft - event_time,
                "ms \n audio processing: ", audio_time - audio_time_fft, 
                "ms \n spotify: ", spotify_time - audio_time, 
                "ms \n graphics background: ", graphics_time_background - spotify_time,
                "ms \n graphics bars: ", graphics_time_bars - graphics_time_background,
                "ms \n graphics spotify: ", graphics_time - graphics_time_bars, 
                "ms \n")

    # Update display
    pygame.display.flip()

    # Get options changes
    frame_rate = options_window.frame_rate.get()
    num_of_bars = options_window.num_of_bars.get()
    media_update_rate = options_window.media_update_rate.get()
    bass_pump = options_window.bass_pump.get()
    smoothing_factor = options_window.smoothing_factor.get()
    album_art_size = options_window.album_art_size.get()
    album_art_colour_vibrancy = options_window.album_art_colour_vibrancy.get()
    # flipper.flip_interval = round(options_window.album_art_flip_interval.get(),1)
    # flipper.flip_duration = round(options_window.album_art_flip_duration.get(),1)

    # Periodically call the Tkinter event loop
    options_window.window.update_idletasks()
    options_window.window.update()

    # Cap the frame rate
    clock.tick(frame_rate)  # Lock the program to FPS


#####################################
#                Exit               #
#####################################
# Clean up
# Stop the FFTProcessor thread
# fft_processor.stop()

# Audio
p.stream.stop_stream()
p.stream.close()
# Graphics
pygame.quit()

# Get performance Stats
if performanceDebug:
    profiler.disable()
    with open('profiling_stats.txt', 'w') as f:
        stats = pstats.Stats(profiler, stream=f)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.print_stats()