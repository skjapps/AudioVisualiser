import pygame

class ImageFlipper:
    def __init__(self, image1_path, image2_path, flip_interval):
        self.image1 = pygame.image.load(image1_path)
        self.image2 = pygame.image.load(image2_path)
        self.flip_interval = flip_interval
        self.last_flip_time = pygame.time.get_ticks()
        self.current_image = self.image1

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_flip_time >= self.flip_interval:
            self.current_image = self.image2 if self.current_image == self.image1 else self.image1
            self.last_flip_time = current_time

    def draw(self, screen, position):
        screen.blit(self.current_image, position)
