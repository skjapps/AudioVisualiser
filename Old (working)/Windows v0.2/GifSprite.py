import pygame
from PIL import Image

class GifSprite(pygame.sprite.Sprite):
    def __init__(self, gif_path, pos, fps=60):
        super().__init__()
        self.frames = self.load_gif(gif_path)
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pos
        self.frame_index = 0
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.time_per_frame = 1000 // fps  # Time per frame in milliseconds
        self.last_update = pygame.time.get_ticks()

    def load_gif(self, gif_path):
        ret = []
        gif = Image.open(gif_path)
        for frame_index in range(gif.n_frames):
            gif.seek(frame_index)
            frame_rgba = gif.convert("RGBA")
            pygame_image = pygame.image.fromstring(
                frame_rgba.tobytes(), frame_rgba.size, frame_rgba.mode
            )
            ret.append(pygame_image)
        return ret
    
    def resize_frames(self, x_stretch, y_stretch):
        resized_frames = []
        for frame in self.frames:
            width = int(frame.get_width() * x_stretch)
            height = int(frame.get_height() * y_stretch)
            resized_frame = pygame.transform.scale(frame, (width, height))
            resized_frames.append(resized_frame)
        self.frames = resized_frames
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.time_per_frame:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
