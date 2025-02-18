import asyncio
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
import webbrowser
import win32api
import win32con
import win32gui
# import pickle

from GifSprite import GifSprite
from PyAudioWrapper import PyAudioWrapper
from MediaInfoWrapper import MediaInfoWrapper
from ImageFlipper import ImageFlipper
from OptionsScreen import OptionsWindow
from Oscilloscope import Oscilloscope

from pathlib import Path

#####################################
#            Functions              #
#####################################
def transparent_on_top():
    hwnd = pygame.display.get_wm_info()["window"]
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                        win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
    # Set window transparency color
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*background_colour), 0, win32con.LWA_COLORKEY)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 1|2) # NOMOVE|NOSIZE...

def load_and_cache_backgrounds(background_folder, cache_folder, background_fps, app_resolution, background_scale):
    backgrounds = []
    
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)
    
    for filename in os.listdir(background_folder):
        if filename.endswith('.gif'):
            background_path = os.path.join(background_folder, filename)
            cache_path = os.path.join(cache_folder, f"{filename}.pkl")

            background = GifSprite(background_path, (0, 0), fps=background_fps, background_scale=background_scale)
            background.resize_frames(app_resolution[0] / background.size[0], app_resolution[1] / background.size[1])

            # if os.path.exists(cache_path):
            #     with open(cache_path, 'rb') as cache_file:
            #         background = pickle.load(cache_file)
            # else:
            #     background = GifSprite(background_path, (0, 0), fps=background_fps)
            #     background.resize_frames(app_resolution[0] / background.size[0], app_resolution[1] / background.size[1])
                
            #     with open(cache_path, 'wb') as cache_file:
            #         pickle.dump(background, cache_file)
            
            backgrounds.append(background)
    
    return backgrounds

# Define a function to open the Tkinter window
def open_options():
    options_window.show()

async def main():
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
    cache_limit = config.getint('Customisation', 'cache_limit')
    media_mode = config.get('Customisation', 'media_mode')
    media_update_rate = config.getint('Customisation', 'MediaUpdateRate')

    # Graphics Customisation
    num_of_bars = config.getint('Customisation', 'NumOfBars')
    smoothing_factor = config.getfloat('Customisation', 'SmoothingFactor')
    frame_rate = config.getint('Customisation', 'FrameRate')
    background_style = config.get('Customisation', 'BackgroundStyle')
    background_colour = tuple(map(int, config.get('Customisation', 'BackgroundColour').split(',')))
    background_fps = config.getint('Customisation', 'BackgroundFPS')
    colour = tuple(map(int, config.get('Customisation', 'Colour').split(',')))
    visualiser_position = tuple(map(float, config.get('Customisation', 'VisualiserPosition').split(',')))
    visualiser_size = tuple(map(float, config.get('Customisation', 'VisualiserSize').split(',')))
    oscilloscope_position = tuple(map(float, config.get('Customisation', 'OscilloscopePosition').split(',')))
    oscilloscope_time_frame = config.getfloat('Customisation', 'OscilloscopeTimeFrame')
    oscilloscope_gain = config.getfloat('Customisation', 'OscilloscopeGain')
    no_frame = config.getboolean('Customisation', 'NOFRAME')
    fullscreen = config.getboolean('Customisation', 'FULLSCREEN')
    background_scale = config.get('Customisation', 'BackgroundScale')
    background_fade_duration = config.getfloat('Customisation', 'BackgroundFadeDuration')
    bass_pump = config.getfloat('Customisation', 'BassPump')

    # Song Data Graphics Config
    random_font_swap = config.getboolean('Customisation', 'RandomFontSwap')
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
    screen = pygame.display.set_mode(OriginalAppResolution, flags=(pygame.RESIZABLE | (pygame.NOFRAME * no_frame) | (pygame.FULLSCREEN * fullscreen)))
    w, h = pygame.display.get_surface().get_size()
    clock = pygame.time.Clock()
    # Fonts setup
    available_fonts = pygame.font.get_fonts()
    font_song_name = pygame.font.SysFont('Arial', song_name_font_size, True)
    font_artist_name = pygame.font.SysFont('Arial', artist_name_font_size, True)

    # Create layered window
    if background_style == "Transparent":
        transparent_on_top()
        
    if background_style == "GIF" :
        try:
            background_folder = 'backgrounds'
            cache_folder = 'cache/obj/back'
            background_fps = 30
            backgrounds = load_and_cache_backgrounds(background_folder, cache_folder, background_fps, OriginalAppResolution, background_scale)
        except Exception as Error:
            print(Error)
            # Reset style to simple colour
            background_style = "Colour"

    #####################################
    #              Options              #
    #####################################
    # Create an instance of OptionsWindow and close it
    options_window = OptionsWindow()
    options_window.close()



    #####################################
    #            Oscilliscope           #
    #####################################
    oscilloscope = Oscilloscope(oscilloscope_time_frame, oscilloscope_gain, p.default_speakers["defaultSampleRate"])

    # To initialise variables
    album_art = None
    artist_image = None

    # Spotify #
    # Spotify Branding
    spotify_icon_path = base_path / 'assets/ico/spotify.png'
    spotify_icon = pygame.image.load(spotify_icon_path).convert_alpha()
    spotify_icon = pygame.transform.smoothscale_by(spotify_icon, 0.04)
    if media_mode == "Spotify" :
        sp = MediaInfoWrapper(media_mode, pygame.time.get_ticks(), cache_limit, media_update_rate)
        if sp.results != None:
            album_art = pygame.image.load(io.BytesIO(sp.album_art_data))
            album_art = pygame.transform.smoothscale_by(album_art, ResizedAlbumArtSize)
            artist_image = pygame.image.load(io.BytesIO(sp.artist_image_data))
            artist_image = pygame.transform.smoothscale_by(artist_image, ResizedAlbumArtSize)
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
    background_index = 0
    font = 'Arial' # Initialised to default font
    font_index = 0 # Counting font change index
    swap_font = False # Flag to swap font when pressed left/right
    change_background = False # Flag to change background when pressed up/down
    scalar = 0 # colour scaling
    while running:
        
        start_time = pygame.time.get_ticks()

        # Pygame Events (Quit, Window Resize)
        for event in pygame.event.get():
            # Quit
            if event.type == pygame.QUIT:
                running = False
            # Keyboard Buttons
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                if event.key == pygame.K_o:
                    open_options()
                if event.key == pygame.K_LEFT:
                    font_index = (font_index - 1)%len(available_fonts)
                    font = available_fonts[font_index]
                    swap_font = True
                if event.key == pygame.K_RIGHT:
                    font_index = (font_index + 1)%len(available_fonts)
                    font = available_fonts[font_index]
                    swap_font = True
                # if event.key == pygame.K_UP:
                #     background_index = (background_index + 1)%len(backgrounds)
                #     change_background = True
                # if event.key == pygame.K_DOWN:
                #     background_index = (background_index - 2)%len(backgrounds)
                #     change_background = True
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
            # Mouse Clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If spotify button is clicked (postions of the mouse click)
                # print(event.pos, "\n\n")
                flipper_rect = pygame.rect.Rect((album_art_position[0] * w - (flipper.current_image.get_width()/2), 
                                                (h - album_art_position[1] * h) - (flipper.current_image.get_height()/2)), 
                                                flipper.current_image.get_size())
                if spotify_icon.get_rect().collidepoint(event.pos):
                    # Open Spotify
                    webbrowser.open("https://open.spotify.com", new=0, autoraise=True)
                if flipper_rect.collidepoint(event.pos):
                    # Open track in spotify when clicking album art
                    webbrowser.open(sp.results['item']['external_urls']['spotify'], new=0, autoraise=True)
            # Resizing window
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
                font_song_name = pygame.font.SysFont(font, ResizedSongNameFontSize)
                font_artist_name = pygame.font.SysFont(font, ResizedArtistNameFontSize)
                # Album art
                if sp.results != None:
                    album_art = pygame.image.load(io.BytesIO(sp.album_art_data))
                    album_art = pygame.transform.smoothscale_by(album_art, ResizedAlbumArtSize)
                    artist_image = pygame.image.load(io.BytesIO(sp.artist_image_data))
                    artist_image = pygame.transform.smoothscale_by(artist_image, ResizedAlbumArtSize)
                    flipper.change_images(album_art, artist_image)
                # Background
                if background_style == "GIF":
                    for background in backgrounds:
                        background.resize_frames(w / background.size[0],
                                        h / background.size[1])
                # win32gui.UpdateLayeredWindow(hwnd, None, None, None, None, None, win32api.RGB(*background_colour), None, win32con.LWA_COLORKEY)
                # if media_mode == "Spotify":
                #     spotify_icon = pygame.transform.scale_by(spotify_icon, w/OriginalAppResolution[0])
        event_time = pygame.time.get_ticks()

        # AUDIO PROCESSING
        try:
            fft_data = np.abs(np.fft.fft(p.mono_data))[:CHUNK // 2]
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
        max_value = max(np.max(log_fft_data), 1e3)
        if max_value > 0:
            log_fft_data = log_fft_data / (max_value * 0.8)

        if (previous_log_fft_data is not None) & (len(log_fft_data) == len(previous_log_fft_data)):
            log_fft_data = smoothing_factor * previous_log_fft_data + (1 - smoothing_factor) * log_fft_data
        previous_log_fft_data = log_fft_data

        audio_time = pygame.time.get_ticks()

        # SPOTIFY PROCESSING
        await sp.update(pygame.time.get_ticks())
        if sp.updated & (sp.results != None):
            try:
                album_art = pygame.image.load(io.BytesIO(sp.album_art_data))
                album_art = pygame.transform.smoothscale_by(album_art, ResizedAlbumArtSize)
                artist_image = pygame.image.load(io.BytesIO(sp.artist_image_data))
                artist_image = pygame.transform.smoothscale_by(artist_image, ResizedAlbumArtSize)
                flipper.change_images(album_art, artist_image)
                sp.updated = False
            except Exception as error:
                print(error, "\n\n")

        spotify_time = pygame.time.get_ticks()

        # GRAPHICS PROCESSING

        # Background GIF
        if background_style == "GIF":
            for background in backgrounds:
                # update any fading backgrounds
                if background.fading:
                    screen.blit(background.image, background.pos)
                    background.update()
            screen.blit(backgrounds[background_index].image, backgrounds[background_index].pos)
            backgrounds[background_index].update()
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

        # Blit the oscilloscope surface onto the main screen
        oscilloscope.update_oscilloscope(p.mono_data / max(np.max(p.mono_data), 1e3), colour=Colour)
        # update_oscilloscope(compress_audio(p.mono_data / 1e7, 0.5, 4), colour=Colour)
        screen.blit(oscilloscope.surface, (w * oscilloscope_position[0], 
                                            h - h * oscilloscope_position[1]))

        # update_oscilloscope(p.mono_data, colour=Colour) # (fallback to this if needed)

        # Render Spotify Data
        if sp.results != None :
            # If spotify is being used, show spotify logo
            if media_mode == "Spotify" :
                screen.blit(spotify_icon, (0,
                                        0))
            # When data changes
            if sp.changed:
                if random_font_swap:
                    font = random.choice(available_fonts)
                    swap_font = True
                if background_style == "GIF":
                    # change background with fade when song changed...
                    if(len(backgrounds) > 1):
                        backgrounds[background_index].start_fade_out(background_fade_duration * 1000)
                        backgrounds[(background_index + 1)%len(backgrounds)].start_fade_in(background_fade_duration * 1000)
                        background_index = (background_index + 1)%len(backgrounds)
                sp.changed = False
                
            if swap_font:
                font_song_name = pygame.font.SysFont(font, ResizedSongNameFontSize, True)
                font_artist_name = pygame.font.SysFont(font, ResizedArtistNameFontSize, True)
                swap_font = False

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
        sp.media_update_rate = options_window.media_update_rate.get()
        bass_pump = options_window.bass_pump.get()
        smoothing_factor = options_window.smoothing_factor.get()
        album_art_size = options_window.album_art_size.get()
        album_art_colour_vibrancy = options_window.album_art_colour_vibrancy.get()
        background_fade_duration = options_window.fade_duration.get()
        flipper.flip_interval = 1000 * options_window.album_art_flip_interval.get()
        flipper.flip_duration = 1000 * options_window.album_art_flip_duration.get()
        oscilloscope.gain = options_window.oscilloscope_gain.get()
        # Positioning
        if options_window.selected_element.get() == "Album Art" :
            album_art_position = (options_window.x_position.get(),options_window.y_position.get())
        if options_window.selected_element.get() == "Song Name" :
            song_name_position = (options_window.x_position.get(),options_window.y_position.get())
        if options_window.selected_element.get() == "Artist Name" :
            artist_name_position = (options_window.x_position.get(),options_window.y_position.get())
        if options_window.selected_element.get() == "Visualiser Position" :
            visualiser_position = (options_window.x_position.get(),options_window.y_position.get())
        if options_window.selected_element.get() == "Visualiser Size" :
            visualiser_size = (options_window.x_position.get(),options_window.y_position.get())
        if options_window.selected_element.get() == "Oscilliscope Position" :
            oscilloscope_position = (options_window.x_position.get(),options_window.y_position.get())
        
        # Periodically call the Tkinter event loop
        options_window.window.update_idletasks()
        options_window.window.update()

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

    # Get performance Stats
    if performanceDebug:
        profiler.disable()
        with open('profiling_stats.txt', 'w') as f:
            stats = pstats.Stats(profiler, stream=f)
            stats.sort_stats(pstats.SortKey.TIME)
            stats.print_stats()

# Run the main function
asyncio.create_task(main())
