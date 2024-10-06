import numpy as np
import pygame
import io
import os
import GifSprite
import PyAudioWrapper
import SpotipyWrapper
import ctypes
import random
import configparser

from PIL import Image

# Using Pyaudio based version package
# https://github.com/s0d3s/PyAudioWPatch/blob/master/examples/pawp_record_wasapi_loopback.py

#####################################
#               Debug               #
#####################################
timingDebug = False

#####################################
#             Constants             #
#####################################
CHUNK = 1024
OriginalAppResolution = (960,540)


#####################################
#           Customisation           #
#####################################
# Initialize the parser
config = configparser.ConfigParser()

# Read the configuration file
config.read('config.cfg')

# Access the settings
cache_limit = config.getint('Customisation', 'cache_limit')
spotify_update_rate = config.getint('Customisation', 'spotify_update_rate')

# Graphics Customisation
style = config.get('Customisation', 'Style')
num_of_bars = config.getint('Customisation', 'NumOfBars')
smoothing_factor = config.getfloat('Customisation', 'smoothing_factor')
frame_rate = config.getint('Customisation', 'FrameRate')
background = config.get('Customisation', 'Background')
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

# Initialize PyAudio Object
p = PyAudioWrapper.PyAudioWrapper(CHUNK)


# Spotify #
sp = SpotipyWrapper.SpotipyWrapper(pygame.time.get_ticks(), cache_limit, spotify_update_rate)
if sp.results != None:
    album_art = pygame.image.load(io.BytesIO(sp.album_art_data))
    album_art = pygame.transform.scale_by(album_art, ResizedAlbumArtSize)


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
    print(random_background)
    Background = GifSprite.GifSprite(random_background, (0,0), fps=background_fps)
    Background.resize_frames(OriginalAppResolution[0] / Background.size[0],
                             OriginalAppResolution[1] / Background.size[1])
except Exception as e:
    # print("Error:", e, "\n\n")
    pass
drawArrayLength = 0
bass_reduction = 2
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
            # Background
            if Background != None:
                Background.resize_frames(w / Background.size[0],
                                h / Background.size[1])

    event_time = pygame.time.get_ticks()

    # AUDIO PROCESSING    
    # Read audio data
    try:
        data = np.frombuffer(p.stream.read(CHUNK), dtype=np.int16)
        fft_data = np.abs(np.fft.fft(data))[:CHUNK // 2]
    except Exception as error:
        # Hmm... I can't get here
        print("An error occurred:", type(error).__name__) # An error occurred: NameError

    
    if style == "Bars":
        # Reduced peaks
        # Calculate logarithmic frequency bins (only once if they don't change)
        if 'log_bins' not in globals():
            log_bins = np.logspace(0, np.log10(CHUNK//2), num=num_of_bars, base=10.0, dtype=int)
            log_bins = np.unique(log_bins)  # Remove duplicates

        drawArrayLength = len(log_bins)
        
        # Map FFT data to logarithmic bins
        log_fft_data = np.zeros(len(log_bins))
        for i in range(1, len(log_bins)):
            log_fft_data[i] = np.mean(fft_data[log_bins[i-1]:log_bins[i]])

        bass_reduction = 2

    if style == "Smooth" : 
        # Define the logarithmic scale
        log_freqs = np.logspace(np.log10(1), np.log10(CHUNK // 2), num=CHUNK // 2)

        # Linear frequency bins
        linear_freqs = np.linspace(0, CHUNK // 2, CHUNK // 2)

        # Interpolate the FFT data to the logarithmic scale
        log_fft_data = np.interp(log_freqs, linear_freqs, fft_data)

        drawArrayLength = len(log_fft_data)

        bass_reduction = 1

    # Apply exponential multiplier to emphasize high frequencies
    # Lower the "start" number in linspace, higher the bass reduction
    logarithmic_multiplier = np.log10(np.linspace(bass_reduction, 10, len(log_fft_data)))
    log_fft_data *= logarithmic_multiplier

    # Normalize the FFT data
    max_value = np.max(log_fft_data)

    # Make sure values hit minimum of 40% volume
    if max_value > 0:
        log_fft_data = log_fft_data / (max_value * 0.8)

    # Apply smoothing
    if previous_log_fft_data is not None:
        log_fft_data = smoothing_factor * previous_log_fft_data + (1 - smoothing_factor) * log_fft_data
    previous_log_fft_data = log_fft_data

    audio_time = pygame.time.get_ticks()

    # SPOTIFY PROCESSING
    if sp.update(pygame.time.get_ticks()) & (sp.results != None):
        album_art = pygame.image.load(io.BytesIO(sp.album_art_data))
        album_art = pygame.transform.scale_by(album_art, ResizedAlbumArtSize)

    spotify_time = pygame.time.get_ticks()

    # GRAPHICS PROCESSING

    # Background GIF
    if Background != None:
        screen.blit(Background.image, Background.pos)
        Background.update()
    else:
        screen.fill(background_colour)

    # Album Art colouring
    # Colour avg
    scalar = 255 - max(sp.avg_colour_album_art)
    Colour = (
                sp.avg_colour_album_art[0] + scalar * album_art_colour_vibrancy,
                sp.avg_colour_album_art[1] + scalar * album_art_colour_vibrancy, 
                sp.avg_colour_album_art[2] + scalar * album_art_colour_vibrancy
             )

    # Draw bars
    if max_value > 100:
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
            
    # Render Spotify Data
    if sp.results != None :
        # Render song name
        song_name = font_song_name.render(sp.results['item']['name'], 
                                          True, Colour)
        # Display song name
        screen.blit(song_name, (w * song_name_position[0], 
                                h - h * song_name_position[1]))

        # Render artist name
        artist_name = font_artist_name.render(sp.results['item']['artists'][0]['name'], 
                                              True, Colour)
        # Display artist name
        screen.blit(artist_name, (w * artist_name_position[0], 
                                  h - h * artist_name_position[1] + ResizedSongNameFontSize))

        # Display album art
        if (album_art != None) :
            screen.blit(album_art, (w * album_art_position[0],
                                    h - h * album_art_position[1]))
                    
    graphics_time = pygame.time.get_ticks()
    
    clock_time = pygame.time.get_ticks() - start_time
    if timingDebug & (clock_time > 1000/frame_rate):
        print("WARN: Underperforming! update took: ", clock_time, "ms \n",
                "Timings: \n events: ", event_time - start_time, 
                "ms \n audio: ", audio_time - event_time, 
                "ms \n spotify: ", spotify_time - audio_time, 
                "ms \n graphics: ", graphics_time - spotify_time, 
                "ms \n")

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(frame_rate)  # Lock the program to FPS


#####################################
#                Exit               #
#####################################
# Clean up
# Audio
p.stream.stop_stream()
p.stream.close()
# Graphics
pygame.quit()
