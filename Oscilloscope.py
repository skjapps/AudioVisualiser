import pygame
import numpy as np

#####################################
#            Oscilliscope           #
#####################################
class Oscilloscope():
    def __init__(self, oscilloscope_time_frame, oscilloscope_gain, sample_rate, oscilloscope_width=400, oscilloscope_height = 160):
        self.width = oscilloscope_width  # Width of the oscilloscope display
        self.height = oscilloscope_height  # Height of the oscilloscope display
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

    def remove_dc_offset(self, data):
        return data - np.mean(data)

    def compress_audio(self, signal, threshold, ratio):
        # Apply compression
        compressed_signal = np.where(signal > threshold, 
                                    threshold + (signal - threshold) / ratio, 
                                    signal)
        return compressed_signal

    def update_oscilloscope(self, audio_data, album_art_colour_vibrancy=1, colour=(0, 255, 0)):
        # Remove DC offset
        audio_data = self.remove_dc_offset(audio_data)
        self.append_audio_data(audio_data * self.gain)

        # Clear the oscilloscope surface
        self.surface.fill((0, 0, 0))
        self.surface.set_colorkey((0, 0, 0))

        if self.current_length == 0:
            return

        scaled_data = self._accumulated_audio_data[:self.current_length]
        scaled_data = np.clip(scaled_data, -1, 1)

        for x in range(self.width):
            sample_index = int((x / self.width) * self.current_length)
            if sample_index < self.current_length:
                y = int((scaled_data[sample_index] + 1) * (self.height / 2))
                normalized_height = abs(self.height // 2 - y) / (self.height // 2) * 3
                pygame.draw.line(self.surface, (
                (colour[0] * min(normalized_height, 0.8) +
                album_art_colour_vibrancy * 50),
                (colour[1] * min(normalized_height, 0.8) +
                album_art_colour_vibrancy * 50),
                (colour[2] * min(normalized_height,
                0.8) + album_art_colour_vibrancy * 50)
                ), (x, self.height // 2), (x, y), width=2)
                pygame.draw.line(self.surface, (
                (colour[0] * min(normalized_height, 0.8) +
                album_art_colour_vibrancy * 50),
                (colour[1] * min(normalized_height, 0.8) +
                album_art_colour_vibrancy * 50),
                (colour[2] * min(normalized_height,
                0.8) + album_art_colour_vibrancy * 50)
                ), (x, self.height // 2), (x, self.height - y), width=2)