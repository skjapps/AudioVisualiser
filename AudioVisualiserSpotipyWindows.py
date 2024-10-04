import numpy as np
import pygame
import io
import os
import GifSprite
import PyAudioWrapper
import SpotipyWrapper
import ctypes
import random

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
# Cache folder size limit (in MB)
cache_limit = 1

# (With set defaults)
Style = "Bars"                                # Style can be "Bars" for monstercat-esque, or "Smooth" for EQ like
NumOfBars = 80                                # Adjust this value for more or less bars (log bins)
smoothing_factor = 0.7                        # Adjust this value between 0 and 1 for more or less smoothing
FrameRate = 60                                # Adjust this value 60+ for more updates and refreshes?
Background = None                             # This sets the background image or GIF
BackgroundColour = (75,75,75)                 # Default Background colour
BackgroundFPS = 36                            # Background FrameRate
Colour = (255,255,255)                        # Sets the colour of the visualisation (RGB)
VisualiserPosition = (0,0)                    # Position of the visualisation (x%, y%) move
Size = (1,1)                                  # Size of visualisation (0 to 1) NOT WORKING YET (rect spawns wrong place use scale)
NOFRAME = False                               # No border (window title bar)
FULLSCREEN = False                            # Fullscreen
BackgroundScale = "Fit"                       # UNIMPLEMENTED "Fill", "Fit", "Stretch", "Center", "Span"
BassPump = 0                                  # 0 to 1 for more bass shown

ArtistNamePosition = (0.02,0.95)              # Position of the artist name (x%, y%) move
# Size of font for artist name
ArtistNameFontSize = ResizedArtistNameFontSize = 56
SongNamePosition = (0.02,0.95)                # Position of the song name (x%, y%) move
# Size of font for song name
SongNameFontSize = ResizedSongNameFontSize = 74
AlbumArtPosition = (0.775,0.95)               # Position of the album art image (x%, y%) move
# Mulitplier (ie 1x, 1.5x, 2x) of art size
AlbumArtSize = 1
ResizedAlbumArtSize = 0.3
AlbumArtColouring = True                      # Colour the graphics to the colour of the album art
AlbumArtColourVibrancy = 1                    # 0 to 1, higher number = brighter colours from album art                      


#####################################
#               PYGAME              #
#####################################
# Window Sizing in windows...
if os.name == 'nt' :
    ctypes.windll.user32.SetProcessDPIAware()
# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode(OriginalAppResolution, flags=(pygame.RESIZABLE | (pygame.NOFRAME * NOFRAME) | (pygame.FULLSCREEN * FULLSCREEN)), vsync=1)
w, h = pygame.display.get_surface().get_size()
pygame.display.set_caption("Audio Visualiser")
pygame.display.set_icon(pygame.image.load('assets/ico/ico.png'))
clock = pygame.time.Clock()
# Fonts setup
font_song_name = pygame.font.SysFont('Arial', SongNameFontSize)
font_artist_name = pygame.font.SysFont('Arial', ArtistNameFontSize)

# To initialise variables
album_art = None

# Initialize PyAudio Object
p = PyAudioWrapper.PyAudioWrapper(CHUNK)


# Spotify #
sp = SpotipyWrapper.SpotipyWrapper(pygame.time.get_ticks(), cache_limit)
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
    Background = GifSprite.GifSprite(random_background, (0,0), fps=BackgroundFPS)
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
            ResizedSongNameFontSize = int(SongNameFontSize * max(w/OriginalAppResolution[0],
                                                                h/OriginalAppResolution[1]))
            ResizedArtistNameFontSize = int(ArtistNameFontSize * max(w/OriginalAppResolution[0],
                                                                h/OriginalAppResolution[1]))
            ResizedAlbumArtSize = AlbumArtSize * max(w/OriginalAppResolution[0],
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

    
    if Style == "Bars":
        # Reduced peaks
        # Calculate logarithmic frequency bins (only once if they don't change)
        if 'log_bins' not in globals():
            log_bins = np.logspace(0, np.log10(CHUNK//2), num=NumOfBars, base=10.0, dtype=int)
            log_bins = np.unique(log_bins)  # Remove duplicates

        drawArrayLength = len(log_bins)
        
        # Map FFT data to logarithmic bins
        log_fft_data = np.zeros(len(log_bins))
        for i in range(1, len(log_bins)):
            log_fft_data[i] = np.mean(fft_data[log_bins[i-1]:log_bins[i]])

        bass_reduction = 2

    if Style == "Smooth" : 
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
        screen.fill(BackgroundColour)

    # Album Art colouring
    # Colour avg
    scalar = 255 - max(sp.avg_colour_album_art)
    Colour = (
                sp.avg_colour_album_art[0] + scalar * AlbumArtColourVibrancy,
                sp.avg_colour_album_art[1] + scalar * AlbumArtColourVibrancy, 
                sp.avg_colour_album_art[2] + scalar * AlbumArtColourVibrancy
             )

    # Draw bars
    if max_value > 100:
        bar_width = w // drawArrayLength
        for i in range(1, drawArrayLength):
            bar_height = log_fft_data[i] * h * 0.5 # Scale to screen height
            log_fft_data[i] = min(log_fft_data[i], 1)
            pygame.draw.rect(screen, (
                                        (Colour[0] * min(log_fft_data[i], 0.5) + AlbumArtColourVibrancy * 125), 
                                        (Colour[1] * min(log_fft_data[i], 0.5) + AlbumArtColourVibrancy * 125), 
                                        (Colour[2] * min(log_fft_data[i], 0.5) + AlbumArtColourVibrancy * 125),
                                    ), 
                            (i * bar_width + (VisualiserPosition[0] * w), 
                            h - bar_height + (-VisualiserPosition[1] * h), 
                            bar_width * Size[0], 
                            bar_height * Size[1]))
            
    # Render Spotify Data
    if sp.results != None :
        # Render song name
        song_name = font_song_name.render(sp.results['item']['name'], 
                                          True, Colour)
        # Display song name
        screen.blit(song_name, (w * SongNamePosition[0], 
                                h - h * SongNamePosition[1]))

        # Render artist name
        artist_name = font_artist_name.render(sp.results['item']['artists'][0]['name'], 
                                              True, Colour)
        # Display artist name
        screen.blit(artist_name, (w * ArtistNamePosition[0], 
                                  h - h * ArtistNamePosition[1] + ResizedSongNameFontSize))

        # Display album art
        if (album_art != None) :
            screen.blit(album_art, (w * AlbumArtPosition[0],
                                    h - h * AlbumArtPosition[1]))
                    
    graphics_time = pygame.time.get_ticks()
    
    clock_time = pygame.time.get_ticks() - start_time
    if timingDebug & (clock_time > 1000/FrameRate):
        print("WARN: Underperforming! update took: ", clock_time, "ms \n",
                "Timings: \n events: ", event_time - start_time, 
                "ms \n audio: ", audio_time - event_time, 
                "ms \n spotify: ", spotify_time - audio_time, 
                "ms \n graphics: ", graphics_time - spotify_time, 
                "ms \n")

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FrameRate)  # Lock the program to FPS


#####################################
#                Exit               #
#####################################
# Clean up
# Audio
p.stream.stop_stream()
p.stream.close()
# Graphics
pygame.quit()
