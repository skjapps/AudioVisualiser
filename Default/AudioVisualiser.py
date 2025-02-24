import asyncio
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
        asyncio.run(self.main())

    async def main(self):
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

        dot_count = config.getint('Customisation', 'ParticleCount')
        dot_size_range = tuple(map(float, config.get(
            'Customisation', 'ParticleSizeRange').split(',')))
        dots_speed_factor = config.getfloat('Customisation', 'ParticleSpeed')
        dots_direction = config.get('Customisation', 'ParticleDirection')

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
        await p.setup()

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
        screen = pygame.display.set_mode(OriginalAppResolution, flags=(
            pygame.RESIZABLE | (pygame.NOFRAME * no_frame) | (pygame.FULLSCREEN * fullscreen)))
        w, h = pygame.display.get_surface().get_size()
        clock = pygame.time.Clock()
        # Fonts setup
        available_fonts = pygame.font.get_fonts()
        font_song_name = pygame.font.SysFont('Arial', song_name_font_size)
        font_artist_name = pygame.font.SysFont('Arial', artist_name_font_size)

        # Create layered window
        if background_style == "Transparent":
            transparent_on_top(background_colour)

        if background_style == "GIF" or visualiser_image == "Background":
            try:
                background_folder = 'backgrounds'
                backgrounds = load_backgrounds(
                    background_folder, background_fps, OriginalAppResolution, background_scale)
                # backgroundManager = BackgroundManager(OriginalAppResolution)
            except Exception as Error:
                print(Error)
                # Reset style to simple colour
                background_style = "Colour"

        #####################################
        #              Options              #
        #####################################
        # Create an instance of OptionsWindow and close it
        options_window = OptionsScreen(config)
        options_window.close()

        # Spotify #
        # Spotify Branding
        spotify_icon_path = Functions.resource_path('assets/ico/spotify.png')
        spotify_icon = pygame.image.load(spotify_icon_path).convert_alpha()
        spotify_icon = pygame.transform.smoothscale_by(spotify_icon, 0.04)
        # Load Spotify Data
        if media_mode == "Spotify" or media_mode == "winsdk":
            sp = MediaInfoWrapper(media_mode, pygame.time.get_ticks(),
                                    cache_limit, media_update_rate)
            await sp.get_data()
            album_art = pygame.image.load(io.BytesIO(sp.album_art_data))
            album_art = pygame.transform.smoothscale_by(
                album_art, ResizedAlbumArtSize)
            if media_mode == "Spotify":
                artist_image = pygame.image.load(io.BytesIO(sp.artist_image_data))
                artist_image = pygame.transform.smoothscale_by(
                    artist_image, ResizedAlbumArtSize)
            sp.updated = False # Need to fix logic here...
            # Create an ImageFlipper instance
            flipper = ImageFlipper(album_art, artist_image, flip_interval=(
                1000 * album_art_flip_interval), flip_duration=(1000 * album_art_flip_duration))            
        
        #####################################
        #             Main loop             #
        #####################################
        # Objects:
        audio_processor = AudioProcess()
        visualiser = Visualiser(visualiser_size, visualiser_width=w, visualiser_height=h)
        oscilloscope = Oscilloscope(oscilloscope_size, oscilloscope_time_frame, oscilloscope_gain, p.default_speakers["defaultSampleRate"],
                                    oscilloscope_width=w, oscilloscope_height=h)
        hud = HUD((w,h))
        # Create a DotField instance
        dot_field = DotField(dot_field_width=w, dot_field_height=h, 
                             dot_count=dot_count, dot_size_range=dot_size_range, speed_factor=dots_speed_factor, direction=dots_direction, 
                             dot_color=(0,0,0), opacity=64)
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
                # Keyboard Buttons
                if event.type == pygame.KEYDOWN:
                    if (48 <= event.key <= 57):
                        options_counter = event.key - 48
                    # changing rotating options
                    if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                        # visualiser changes
                        if options_counter == 1:
                            visualiser_option_counter = abs((visualiser_option_counter+1) % len(visualiser_options))
                            visualiser_image = visualiser_options[visualiser_option_counter]
                        # oscilloscope changes
                        if options_counter == 2:
                            oscilloscope_option_counter = abs((oscilloscope_option_counter+1) % len(oscilloscope_options))
                            oscilloscope_acdc = oscilloscope_options[oscilloscope_option_counter]
                        # dot field changes
                        if options_counter == 3:
                            dot_field_option_counter = abs((dot_field_option_counter+1) % len(dot_field_options))
                            dot_field.direction = dot_field_options[dot_field_option_counter]
                    if event.key == pygame.K_UNDERSCORE or event.key == pygame.K_MINUS:
                        # visualiser changes
                        if options_counter == 1:
                            visualiser_option_counter = abs((visualiser_option_counter-1) % len(visualiser_options))
                            visualiser_image = visualiser_options[visualiser_option_counter]
                        # oscilloscope changes
                        if options_counter == 2:
                            oscilloscope_option_counter = abs((oscilloscope_option_counter-1) % len(oscilloscope_options))
                            oscilloscope_acdc = oscilloscope_options[oscilloscope_option_counter]
                        # dot field changes
                        if options_counter == 3:
                            dot_field_option_counter = abs((dot_field_option_counter-1) % len(dot_field_options))
                            dot_field.direction = dot_field_options[dot_field_option_counter]
                    if event.key == pygame.K_r:
                        # Re-Initialize PyAudio
                        await p.setup()
                    if event.key == pygame.K_q:
                        # Quit AV
                        self.re_run = False
                        pygame.event.post(pygame.event.Event(pygame.QUIT))
                    if event.key == pygame.K_o:
                        options_window.show()
                    if event.key == pygame.K_g:
                        oscilloscope_normalisation = not oscilloscope_normalisation
                    if event.key == pygame.K_LEFT:
                        font_index = (font_index - 1) % len(available_fonts)
                        font = available_fonts[font_index]
                        swap_font = True
                    if event.key == pygame.K_RIGHT:
                        font_index = (font_index + 1) % len(available_fonts)
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
                if event.type == pygame.MOUSEBUTTONDOWN and media_mode == "None":
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
                        webbrowser.open(
                            sp.results['item']['external_urls']['spotify'], new=0, autoraise=True)
                # Resizing window
                if event.type == pygame.VIDEORESIZE:
                    #  Get canvas size when resized (on instant)
                    w, h = pygame.display.get_surface().get_size()

                    # Changes for resize
                    # Visualiser Resize
                    visualiser.resize_surface(visualiser_size, w, h)
                    # Resize Rainbow Gif
                    rainbow_animate.resize_frames(w / rainbow_animate.size[0], h / rainbow_animate.size[1])
                    # Oscilloscope Resize
                    oscilloscope.resize_surface(oscilloscope_size, w, h)
                    # Dots Resize
                    dot_field.resize_surface(w, h)
                    # HUD Resize
                    hud.resize_surface((w, h))
                    # Info Font
                    # Max instead of min for wider resolutions
                    # Min instead of max for "phone" resolutions
                    ResizedSongNameFontSize = int(song_name_font_size * min(w/OriginalAppResolution[0],
                                                                            h/OriginalAppResolution[1]))
                    ResizedArtistNameFontSize = int(artist_name_font_size * min(w/OriginalAppResolution[0],
                                                                                h/OriginalAppResolution[1]))
                    ResizedAlbumArtSize = album_art_size * min(w/OriginalAppResolution[0],
                                                            h/OriginalAppResolution[1]) * 0.3
                    font_song_name = pygame.font.SysFont(font, ResizedSongNameFontSize)
                    font_artist_name = pygame.font.SysFont(font, ResizedArtistNameFontSize)
                    # Album art
                    album_art = pygame.image.load(io.BytesIO(sp.album_art_data))
                    album_art = pygame.transform.scale_by(
                        album_art, ResizedAlbumArtSize)
                    artist_image = pygame.image.load(io.BytesIO(sp.artist_image_data))
                    artist_image = pygame.transform.scale_by(
                        artist_image, ResizedAlbumArtSize)
                    if media_mode == "None":
                        flipper.change_images(album_art, artist_image)
                    # Background
                    if background_style == "GIF" or visualiser_image == "Background":
                        threads = []
                        width_ratio = w / background.size[0]
                        height_ratio = h / background.size[1]

                        for background in backgrounds:
                            thread = threading.Thread(target=background.resize_frames, args=(width_ratio, height_ratio))
                            threads.append(thread)
                            thread.start()

                        # Wait for all threads to finish
                        for thread in threads:
                            thread.join()
                    # win32gui.UpdateLayeredWindow(hwnd, None, None, None, None, None, win32api.RGB(*background_colour), None, win32con.LWA_COLORKEY)
                    # if media_mode == "Spotify":
                    #     spotify_icon = pygame.transform.scale_by(spotify_icon, w/OriginalAppResolution[0])

            # Detect change in audio device
            # Im not too sure how reliable this is, should still catch most cases of audio device change
            # ok this isn't working currently, could be fixed one day maybe
            if p.default_speakers['index'] is not p.get_default_speakers()['index']:
                # Re-setup for new speakers
                await p.setup()

            # AUDIO PROCESSING
            log_fft_data, max_value, bass_reading = audio_processor.perform_FFT(CHUNK, num_of_bars, bass_pump, smoothing_factor, low_pass_bass_reading, p)
            
            # SPOTIFY PROCESSING
            if media_mode != "None":
                await sp.update(pygame.time.get_ticks())
                if sp.updated:
                    try:
                        album_art = pygame.image.load(io.BytesIO(sp.album_art_data))
                        album_art = pygame.transform.smoothscale_by(
                            album_art, ResizedAlbumArtSize)
                        artist_image = pygame.image.load(io.BytesIO(sp.artist_image_data))
                        artist_image = pygame.transform.smoothscale_by(
                            artist_image, ResizedAlbumArtSize)
                        flipper.change_images(album_art, artist_image)
                        sp.updated = False
                    except Exception as error:
                        print(error, "\n\n")

            # GRAPHICS PROCESSING

            # Background GIF
            screen.fill(background_colour) # Clear screen
            if background_style == "GIF" or visualiser_image == "Background":
                for background in backgrounds:
                    # update any fading backgrounds
                    if background.fading:
                        if background_style == "GIF":
                            screen.blit(background.image, 
                                    background.image.get_rect(center=(w//2,h//2)).topleft)
                        background.update()
                if background_style == "GIF":
                    screen.blit(backgrounds[background_index].image,
                                backgrounds[background_index].image.get_rect(center=(w//2,h//2)).topleft)
                backgrounds[background_index].update()
            if background_style == "Artist":
                image_scaled = pygame.transform.smoothscale(pygame.transform.gaussian_blur(artist_image, 2), (w,h))
                screen.blit(image_scaled, image_scaled.get_rect(center=(w//2,h//2)).topleft)
            if background_style == "Album":
                image_scaled = pygame.transform.smoothscale(pygame.transform.gaussian_blur(album_art, 2), (w,h))
                screen.blit(image_scaled, image_scaled.get_rect(center=(w//2,h//2)).topleft)

            # Album Art colouring
            # Colour avg
            if album_art_colouring and media_mode != "None":
                scalar = 255 - max(sp.avg_colour_album_art)
                Colour = (
                    sp.avg_colour_album_art[0] + scalar * album_art_colour_vibrancy,
                    sp.avg_colour_album_art[1] + scalar * album_art_colour_vibrancy,
                    sp.avg_colour_album_art[2] + scalar * album_art_colour_vibrancy
                )

            # Update the visualiser
            dot_field.update(bass_reading, dot_count, dots_speed_factor)
            dot_field_rect = dot_field.surface.get_rect(center=(w/2,h/2))

            # Update the visualiser
            visualiser.update(log_fft_data, max_value, album_art_colour_vibrancy, Colour, bar_thickness, bar_height)
            # Render Visualiser to main screen
            visualiser_rect = visualiser.surface.get_rect(center=(int(w * visualiser_position[0]), 
                                                        int(h - h * visualiser_position[1])))

            # Update the oscilloscope
            gain_change = 1e4
            if oscilloscope_normalisation:
                gain_change = max(np.max(p.mono_data), 1e3)
            oscilloscope.update_oscilloscope(
                p.mono_data / gain_change, album_art_colour_vibrancy=album_art_colour_vibrancy, 
                                                            colour=Colour, mode=oscilloscope_acdc)
            oscilloscope_rect = oscilloscope.surface.get_rect(center=(int(w * oscilloscope_position[0]), 
                                                            int(h - h * oscilloscope_position[1])))
            
            if visualiser_image == "None":
                # screen.blit(pygame.transform.flip(visualiser.surface, True, False), rect)
                # screen.blit(pygame.transform.flip(visualiser.surface, False, True), rect)
                screen.blit(dot_field.surface, dot_field_rect)
                screen.blit(visualiser.surface, visualiser_rect)
                # Blit the oscilloscope surface onto the main screen
                screen.blit(oscilloscope.surface, oscilloscope_rect)
            else:
                # Filter for colours and other visuals
                filter = pygame.Surface((w,h))
                # Make masks from the visualiser(s)
                mask_main = pygame.Mask((w,h))
                mask1 = pygame.mask.from_surface(visualiser.surface)
                mask2 = pygame.mask.from_surface(oscilloscope.surface)
                mask3 = pygame.mask.from_surface(dot_field.surface)

                # Make the Filter
                if visualiser_image == "Rainbow": 
                    filter.blit(rainbow_animate.image,
                                rainbow_animate.image.get_rect(center=(w//2,h//2)).topleft)
                    rainbow_animate.update(fps=int(bass_reading*55) + 5)
                elif visualiser_image == "Artist":
                    image_scaled = pygame.transform.smoothscale(pygame.transform.gaussian_blur(artist_image, 2), (w,h))
                    filter.blit(image_scaled, image_scaled.get_rect(center=(w//2,h//2)).topleft)
                elif visualiser_image == "Album":
                    image_scaled = pygame.transform.smoothscale(pygame.transform.gaussian_blur(album_art, 2), (w,h))
                    filter.blit(image_scaled, image_scaled.get_rect(center=(w//2,h//2)).topleft)
                elif visualiser_image == "Background":
                    image_scaled = pygame.Surface((w,h))
                    for background in backgrounds:
                        # update any fading backgrounds
                        if background.fading:
                            image_scaled.blit(background.image, background.pos)
                    image_scaled.blit(backgrounds[background_index].image,
                                backgrounds[background_index].pos)
                    filter.blit(image_scaled, image_scaled.get_rect().topleft)

                # Combine the visualiser masks
                mask_main.draw(mask3, dot_field_rect.topleft)
                mask_main.draw(mask1, visualiser_rect.topleft)
                mask_main.draw(mask2, oscilloscope_rect.topleft)
                mask_surface = mask_main.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
                # Apply mask to filter
                filter.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                filter.set_colorkey((0,0,0))
                # Blit Filter with visualisers to screen
                screen.blit(filter, (0,0))
            
            # Render Spotify Data
            # If spotify is being used, show spotify logo
            # if media_mode == "Spotify":
            #     screen.blit(spotify_icon, (w - spotify_icon.get_width(),
            #                                 0))
            # When data changes
            if media_mode != "None":
                if sp.changed:
                    if random_font_swap:
                        font = random.choice(available_fonts)
                        swap_font = True
                    if background_style == "GIF" or visualiser_image == "Background":
                        # change background with fade when song changed...
                        if (len(backgrounds) > 1):
                            backgrounds[background_index].start_fade_out(
                                background_fade_duration * 1000)
                            backgrounds[(background_index + 1) % len(backgrounds)
                                        ].start_fade_in(background_fade_duration * 1000)
                            background_index = (background_index + 1) % len(backgrounds)
                    sp.changed = False

            if swap_font:
                font_song_name = pygame.font.SysFont(
                    font, ResizedSongNameFontSize, True)
                font_artist_name = pygame.font.SysFont(
                    font, ResizedArtistNameFontSize, True)
                swap_font = False

            # Render song name
            if media_mode != "None":
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
                if (album_art != None) or (artist_image != None):
                    try:
                        # Incase size changed
                        ResizedAlbumArtSize = album_art_size * max(w/OriginalAppResolution[0],
                                                                h/OriginalAppResolution[1]) * 0.3

                        # Update the flipper
                        flipper.update()

                        # Render the current image
                        flipper.render(screen, (w * album_art_position[0],
                                            h - h * album_art_position[1]))
                    except Exception as error:
                        print(error)

            # Update and draw HUD
            hud.update(media_mode, clock.get_fps())
            screen.blit(hud.surface, (0,0))

            # Update display
            pygame.display.flip()

            # Get options changes
            frame_rate = options_window.frame_rate.get()
            num_of_bars = options_window.num_of_bars.get()
            bass_pump = options_window.bass_pump.get()
            bar_thickness = options_window.bars_width.get()
            smoothing_factor = options_window.smoothing_factor.get()
            background_fade_duration = options_window.fade_duration.get()
            oscilloscope.gain = options_window.oscilloscope_gain.get()
            low_pass_bass_reading = options_window.bass_low_pass.get()
            dot_count = options_window.dot_count.get()
            dots_speed_factor = options_window.dot_speed_factor.get()
            # For media
            if media_mode != "None":
                sp.media_update_rate = options_window.media_update_rate.get()
                album_art_size = options_window.album_art_size.get()
                album_art_colour_vibrancy = options_window.album_art_colour_vibrancy.get()
                flipper.flip_interval = 1000 * options_window.album_art_flip_interval.get()
                flipper.flip_duration = 1000 * options_window.album_art_flip_duration.get()
            # Positioning
            if options_window.selected_element.get() == "Album Art":
                album_art_position = (options_window.x_value.get(),
                                        options_window.y_value.get())
            if options_window.selected_element.get() == "Song Name":
                song_name_position = (options_window.x_value.get(),
                                        options_window.y_value.get())
            if options_window.selected_element.get() == "Artist Name":
                artist_name_position = (options_window.x_value.get(),
                                        options_window.y_value.get())
            if options_window.selected_element.get() == "Visualiser Position":
                visualiser_position = (options_window.x_value.get(),
                                        options_window.y_value.get())
            if options_window.selected_element.get() == "Visualiser Size":
                visualiser_size = (options_window.x_value.get(),
                                    options_window.y_value.get())
                visualiser.resize_surface(visualiser_size, w, h)
            if options_window.selected_element.get() == "Oscilloscope Position":
                oscilloscope_position = (
                    options_window.x_value.get(), options_window.y_value.get())
            if options_window.selected_element.get() == "Oscilloscope Size":
                oscilloscope_size = (options_window.x_value.get(),
                                    options_window.y_value.get())
                oscilloscope.resize_surface(oscilloscope_size, w, h)

            # Periodically call the Tkinter event loop
            options_window.window.update_idletasks()
            options_window.window.update()

            # Close the app automatically (to allow sleep pc)
            if sleep_time != 0:
                if getIdleTime() >= (sleep_time * 60):
                    running = False

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
        options_window.close()

        # Get performance Stats
        if performanceDebug:
            profiler.disable()
            with open('.\\profiling_stats.txt', 'w') as f:
                stats = pstats.Stats(profiler, stream=f)
                stats.sort_stats(pstats.SortKey.TIME)
                stats.print_stats()

        # # exit fully
        # exit()