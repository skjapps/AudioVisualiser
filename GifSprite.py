import pygame
from PIL import Image

class GifSprite(pygame.sprite.Sprite):
    def __init__(self, gif_path, pos, fps=24, background_scale="Fill"):
        super().__init__()
        self._frames = self.load_gif(gif_path)
        self.image = self._frames[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pos
        self.size = self._frames[0].get_size()
        self.fading = False
        self.background_scale = background_scale

        self._frame_index = 0
        self._fps = fps
        self._clock = pygame.time.Clock()
        self._time_per_frame = 1000 // fps  # Time per frame in milliseconds
        self._last_update = pygame.time.get_ticks()
        self._fade_start_time = None
        self._fade_duration = None
        self._fade_in = False
        self._fade_out = False

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
        # Calculate the target width and height based on the first frame
        width = int(self.image.get_width() * x_stretch)
        height = int(self.image.get_height() * y_stretch)

        for i, frame in enumerate(self._frames):
            if self.background_scale == "Stretch":
                # Stretch based on the larger scale factor
                if x_stretch >= y_stretch:
                    self._frames[i] = pygame.transform.scale_by(frame, x_stretch)
                else:
                    self._frames[i] = pygame.transform.scale_by(frame, y_stretch)
            else:
                # Fill to the calculated width and height
                self._frames[i] = pygame.transform.scale(frame, (width, height))

        # Update the main image and rect
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
