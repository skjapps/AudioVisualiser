import numpy as np
import pygame
import pyaudio
import random
from collections import namedtuple

# Audio stream parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# PYGAME
# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((960, 600), flags=pygame.RESIZABLE, vsync=1)
pygame.display.set_caption("Audio Visualizer")

# Initialize PyAudio
p = pyaudio.PyAudio()

# List all available devices
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"Device {i}: {info['name']}")

# List all available devices and their channel information
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"Device {i}: {info['name']}, Max Input Channels: {info['maxInputChannels']}, Max Output Channels: {info['maxOutputChannels']}")

# Set the device index (replace with your desired device index)
# device_index = 4

# Open audio stream with the selected device
stream = p.open(format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=44100,
                input=True,
                # input_device_index=device_index,
                frames_per_buffer=1024)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read audio data
    data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
    # Average the two channels to get a mono signal
    # mono_data = np.mean(data.reshape(-1, 2), axis=1)
    fft_data = np.abs(np.fft.fft(data))[:CHUNK // 2]

    # Calculate logarithmic frequency bins
    log_bins = np.logspace(0, np.log10(CHUNK // 2), num=CHUNK // 2, base=10.0, dtype=int)
    log_bins = np.unique(log_bins)  # Remove duplicates

    # Map FFT data to logarithmic bins
    log_fft_data = np.zeros(len(log_bins))
    for i in range(1, len(log_bins)):
        log_fft_data[i] = np.mean(fft_data[log_bins[i-1]:log_bins[i]])
    
    # Normalize the FFT data
    max_value = np.max(log_fft_data)
    if max_value > 0:
        log_fft_data = log_fft_data / max_value

    print(max_value)

    # Clear screen
    screen.fill((0, 0, 0))

    w, h = pygame.display.get_surface().get_size()

    # Draw bars
    bar_width = w // len(log_bins)
    for i in range(len(log_bins)):
        bar_height = log_fft_data[i] * h * np.clip(max_value, 0, 100000) * 0.0000001 * 100 # Scale to screen height
        pygame.draw.rect(screen, (random.randint(100,175), random.randint(75,150), random.randint(175,255)), (i * bar_width, h - bar_height, bar_width, bar_height))

    # Update display
    pygame.display.flip()

# Clean up
stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()