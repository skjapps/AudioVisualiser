import sdl2
import sdl2.ext
import OpenGL.GL as gl
import numpy as np

class Visualiser():
    def __init__(self, visualiser_size, visualiser_width=800, visualiser_height=480):
        self.width = int(visualiser_width * visualiser_size[0])  # Width of the visualiser display
        self.height = int(visualiser_height * visualiser_size[1])  # Height of the visualiser display

    def update(self, log_fft_data, max_value, album_art_colour_vibrancy, Colour, bar_thickness=1.0, bar_height_modifier=0.5):
        # Clear the screen
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        if max_value > 30:
            bar_width = 2.0 / len(log_fft_data)  # Normalize width to OpenGL coordinates
            for i in range(1, len(log_fft_data)):
                bar_height = log_fft_data[i] * bar_height_modifier  # Scale to screen height
                log_fft_data[i] = min(log_fft_data[i], 1)
                color = (
                    Colour[0] * min(log_fft_data[i], 0.8) + album_art_colour_vibrancy * 50,
                    Colour[1] * min(log_fft_data[i], 0.8) + album_art_colour_vibrancy * 50,
                    Colour[2] * min(log_fft_data[i], 0.8) + album_art_colour_vibrancy * 50
                )

                gl.glBegin(gl.GL_QUADS)
                gl.glColor3f(*color)
                gl.glVertex2f(-1.0 + i * bar_width, -1.0)
                gl.glVertex2f(-1.0 + (i + 1) * bar_width, -1.0)
                gl.glVertex2f(-1.0 + (i + 1) * bar_width, -1.0 + bar_height)
                gl.glVertex2f(-1.0 + i * bar_width, -1.0 + bar_height)
                gl.glEnd()

    def resize_surface(self, visualiser_size, width, height):
        self.width = int(width * visualiser_size[0])  # Width of the visualiser display
        self.height = int(height * visualiser_size[1])  # Height of the visualiser display
        gl.glViewport(0, 0, self.width, self.height)  # Update the OpenGL viewport