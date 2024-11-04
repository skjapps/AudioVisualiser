import pygame
from PIL import Image

class GifSprite(pygame.sprite.Sprite):
    def __init__(self, gif_path, pos, fps=60):
        super().__init__()
        self._frames = self.load_gif(gif_path)
        self.image = self._frames[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pos
        self.size = self._frames[0].get_size()
        self._frame_index = 0
        self._fps = fps
        self._clock = pygame.time.Clock()
        self._time_per_frame = 1000 // fps  # Time per frame in milliseconds
        self._last_update = pygame.time.get_ticks()
        self._fade_start_time = None
        self._fade_duration = None
        self._fade_in = False
        self._fade_out = False
        self.fading = False

    def load_gif(self, gif_path):
        ret = []
        gif = Image.open(gif_path)
        for frame_index in range(gif.n_frames):
            gif.seek(frame_index)
            frame_rgba = gif.convert("RGBA")
            pygame_image = pygame.image.fromstring(
                frame_rgba.tobytes(), frame_rgba.size, frame_rgba.mode
            )
            # Convert the surface to the display format
            pygame_image = pygame_image.convert_alpha()
            ret.append(pygame_image)
        return ret
    
    def resize_frames(self, x_stretch, y_stretch):
        resized_frames = []
        for frame in self._frames:
            width = int(frame.get_width() * x_stretch)
            height = int(frame.get_height() * y_stretch)
            resized_frame = pygame.transform.scale(frame, (width, height))
            resized_frames.append(resized_frame)
        self._frames = resized_frames
        self.image = self._frames[0]
        self.rect = self.image.get_rect(topleft=self.pos)
        self.size = self._frames[0].get_size()

    def start_fade_in(self, duration):
        self._fade_in = True
        self._fade_out = False
        self._fade_start_time = pygame.time.get_ticks()
        self._fade_duration = duration
        self.fading = True

    def start_fade_out(self, duration):
        self._fade_out = True
        self._fade_in = False
        self._fade_start_time = pygame.time.get_ticks()
        self._fade_duration = duration
        self.fading = True

    def update(self):
        now = pygame.time.get_ticks()
        if now - self._last_update > self._time_per_frame:
            self._last_update = now
            self._frame_index = (self._frame_index + 1) % len(self._frames)
            self.image = self._frames[self._frame_index]

        if self._fade_in or self._fade_out:
            elapsed_time = now - self._fade_start_time
            if elapsed_time < self._fade_duration:
                fade_progress = elapsed_time / self._fade_duration
                if self._fade_in:
                    opacity = int(255 * fade_progress)
                elif self._fade_out:
                    opacity = int(255 * (1 - fade_progress))
                self.apply_opacity(opacity)
            else:
                if self._fade_in:
                    self.apply_opacity(255)
                elif self._fade_out:
                    self.apply_opacity(0)
                self._fade_in = False
                self._fade_out = False
                self.fading = False

    def apply_opacity(self, opacity):
        frame = self._frames[self._frame_index].copy()
        frame.fill((255, 255, 255, opacity), special_flags=pygame.BLEND_RGBA_MULT)
        self.image = frame
