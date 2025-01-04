import sys
import pygame

from pathlib import Path

class HUD():
    def __init__(self, HUD_size):
        self.size = HUD_size # HUD size is tuple
        # Get the base path
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).resolve().parent

        self.spotify_icon = pygame.transform.smoothscale_by(
                            pygame.image.load(
                                base_path / '../assets/ico/spotify.png').convert_alpha(), 0.04
                            )

        # Create HUD surface
        self.surface = pygame.Surface(self.size)

    def update(self, media_mode):

        # Clear the HUD surface
        self.surface.fill((0, 0, 0))
        self.surface.set_colorkey((0, 0, 0))

        # Render Menu Button
        

        # If spotify is being used, show spotify logo
        if media_mode == "Spotify":
            self.surface.blit(self.spotify_icon, (self.width * 0.9, self.height * 0.1))
    
    def resize_surface(self, HUD_size):
        self.size = HUD_size # HUD size is tuple 

        # Resize the surface to the new size
        self.surface = pygame.transform.scale(self.surface, self.size)