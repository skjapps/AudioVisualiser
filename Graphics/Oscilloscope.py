import pygame
import numpy as np

#####################################
#            Oscilliscope           #
#####################################
class Oscilloscope():
    def __init__(self, oscilloscope_size, oscilloscope_time_frame, oscilloscope_gain, sample_rate, oscilloscope_width=400, oscilloscope_height=160):
        self.width = int(oscilloscope_width * oscilloscope_size[0])  # Width of the oscilloscope display
        self.height = int(oscilloscope_height * oscilloscope_size[1]) # Height of the oscilloscope display
        self.gain = oscilloscope_gain
        self.max_samples = int(oscilloscope_time_frame * sample_rate)  # Maximum number of samples to store
        self._accumulated_audio_data = np.zeros(self.max_samples)  # Zero array for accumulated audio data
        self.current_length = 0  # Current number of samples stored
        
        # Create oscilloscope surface
        self.surface = pygame.Surface((self.width, self.height))

    def append_audio_data(self, new_data):
        new_length = len(new_data)

        if self.current_length + new_length > self.max_samples:
            # Shift existing data to the left to make room for new data
            shift_amount = self.current_length + new_length - self.max_samples
            self._accumulated_audio_data[:-shift_amount] = self._accumulated_audio_data[shift_amount:]
            self.current_length = self.max_samples  # We are now at max capacity
        else:
            self.current_length += new_length

        # Add new data to the end of the array
        self._accumulated_audio_data[-new_length:] = new_data

    def remove_dc_offset(self, data: np.ndarray) -> np.ndarray:
        """Remove the DC offset from a given array of data.

        Args:
            data (np.ndarray): The input array of data, expected to be an array of floats.

        Returns:
            np.ndarray: The input array with the DC offset removed, also an array of floats.
        """
        return data - np.mean(data)

    def update_oscilloscope(self, audio_data, album_art_colour_vibrancy=1, colour=(0, 255, 0)):
        """Update the oscilloscope with the given audio data and album art colour vibrancy.

        Args:
            audio_data (np.ndarray): The array of audio data to render.
            album_art_colour_vibrancy (int, optional): The vibrancy of the album art colour to use. Defaults to 1.
            colour (tuple, optional): The colour to render the oscilloscope with, as a tuple of (r, g, b) values. Defaults to (0, 255, 0).

        Returns:
            None
        """
        
        # Clear the oscilloscope surface
        self.surface.fill((0, 0, 0))
        self.surface.set_colorkey((0, 0, 0))

        # If width or height are 0, dont render
        if (self.width > 0) and (self.height > 0):
            # Remove DC offset
            audio_data = self.remove_dc_offset(audio_data)
            self.append_audio_data(audio_data * self.gain)
            
            if self.current_length == 0:
                return

            scaled_data = self._accumulated_audio_data[:self.current_length]
            scaled_data = np.clip(scaled_data, -1, 1)

            # Render audio data
            for x in range(self.width):
                sample_index = int((x / self.width) * self.current_length)
                if sample_index < self.current_length:
                    y = int((scaled_data[sample_index] + 1) * (self.height / 2))
                    normalized_height = abs(self.height // 2 - y) / (self.height // 2) * 3
                    # Draw line
                    pygame.draw.line(self.surface, (
                    (colour[0] * min(normalized_height, 0.8) +
                    album_art_colour_vibrancy * 50),
                    (colour[1] * min(normalized_height, 0.8) +
                    album_art_colour_vibrancy * 50),
                    (colour[2] * min(normalized_height, 0.8) + 
                    album_art_colour_vibrancy * 50)), 
                    (x, y), (x, self.height - y), width=2)

    def resize_surface(self, oscilloscope_size, width, height):
        self.width = int(width * oscilloscope_size[0])  # Width of the oscilloscope display
        self.height = int(height * oscilloscope_size[1]) # Height of the oscilloscope display

        # Resize the surface to the new size
        self.surface = pygame.transform.scale(self.surface, (width, height))
