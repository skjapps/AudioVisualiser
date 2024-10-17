import pygame
import math

def ease_in_out(t):
    return t * t * (3 - 2 * t)

class ImageFlipper:
    def __init__(self, image1_pygame_surface, image2_pygame_surface, flip_interval, flip_duration):
        self.image1 = image1_pygame_surface
        self.image2 = image2_pygame_surface
        self.flip_interval = flip_interval
        self.flip_duration = flip_duration
        self.last_flip_time = pygame.time.get_ticks()
        self.current_image = self.image1
        self.flipping = False
        self.scale = 1
        self.image_switched = False

    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.last_flip_time

        if self.flipping:
            t = elapsed_time / self.flip_duration
            if t >= 1:
                self.flipping = False
                self.last_flip_time = current_time
                self.scale = 1
                self.image_switched = False
            else:
                if t >= 0.5 and not self.image_switched:
                    self.current_image = self.image2 if self.current_image == self.image1 else self.image1
                    self.image_switched = True
                eased_t = ease_in_out(t)
                self.scale = 1 - 2 * abs(eased_t - 0.5)

        elif elapsed_time >= self.flip_interval:
            self.flipping = True
            self.last_flip_time = current_time

    def change_images(self, image1_pygame_surface, image2_pygame_surface):
        self.image1 = image1_pygame_surface
        self.image2 = image2_pygame_surface
        self.current_image = self.image1
        self.last_flip_time = pygame.time.get_ticks()
        self.scale = 1
        self.flipping = False
        self.image_switched = False

    def set_flip_interval(self, flip_interval):
        self.flip_interval = flip_interval

    def set_flip_duration(self, flip_duration):
        self.flip_duration = flip_duration

    def draw(self, screen, position):
        if self.flipping:
            scaled_width = int(self.current_image.get_width() * self.scale)
            scaled_image = pygame.transform.scale(self.current_image, (scaled_width, self.current_image.get_height()))
            rect = scaled_image.get_rect(center=position)
            screen.blit(scaled_image, rect.topleft)
        else:
            screen.blit(self.current_image, position)
