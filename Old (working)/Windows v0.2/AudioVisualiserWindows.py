import numpy as np
import pygame
import pyaudiowpatch as pyaudio
import random
import GifSprite
import PyAudioWrapper

# Using Pyaudio based version package
# https://github.com/s0d3s/PyAudioWPatch/blob/master/examples/pawp_record_wasapi_loopback.py

# CUSTOMISATION (set with defaults)
NumOfBars = 50                                # Adjust this value for more or less bars (log bins)
smoothing_factor = 0.6                        # Adjust this value between 0 and 1 for more or less smoothing
FrameRate = 60                                # Adjust this value 60+ for more updates and refreshes?
Background = "assets/background1.gif"         # This sets the background image or GIF
Colour = (255,255,255)                        # Sets the colour of the visualisation (RGB)
Position = (0,0)                              # Position of the visualisation (x%, y%) move
Size = (1,1)                                  # Size of visualisation (0 to 1) NOT WORKING YET (rect spawns wrong place use scale)
NOFRAME = False                               # No border (window title bar)
FULLSCREEN = False                            # Fullscreen
BackgroundScale = "Fit"                       # UNIMPLEMENTED "Fill", "Fit", "Stretch", "Center", "Span" (some don't work lol)

# Audio stream parameters
CHUNK = 1024

#####################################
#               PYGAME              #
#####################################
# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((960, 600), flags=(pygame.RESIZABLE | (pygame.NOFRAME * NOFRAME) | (pygame.FULLSCREEN * FULLSCREEN)), vsync=1)
w, h = pygame.display.get_surface().get_size()
pygame.display.set_caption("Audio Visualizer")
clock = pygame.time.Clock()



# Initialize PyAudio Object
p = PyAudioWrapper.PyAudioWrapper(CHUNK)



#####################################
#             Main loop             #
#####################################
# Calculation variables:
previous_log_fft_data = None
# Program
running = True
background = GifSprite.GifSprite(Background, (0,0), fps=24)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.VIDEORESIZE:
            #  Get canvas size when resized
            w, h = pygame.display.get_surface().get_size()
    
    # Read audio data
    data = np.frombuffer(p.stream.read(CHUNK), dtype=np.int16)
    fft_data = np.abs(np.fft.fft(data))[:CHUNK // 2]

    # Reduced peaks
    # Calculate logarithmic frequency bins
    log_bins = np.logspace(0, np.log10(CHUNK // 2), num=NumOfBars, base=10.0, dtype=int)  # Reduced number of bins to 50
    log_bins = np.unique(log_bins)  # Remove duplicates

    # Map FFT data to logarithmic bins
    log_fft_data = np.zeros(len(log_bins))
    for i in range(1, len(log_bins)):
        log_fft_data[i] = np.mean(fft_data[log_bins[i-1]:log_bins[i]])
    
    # Normalize the FFT data
    # max_value = np.max(log_fft_data)
    # if max_value > 0:
    #     log_fft_data = log_fft_data / max_value

    # print(max_value)

    # Apply smoothing
    if previous_log_fft_data is not None:
        log_fft_data = smoothing_factor * previous_log_fft_data + (1 - smoothing_factor) * log_fft_data
    previous_log_fft_data = log_fft_data

    # Clear screen 
    screen.fill((0, 0, 0))

    # Background GIF
    screen.blit(background.image, background.pos)
    background.update()
    
    # Draw bars
    bar_width = w // len(log_bins)
    for i in range(len(log_bins)):
        # bar_height = log_fft_data[i] * h * np.clip(max_value, 0, 100000) * 0.0000001 * 100  # Scale to screen height
        bar_height = log_fft_data[i] * h * 0.00000005  # Scale to screen height
        pygame.draw.rect(screen, Colour, 
                         (i * bar_width + (Position[0] * w), 
                          h - bar_height + (-Position[1] * h), 
                          bar_width * Size[0], 
                          bar_height * Size[1]))

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
p.terminate()
# Graphics
pygame.quit()
