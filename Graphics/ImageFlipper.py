import pygame
import math

class ImageFlipper:
    def __init__(self, image1_pygame_surface, image2_pygame_surface, flip_interval, flip_duration):
        self.image1 = image1_pygame_surface
        self.image2 = image2_pygame_surface
        self.flip_interval = flip_interval
        self.flip_duration = flip_duration
        self.last_flip_time = pygame.time.get_ticks()
        self.current_image = self.image1
        self.flipping = False
        self.scale_width = 1
        self.scale_height = 1
        self.image_switched = False

    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.last_flip_time

        if self.flipping:
            t = elapsed_time / self.flip_duration
            if t >= 1:
                self.flipping = False
                self.last_flip_time = current_time
                self.scale_width = 1
                self.image_switched = False
            else:
                if t >= 0.5 and not self.image_switched:
                    self.current_image = self.image2 if self.current_image == self.image1 else self.image1
                    self.image_switched = True
                self.scale_width = self.ease_in_out_cosine(t)
                self.scale_height = self.ease_in_out_sine(t)

        elif elapsed_time >= self.flip_interval:
            self.flipping = True
            self.last_flip_time = current_time

    def render(self, screen, position):
        if self.flipping:
            scaled_width = int(self.current_image.get_width() * self.scale_width)
            scaled_height = int(self.current_image.get_height() + (self.current_image.get_height() * self.scale_height * 0.1))
            if scaled_width > 0:  # Ensure width is positive
                scaled_image = pygame.transform.scale(self.current_image, (scaled_width, scaled_height))
                rect = scaled_image.get_rect(center=position)
                screen.blit(scaled_image, rect.topleft)
        else:
            rect = self.current_image.get_rect(center=position)
            screen.blit(self.current_image, rect.topleft)

    def change_images(self, image1_pygame_surface, image2_pygame_surface):
        # No change if it's already the same
        if not self._surfaces_are_equal(self.image1, image1_pygame_surface) or not self._surfaces_are_equal(self.image2, image2_pygame_surface):
            self.image1 = image1_pygame_surface
            self.image2 = image2_pygame_surface
            self.current_image = self.image1
            self.scale_width = 1
            self.scale_height = 1

    def set_flip_interval(self, flip_interval):
        self.flip_interval = flip_interval

    def set_flip_duration(self, flip_duration):
        self.flip_duration = flip_duration

    def _surfaces_are_equal(self, surface1, surface2):
        if surface1.get_size() != surface2.get_size():
            return False
        bytes1 = pygame.image.tostring(surface1, 'RGB')
        bytes2 = pygame.image.tostring(surface2, 'RGB')
        return bytes1 == bytes2
        
    @staticmethod
    def ease_in_out_cosine(t):
        return abs(math.cos(math.pi * t))

    @staticmethod
    def ease_in_out_sine(t):
        return abs(math.sin(math.pi * t))

