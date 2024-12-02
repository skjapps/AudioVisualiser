import pygame
import GifSprite
import os

class BackgroundManager:
    def __init__(self, background_folder, app_resolution, background_fps=24, background_scale="Scale"):
        self.background_folder = background_folder
        self.current_background_filename = os.listdir(self.background_folder)[0]
        self.current_background = GifSprite(os.path.join(background_folder, self.current_background_filename), 
                                            (0, 0), fps=background_fps, background_scale=background_scale)
        self.current_background.resize_frames(
            app_resolution[0] / self.current_background.size[0], app_resolution[1] / self.current_background.size[1])
        self.next_background = None

    def load_background(self, filename):
        background_path = os.path.join(self.background_folder, filename)
        return GifSprite(background_path, (0, 0))  # Adjust as needed

    def change_background(self, direction):
        current_backgrounds = os.listdir(self.background_folder)
        if self.current_background:
            self.fade_out(self.current_background)

        self.next_background = self.load_background(new_background_file)
        self.fade_in(self.next_background)
    
    def update()

# Usage
background_manager = BackgroundManager('backgrounds')

# On song change
background_manager.change_background('new_background.gif')
