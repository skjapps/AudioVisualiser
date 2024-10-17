import numpy as np
import pygame
import io
import os
import ctypes
import random
import configparser
import cProfile
import pstats

import GifSprite
from PyAudioWrapper import PyAudioWrapper
from MediaInfoWrapper import MediaInfoWrapper
from FFTProcessor import FFTProcessor
from ImageFlipper import ImageFlipper

from PIL import Image

# Using Pyaudio based version package
# https://github.com/s0d3s/PyAudioWPatch/blob/master/examples/pawp_record_wasapi_loopback.py

#####################################
#               Debug               #
#####################################
timingDebug = False
performanceDebug = True

profiler = cProfile.Profile()
if performanceDebug:
    profiler.enable()


#####################################
#             Constants             #
#####################################
OriginalAppResolution = (960,540)


#####################################
#           Customisation           #
#####################################
# Initialize the parser
config = configparser.ConfigParser()

# Read the configuration file
config.read('config.cfg')

# Access the settings
CHUNK = config.getint('Customisation', 'CHUNK')
fft_update_rate = config.getfloat('Customisation', 'fft_update_rate')
cache_limit = config.getint('Customisation', 'cache_limit')
media_mode = config.get('Customisation', 'media_mode')
media_update_rate = config.getint('Customisation', 'media_update_rate')

# Graphics Customisation
style = config.get('Customisation', 'Style')
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
artist_name_position = tuple(map(float, config.get('Customisation', 'ArtistNamePosition').split(',')))
artist_name_font_size = config.getint('Customisation', 'ArtistNameFontSize')
song_name_position = tuple(map(float, config.get('Customisation', 'SongNamePosition').split(',')))
song_name_font_size = config.getint('Customisation', 'SongNameFontSize')
song_name_short = config.getboolean('Customisation', 'ShortSongName')
album_art_position = tuple(map(float, config.get('Customisation', 'AlbumArtPosition').split(',')))
album_art_size = config.getfloat('Customisation', 'AlbumArtSize')
album_art_colouring = config.getboolean('Customisation', 'AlbumArtColouring')
album_art_colour_vibrancy = config.getfloat('Customisation', 'AlbumArtColourVibrancy')                     

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
pygame.init()
screen = pygame.display.set_mode(OriginalAppResolution, flags=(pygame.RESIZABLE | (pygame.NOFRAME * no_frame) | (pygame.FULLSCREEN * fullscreen)), vsync=1)
w, h = pygame.display.get_surface().get_size()
pygame.display.set_caption("Audio Visualiser")
pygame.display.set_icon(pygame.image.load('assets/ico/ico.png'))
clock = pygame.time.Clock()
# Fonts setup
font_song_name = pygame.font.SysFont('Arial', song_name_font_size)
font_artist_name = pygame.font.SysFont('Arial', artist_name_font_size)

# To initialise variables
album_art = None
artist_image = None

# Initialize PyAudio Object
p = PyAudioWrapper(CHUNK)

# Initialise FFTProcessor
# fft_processor = FFTProcessor(chunk_size=CHUNK, update_rate=1/fft_update_rate, stream=p.stream, sample_rate=p.default_speakers["defaultSampleRate"])

# Spotify #
sp = MediaInfoWrapper(media_mode, pygame.time.get_ticks(), cache_limit, media_update_rate)
if sp.results != None:
    album_art = pygame.image.load(io.BytesIO(sp.album_art_data))
    album_art = pygame.transform.scale_by(album_art, ResizedAlbumArtSize)
    artist_image = pygame.image.load(io.BytesIO(sp.artist_image_data))
    artist_image = pygame.transform.scale_by(artist_image, ResizedAlbumArtSize)
    sp.updated = False

# Create an ImageFlipper instance
# flipper = ImageFlipper(album_art, artist_image, flip_interval=5000, flip_duration=1000)


#####################################
#             Main loop             #
#####################################
# Calculation variables:
previous_log_fft_data = None
# Program variables:
running = True
# Pick a random background from folder
try:
    random_background = str('assets/img/' + random.choice(os.listdir('assets/img/')))
    background = GifSprite.GifSprite(random_background, (0,0), fps=background_fps)
    background.resize_frames(OriginalAppResolution[0] / background.size[0],
                             OriginalAppResolution[1] / background.size[1])
except Exception as e:
    # print("Error:", e, "\n\n")
    background = None
drawArrayLength = 0
while running:
    
    start_time = pygame.time.get_ticks()

    # Pygame Events (Quit, Window Resize)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.VIDEORESIZE:
            #  Get canvas size when resized (on instant)
            w, h = pygame.display.get_surface().get_size()
        
            # Changes for resize
            # Info Font
            # Max instead of min for wider resolutions
            # Min instead of max for "phone" resolutions
            ResizedSongNameFontSize = int(song_name_font_size * max(w/OriginalAppResolution[0],
                                                                h/OriginalAppResolution[1]))
            ResizedArtistNameFontSize = int(artist_name_font_size * max(w/OriginalAppResolution[0],
                                                                h/OriginalAppResolution[1]))
            ResizedAlbumArtSize = album_art_size * max(w/OriginalAppResolution[0],
                                                            h/OriginalAppResolution[1]) * 0.3
            font_song_name = pygame.font.SysFont('Arial', ResizedSongNameFontSize)
            font_artist_name = pygame.font.SysFont('Arial', ResizedArtistNameFontSize)
            # Album art
            if sp.results != None:
                album_art = pygame.image.load(io.BytesIO(sp.album_art_data))
                album_art = pygame.transform.scale_by(album_art, ResizedAlbumArtSize)
                artist_image = pygame.image.load(io.BytesIO(sp.artist_image_data))
                artist_image = pygame.transform.scale_by(artist_image, ResizedAlbumArtSize)
                # flipper.change_images(album_art, artist_image)
            # Background
            if background != None:
                background.resize_frames(w / background.size[0],
                                h / background.size[1])

    event_time = pygame.time.get_ticks()

    # AUDIO PROCESSING
    try:
        data = p.read_mono()
        fft_data = np.abs(np.fft.fft(data))[:CHUNK // 2]
        # fft_data = np.abs(fft_processor.get_smoothed_fft_result())
    except Exception as error:
        print("An error occurred:", error)

    audio_time_fft = pygame.time.get_ticks()

    if style == "Bars":
        if 'log_bins' not in globals():
            log_bins = np.logspace(0, np.log10(CHUNK//2), num=num_of_bars, base=10.0, dtype=int)
            log_bins = np.unique(log_bins)

        log_fft_data = np.array([np.mean(fft_data[log_bins[i-1]:log_bins[i]]) for i in range(1, len(log_bins))])

    elif style == "Smooth":
        log_freqs = np.logspace(np.log10(1), np.log10(CHUNK // 2), num=CHUNK // 2)
        linear_freqs = np.linspace(0, CHUNK // 2, CHUNK // 2)
        log_fft_data = np.interp(log_freqs, linear_freqs, fft_data)

    drawArrayLength = len(log_fft_data)

    logarithmic_multiplier = np.log10(np.linspace(1 + 4*bass_pump, 10, len(log_fft_data)))
    log_fft_data *= logarithmic_multiplier

    max_value = np.max(log_fft_data)
    if max_value > 0:
        log_fft_data = log_fft_data / (max_value * 0.8)

    if previous_log_fft_data is not None:
        log_fft_data = smoothing_factor * previous_log_fft_data + (1 - smoothing_factor) * log_fft_data
    previous_log_fft_data = log_fft_data

    audio_time = pygame.time.get_ticks()

    # SPOTIFY PROCESSING
    sp.update(pygame.time.get_ticks())
    if sp.updated & (sp.results != None):
        album_art = pygame.image.load(io.BytesIO(sp.album_art_data))
        album_art = pygame.transform.scale_by(album_art, ResizedAlbumArtSize)
        artist_image = pygame.image.load(io.BytesIO(sp.artist_image_data))
        artist_image = pygame.transform.scale_by(artist_image, ResizedAlbumArtSize)
        # flipper.change_images(album_art, artist_image)
        sp.updated = False

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
        bar_width = w // drawArrayLength
        for i in range(1, drawArrayLength):
            bar_height = log_fft_data[i] * h * 0.5 # Scale to screen height
            log_fft_data[i] = min(log_fft_data[i], 1)
            pygame.draw.rect(screen, (
                                        (Colour[0] * min(log_fft_data[i], 0.5) + album_art_colour_vibrancy * 125), 
                                        (Colour[1] * min(log_fft_data[i], 0.5) + album_art_colour_vibrancy * 125), 
                                        (Colour[2] * min(log_fft_data[i], 0.5) + album_art_colour_vibrancy * 125),
                                    ), 
                            (i * bar_width + (visualiser_position[0] * w), 
                            h - bar_height + (-visualiser_position[1] * h), 
                            bar_width * visualiser_size[0], 
                            bar_height * visualiser_size[1]))
            
    graphics_time_bars = pygame.time.get_ticks()
            
    # Render Spotify Data
    if sp.results != None :
        # Render song name
        song_name = font_song_name.render(sp.song_name, 
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
        # if (album_art != None) or (artist_image != None) :
        if (album_art != None) :
            # Update the flipper
            # flipper.update()

            # Draw the current image
            # flipper.draw(screen, (w * album_art_position[0],
            #                         h - h * album_art_position[1]))
            screen.blit(album_art, (w * album_art_position[0],
                                    h - h * album_art_position[1]))
                    
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