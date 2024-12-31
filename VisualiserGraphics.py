import pygame

import numpy as np
import pygame

class Visualiser():
    def __init__(self, visualiser_width=800, visualiser_height = 600):
        self.width = visualiser_width  # Width of the oscilloscope display
        self.height = visualiser_height  # Height of the oscilloscope display

        # Create visualiser surface
        self.surface = pygame.Surface((self.width, self.height))

    def update(self, log_fft_data, max_value, album_art_colour_vibrancy, Colour, bar_thickness=1.0):

        # Clear the visuiliser surface
        self.surface.fill((0, 0, 0))
        self.surface.set_colorkey((0, 0, 0))

        # Render Visualiser to internal pygame surface
        if (max_value > 30):
            bar_width = self.width // len(log_fft_data)
            for i in range(1, len(log_fft_data)):
                bar_height = log_fft_data[i] * self.height * 0.5  # Scale to screen height
                log_fft_data[i] = min(log_fft_data[i], 1)
                pygame.draw.rect(self.surface, (
                    (Colour[0] * min(log_fft_data[i], 0.8) +
                    album_art_colour_vibrancy * 50),
                    (Colour[1] * min(log_fft_data[i], 0.8) +
                    album_art_colour_vibrancy * 50),
                    (Colour[2] * min(log_fft_data[i],
                                    0.8) + album_art_colour_vibrancy * 50)
                    ),
                    # (i * bar_width + (visualiser_position[0] * self.width),
                    # self.height - bar_height + (-visualiser_position[1] * self.height),
                    # bar_width * visualiser_size[0],
                    # bar_height * visualiser_size[1]))
                    (i * bar_width,
                    self.height - bar_height,
                    bar_width * bar_thickness,
                    bar_height))