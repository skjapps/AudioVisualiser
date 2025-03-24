import numpy as np
import pygame

class AudioProcess():
    def __init__(self):
        self.previous_log_fft_data = []

    def perform_FFT(self, CHUNK, num_of_bars, bass_pump, smoothing_factor, low_pass_bass_reading, p):
        # AUDIO PROCESSING
        try:
            fft_data = np.abs(np.fft.fft(p.mono_data))[:CHUNK // 2]
        except Exception as error:
            print("An error occurred:", error)

        # The new maths
        # Smooth interpretation
        log_freqs = np.logspace(np.log10(1), np.log10(CHUNK // 2), num=CHUNK // 2)
        linear_freqs = np.linspace(0, CHUNK // 2, CHUNK // 2)
        smooth_log_fft_data = np.interp(log_freqs, linear_freqs, fft_data)

        # Create evenly spaced bins for averaging
        bins = np.linspace(0, len(smooth_log_fft_data), num_of_bars + 1, dtype=int)

        # Averaging the smooth log fft data into bars
        log_fft_data = np.array(
            [np.mean(smooth_log_fft_data[bins[i]:bins[i+1]]) for i in range(num_of_bars)])

        # Bass reduction
        # log10 of a linear 1 to 10, for the right effect.
        logarithmic_multiplier = np.power(np.log10(np.linspace(
            1 + 1*bass_pump, 10, len(log_fft_data))), 2*(1-bass_pump))
        log_fft_data *= logarithmic_multiplier

        # Normalisation of values
        max_value = max(np.max(log_fft_data), 1e3)
        if max_value > 0:
            log_fft_data = log_fft_data / max_value

        # Calculate the bass reading
        sample_rate = p.default_speakers["defaultSampleRate"]
        desired_freq = low_pass_bass_reading
        freqs = np.fft.fftfreq(len(smooth_log_fft_data), d=1/sample_rate)
        closest_index = max(np.argmin(np.abs(freqs - desired_freq)), 1)
        
        bass_region = log_fft_data[:closest_index]
        bass_reading = np.max(bass_region)

        # Apply smoothing for visualisation
        if (self.previous_log_fft_data is not None) & (len(log_fft_data) == len(self.previous_log_fft_data)):
            log_fft_data = smoothing_factor * self.previous_log_fft_data + \
                (1 - smoothing_factor) * log_fft_data
        self.previous_log_fft_data = log_fft_data

        return log_fft_data, max_value, bass_reading