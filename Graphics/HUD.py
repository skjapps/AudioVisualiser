import sys
import pygame

from pathlib import Path

from Default import Functions

class HUD():
    def __init__(self, HUD_size):
        self.size = HUD_size # HUD size is tuple
    
        self.spotify_icon = pygame.transform.smoothscale_by(
                            pygame.image.load(
                            Functions.resource_path('assets/ico/spotify.png')).convert_alpha(), 0.03)

        # Create HUD surface
        self.surface = pygame.Surface(self.size)
        # 1x scale, will change to fractions or multiples to calculate sizing
        self.scale = 1
        self.original_size = HUD_size

        self.basic_font = pygame.font.SysFont('Arial', 24)

        # Run to create scaled objects
        self.__resize_objects__()

    def update(self, media_mode, frame_rate):

        # Clear the HUD surface
        self.surface.fill((0, 0, 0))
        self.surface.set_colorkey((0, 0, 0))

        # Render Menu Button
        

        # If spotify is being used, show spotify logo
        if media_mode == "Spotify":
            self.surface.blit(self.spotify_icon_scaled, 
                                self.__getposition__(0.975, 0.95, self.spotify_icon_scaled)) 
        
        # Show FPS...
        fps = self.basic_font.render(str(int(frame_rate)), True, (255,255,255))
        self.surface.blit(fps, self.__getposition__(0.025, 0.95, fps))
    
    def resize_surface(self, HUD_size):
        self.size = HUD_size # HUD size is tuple 

        # Getting scale
        self.scale = min(self.size[0] / self.original_size[0], 
                            self.size[1] / self.original_size[1])

        # Resize the surface to the new size
        self.surface = pygame.transform.scale(self.surface, self.size)

        self.__resize_objects__()

    def __resize_objects__(self):
        # Update with all objects being rendered, running only at resize improves efficiency
        self.spotify_icon_scaled = self.__getscale__(self.spotify_icon, "smooth")
        # self.basic_font_scaled = self.__getscale__(self.basic_font, "linear")

    def __getposition__(self, x, y, surface):
        """
        Internal function to calculate the position on the HUD surface given relative x, y coordinates.

        :param x: Relative x position on the HUD surface (0 to 1)
        :param y: Relative y position on the HUD surface (0 to 1)
        :return: The position on the HUD surface as a tuple (x, y)
        """

        position = ((self.size[0] * x), self.size[1] - (self.size[1] * y))
        centre = (surface.get_width() // 2, surface.get_height() // 2)
        blit_position = (position[0] - centre[0], position[1] - centre[1])
        return blit_position
    
    def __getscale__(self, object, scale_type):
        if scale_type == "smooth":
            return pygame.transform.smoothscale_by(object, self.scale)
        elif scale_type == "linear":
            return pygame.transform.scale_by(object, self.scale)