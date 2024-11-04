import pygame
import tkinter as tk
import sys
from pathlib import Path
from PIL import Image, ImageTk
from tkinter import ttk
import configparser

class OptionsWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Options")
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.slider_list_names = ["Album Art", "Song Name", "Artist Name", "Visualiser Position", "Visualiser Size"]
        # self.slider_index = self.slider_list_names.index(self.selected_element.get())

        # Get the path to the icon file
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).resolve().parent
        image_path = base_path / 'assets/img/options.png'

        # Load the background image
        self.background_image = Image.open(image_path)
        self.background_photo = ImageTk.PhotoImage(self.background_image)

        # Create a canvas to display the background image
        self.canvas = tk.Canvas(self.window, width=self.background_image.width, height=self.background_image.height)
        self.canvas.pack(fill="both")
        self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

        # Initialize the parser
        config = configparser.ConfigParser()
        # Read the configuration file
        config.read('config.cfg')

        # Define variables to be controlled by sliders
        self.bass_pump = tk.DoubleVar(value=config.getfloat('Customisation', 'BassPump'))
        self.smoothing_factor = tk.DoubleVar(value=config.getfloat('Customisation', 'smoothing_factor'))
        self.frame_rate = tk.IntVar(value=config.getint('Customisation', 'FrameRate'))
        self.media_update_rate = tk.IntVar(value=config.getint('Customisation', 'media_update_rate'))
        self.num_of_bars = tk.IntVar(value=config.getint('Customisation', 'NumOfBars'))
        self.album_art_size = tk.DoubleVar(value=config.getfloat('Customisation', 'AlbumArtSize'))
        self.album_art_colour_vibrancy = tk.DoubleVar(value=config.getfloat('Customisation', 'AlbumArtColourVibrancy'))
        self.album_art_flip_interval = tk.DoubleVar(value=config.getfloat('Customisation', 'AlbumArtFlipInterval'))
        self.album_art_flip_duration = tk.DoubleVar(value=config.getfloat('Customisation', 'AlbumArtFlipDuration'))
        # Array of x/y values
        self.xy_variables = [list(tuple(map(float, config.get('Customisation', 'AlbumArtPosition').split(',')))),
                             list(tuple(map(float, config.get('Customisation', 'SongNamePosition').split(',')))),
                             list(tuple(map(float, config.get('Customisation', 'ArtistNamePosition').split(',')))),
                             list(tuple(map(float, config.get('Customisation', 'VisualiserPosition').split(',')))),
                             list(tuple(map(float, config.get('Customisation', 'VisualiserSize').split(','))))]

        # Variables for position sliders
        self.selected_element = tk.StringVar(value="Album Art")
        self.x_position = tk.DoubleVar(value=self.xy_variables[self.slider_list_names.index(self.selected_element.get())][0])
        self.y_position = tk.DoubleVar(value=self.xy_variables[self.slider_list_names.index(self.selected_element.get())][1])

        # Create sliders
        self.create_slider("Frame Rate", self.frame_rate, 1, 60, 1, 0.25, 75, "white", ("Helvetica", 14))
        self.create_slider("Bass Pump", self.bass_pump, 0, 1, 0.1, 0.25, 175, "white", ("Helvetica", 14))
        self.create_slider("Bars", self.num_of_bars, 10, config.getint('Customisation', 'CHUNK') // 2, 1, 0.25, 275, "white", ("Helvetica", 14))
        self.create_slider("Smoothing Factor", self.smoothing_factor, 0, 1, 0.025, 0.25, 375, "white", ("Helvetica", 14))
        self.create_slider("Media Update Rate (seconds)", self.media_update_rate, 1, 10, 1, 0.25, 475, "white", ("Helvetica", 14))
        self.create_slider("Album Art Size", self.album_art_size, 0.5, 5, 0.1, 0.75, 75, "white", ("Helvetica", 14))
        self.create_slider("Colour Vibrancy", self.album_art_colour_vibrancy, 0, 1, 0.05, 0.75, 175, "white", ("Helvetica", 14))
        # self.create_slider("Album Art Flip Interval", self.album_art_flip_interval, 0, 10, 0.5, 0.75, 275, "white", ("Helvetica", 14))
        # self.create_slider("Album Art Flip Duration", self.album_art_flip_duration, 0, 1, 0.1, 0.75, 375, "white", ("Helvetica", 14))

        # Create position sliders
        self.x_slider = self.create_slider("X Position", self.x_position, 0, 1, 0.005, 0.75, 275, "white", ("Helvetica", 14))
        self.y_slider = self.create_slider("Y Position", self.y_position, 0, 1, 0.005, 0.75, 375, "white", ("Helvetica", 14))

        # Create buttons to select the element to move
        self.create_button("Album Art", 0.25, 575)
        self.create_button("Song Name", 0.5, 575)
        self.create_button("Artist Name", 0.75, 575)
        self.create_button("Visualiser Position", 0.25, 625)
        self.create_button("Visualiser Size", 0.5, 625)

    def create_slider(self, label, variable, from_, to, resolution, horizontal_position, y_position, text_colour, font):
        label_widget = ttk.Label(self.window, text=label, foreground=text_colour, background='black', font=font)
        label_widget.place(relx=horizontal_position, y=y_position - 40, anchor='center')
        slider = tk.Scale(self.window, from_=from_, to=to, orient='horizontal', variable=variable, 
                           resolution=resolution, length=200, background="black", foreground=text_colour)
        slider.place(relx=horizontal_position, y=y_position, anchor='center')
    
    # def create_slider_command(self, label, variable, from_, to, resolution, horizontal_position, y_position, text_colour, font, command):
    #     label_widget = ttk.Label(self.window, text=label, foreground=text_colour, background='black', font=font)
    #     label_widget.place(relx=horizontal_position, y=y_position - 40, anchor='center')
    #     slider = tk.Scale(self.window, from_=from_, to=to, orient='horizontal', variable=variable, 
    #                        resolution=resolution, length=200, background="black", foreground=text_colour,
    #                        command=command)
    #     slider.place(relx=horizontal_position, y=y_position, anchor='center')

    #     return slider

    # def update_value(self):
    #     self.xy_variables[self.slider_index] = [self.x_position.get(),self.y_position.get()]

    def create_button(self, label, horizontal_position, y_position):
        button = ttk.Button(self.window, text=label, command=lambda: self.select_element(label))
        button.place(relx=horizontal_position, y=y_position, anchor='center')

    def select_element(self, element):
        #Set previous ones
        self.xy_variables[self.slider_list_names.index(self.selected_element.get())] = [self.x_position.get(),
                                                                                        self.y_position.get()]
        #Change
        self.selected_element.set(element)
        self.slider_index = self.slider_list_names.index(self.selected_element.get())
        #Load new ones
        self.x_position.set(self.xy_variables[self.slider_list_names.index(self.selected_element.get())][0])
        self.y_position.set(self.xy_variables[self.slider_list_names.index(self.selected_element.get())][1])

    def close(self):
        self.window.withdraw()

    def show(self):
        self.window.deiconify()

# Example usage
# options_window = OptionsWindow()
# options_window.show()
# tk.mainloop()
