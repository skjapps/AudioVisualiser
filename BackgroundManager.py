import pygame
import GifSprite
import os

class BackgroundManager:
    def __init__(self, app_resolution, background_folder='backgrounds', background_fps=24, background_scale="Scale"):
        self.background_folder = background_folder
        self.app_resolution = app_resolution
        self.background_change = False # flag to know when the background fades are done

        self.current_background_filename = os.listdir(self.background_folder)[0]
        self.current_background = self.load_and_resize_background(self, self.current_background_filename, background_fps, background_scale)

        # self.next_background_filename = os.listdir(self.background_folder)[1]
        # self.next_background = self.load_and_resize_background(self, self.next_background_filename, background_fps, background_scale)

    def load_and_resize_background(self, filename, background_fps, background_scale):
        background_path = os.path.join(self.background_folder, filename)
        background = GifSprite(os.path.join(background_path, self.current_background_filename), 
                                            (0, 0), fps=background_fps, background_scale=background_scale)
        background.resize_frames(
            self.app_resolution[0] / background.size[0], 
            self.app_resolution[1] / background.size[1])
        return background

    def change_background(self, fade_duration):

        # get list of current backgrounds
        current_backgrounds = os.listdir(self.background_folder)
        # index of the background in list
        try:
            current_background_index = current_backgrounds.index(self.current_background_filename)
        except ValueError:
            current_background_index = 0

        # Load the next background
        self.next_background = self.load_and_resize_background(current_backgrounds[current_background_index + 1])
        
        # Start the fades
        self.current_background.start_fade_out(fade_duration)
        self.next_background.start_fade_in(fade_duration)

        # True flag
        self.background_change = True

    def resize(self, new_resolution):
        if self.current_background:

    
    def update(self):
        # render fading backgrounds
        if self.current_background.fading:
                screen.blit(background.image, background.pos)
                background.update()
        # turn the current into next when the fades are done...
        if (self.background_change) :
            
        pass