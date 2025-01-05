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
import sys
import win32api
import win32con
import win32gui
import webbrowser
import threading
import numpy as np

from Graphics.GifSprite import GifSprite
from Graphics.VisualiserGraphics import Visualiser
# from BackgroundManager import BackgroundManager
from Graphics.ImageFlipper import ImageFlipper
from Graphics.OptionsScreen import OptionsWindow
from Graphics.Oscilloscope import Oscilloscope
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

def main():
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
    # Get the path to the icon file
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent
    icon_path = base_path / 'assets/ico/ico.png'
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

    if background_style == "GIF":
        try:
            background_folder = 'backgrounds'
            background_fps = 30
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
    options_window = OptionsWindow()
    options_window.close()

    # Spotify #
    # Spotify Branding
    spotify_icon_path = base_path / 'assets/ico/spotify.png'
    spotify_icon = pygame.image.load(spotify_icon_path).convert_alpha()
    spotify_icon = pygame.transform.smoothscale_by(spotify_icon, 0.04)
    # Load Spotify Data
    if media_mode == "Spotify":
        sp = MediaInfoWrapper(media_mode, pygame.time.get_ticks(),
                                cache_limit, media_update_rate)
        album_art = pygame.image.load(io.BytesIO(sp.album_art_data))
        album_art = pygame.transform.smoothscale_by(
            album_art, ResizedAlbumArtSize)
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
    rainbow_image = pygame.transform.scale(
                    pygame.transform.gaussian_blur(
                    (pygame.image.load(('assets/img/rainbow.jpg')).convert_alpha()), 5), (w,h))
    test_counter_1 = 0
    # Main Loop
    while running:

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
                    webbrowser.open(
                        sp.results['item']['external_urls']['spotify'], new=0, autoraise=True)
            # Resizing window
            if event.type == pygame.VIDEORESIZE:
                #  Get canvas size when resized (on instant)
                w, h = pygame.display.get_surface().get_size()

                # Changes for resize
                # Visualiser Resize
                visualiser.resize_surface(visualiser_size, w, h)
                # Resize Rainbow image
                rainbow_image = pygame.transform.scale(rainbow_image, (w, h))
                # Oscilloscope Resize
                oscilloscope.resize_surface(oscilloscope_size, w, h)
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
                flipper.change_images(album_art, artist_image)
                # Background
                if background_style == "GIF":
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

        # AUDIO PROCESSING
        log_fft_data, max_value = audio_processor.perform_FFT(CHUNK, num_of_bars, bass_pump, smoothing_factor, p)

        # SPOTIFY PROCESSING
        sp.update(pygame.time.get_ticks())
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
        if background_style == "GIF":
            for background in backgrounds:
                # update any fading backgrounds
                if background.fading:
                    screen.blit(background.image, background.pos)
                    background.update()
            screen.blit(backgrounds[background_index].image,
                        backgrounds[background_index].pos)
            backgrounds[background_index].update()
        else:
            screen.fill(background_colour)

        # Album Art colouring
        # Colour avg
        if album_art_colouring:
            scalar = 255 - max(sp.avg_colour_album_art)
            Colour = (
                sp.avg_colour_album_art[0] + scalar * album_art_colour_vibrancy,
                sp.avg_colour_album_art[1] + scalar * album_art_colour_vibrancy,
                sp.avg_colour_album_art[2] + scalar * album_art_colour_vibrancy
            )

        # Update the visualiser
        visualiser.update(log_fft_data, max_value, album_art_colour_vibrancy, Colour, bar_thickness)
        # Render Visualiser to main screen
        rect = visualiser.surface.get_rect(center=(int(w * visualiser_position[0]), 
                                                    int(h - h * visualiser_position[1])))
        
        if visualiser_image == "None":
            screen.blit(pygame.transform.flip(visualiser.surface, True, False), rect)
            screen.blit(pygame.transform.flip(visualiser.surface, False, True), rect)
        else:
            filter = pygame.Surface((w,h))
            # Make masks from the visualiser(s)
            mask1 = pygame.mask.from_surface(pygame.transform.flip(visualiser.surface, True, False))
            mask2 = pygame.mask.from_surface(pygame.transform.flip(visualiser.surface, False, True))
            # Make the Rainbow Filter
            test_counter_1 = ((test_counter_1 + 1) % (frame_rate * 2))
            test_scalar_1 = (math.sin(math.pi * 2 * (test_counter_1 / (frame_rate * 2)))) / 5
            if visualiser_image == "Rainbow": 
                image_scaled = pygame.transform.scale_by(rainbow_image, 1.2 + test_scalar_1)
            elif visualiser_image == "Artist":
                image_scaled = pygame.transform.smoothscale_by(artist_image, 
                                                            max(w//artist_image.get_width(), h//artist_image.get_height()))
            filter.blit(image_scaled, image_scaled.get_rect(center=(rainbow_image.get_width() // 2, 
                                                                        rainbow_image.get_height() // 2)))

            # Combine the visualiser masks
            mask1.draw(mask2, (0,0))
            mask_surface = mask1.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
            # Apply mask to filter
            filter.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            filter.set_colorkey((0,0,0))
            # Blit Filter with visualisers to screen
            screen.blit(filter, (0, 0))
        

        # Blit the oscilloscope surface onto the main screen
        if oscilloscope_normalisation:
            oscilloscope.update_oscilloscope(
                p.mono_data / max(np.max(p.mono_data), 1e3), album_art_colour_vibrancy=album_art_colour_vibrancy, 
                                                            colour=Colour, mode=oscilloscope_acdc)
        elif not oscilloscope_normalisation:
            oscilloscope.update_oscilloscope(
                p.mono_data / 1e4, album_art_colour_vibrancy=album_art_colour_vibrancy, 
                                                        colour=Colour, mode=oscilloscope_acdc)
        rect = oscilloscope.surface.get_rect(center=(int(w * oscilloscope_position[0]), 
                                                        int(h - h * oscilloscope_position[1])))
        screen.blit(oscilloscope.surface, rect)
        
        # Render Spotify Data
        # If spotify is being used, show spotify logo
        # if media_mode == "Spotify":
        #     screen.blit(spotify_icon, (w - spotify_icon.get_width(),
        #                                 0))
        # When data changes
        if sp.changed:
            if random_font_swap:
                font = random.choice(available_fonts)
                swap_font = True
            if background_style == "GIF":
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
        if options_window.selected_element.get() == "Album Art":
            album_art_position = (options_window.x_position.get(),
                                    options_window.y_position.get())
        if options_window.selected_element.get() == "Song Name":
            song_name_position = (options_window.x_position.get(),
                                    options_window.y_position.get())
        if options_window.selected_element.get() == "Artist Name":
            artist_name_position = (options_window.x_position.get(),
                                    options_window.y_position.get())
        if options_window.selected_element.get() == "Visualiser Position":
            visualiser_position = (options_window.x_position.get(),
                                    options_window.y_position.get())
        if options_window.selected_element.get() == "Visualiser Size":
            visualiser_size = (options_window.x_position.get(),
                                options_window.y_position.get())
            visualiser.resize_surface(visualiser_size, w, h)
        if options_window.selected_element.get() == "Oscilloscope Position":
            oscilloscope_position = (
                options_window.x_position.get(), options_window.y_position.get())
        if options_window.selected_element.get() == "Oscilloscope Size":
            oscilloscope_size = (options_window.x_position.get(),
                                options_window.y_position.get())
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
        with open('profiling_stats.txt', 'w') as f:
            stats = pstats.Stats(profiler, stream=f)
            stats.sort_stats(pstats.SortKey.TIME)
            stats.print_stats()

    # exit fully
    exit()

if __name__ == '__main__':
    main()
