import pygame
import random
import math

class DotField():
    def __init__(self, dot_count, dot_size_range, speed_factor, direction="right", dot_color=(0, 0, 0), opacity=255, dot_field_width=800, dot_field_height=480):
        self.width = int(dot_field_width)  # Width of the dot field display
        self.height = int(dot_field_height)  # Height of the dot field display
        self.dot_count = dot_count
        self.dot_size_range = dot_size_range
        self.speed_factor = speed_factor
        self.direction = direction
        self.dot_color = dot_color
        self.opacity = opacity

        # Create dot field surface
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.set_alpha(self.opacity)  # Set the opacity of the surface

        # Initialize dots with random positions and sizes
        self.dots = []
        self._generate_dots()

    def update(self, bass_reading):
        # Clear the dot field surface
        self.surface.fill((255, 255, 255))
        self.surface.set_colorkey((255, 255, 255))

        # Update and render dots
        for dot in self.dots:
            x, y, size, speed, phase = dot
            speed = self.speed_factor * bass_reading  # Adjust speed based on bass reading

            if self.direction == "right":
                x += speed
                if x > self.width:
                    x = 0
                    y = random.randint(0, self.height)
                    # Min size 1
                    size = max(random.uniform(self.dot_size_range[0], self.dot_size_range[1]), 1)
                    speed = random.uniform(1, self.speed_factor) * ((size / self.dot_size_range[1]) * 200)
                    phase = random.uniform(0, 2 * math.pi)
            elif self.direction == "left":
                x -= speed
                if x < 0:
                    x = self.width
                    y = random.randint(0, self.height)
                    # Min size 1
                    size = max(random.uniform(self.dot_size_range[0], self.dot_size_range[1]), 1)
                    speed = random.uniform(0.5, self.speed_factor) * ((size / self.dot_size_range[1]) * 200)
                    phase = random.uniform(0, 2 * math.pi)

            # Apply sine wave motion to the y-coordinate
            y += int(math.sin(x / 20 + phase) * 10)

            pygame.draw.circle(self.surface, self.dot_color, (int(x), int(y)), size)
            dot[0] = x

    def _generate_dots(self):
        # Initialize dots with random positions and sizes
        self.dots = []
        for _ in range(self.dot_count):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            # Min size 1
            size = max(random.uniform(self.dot_size_range[0], self.dot_size_range[1]), 1)
            speed = random.uniform(1, self.speed_factor) * ((size / self.dot_size_range[1]) * 200)
            phase = random.uniform(0, 2 * math.pi)  # Random phase for sine wave motion
            self.dots.append([x, y, size, speed, phase])

    def resize_surface(self, width, height, opacity=None):
        ratio = width / self.width
        self.width = int(width)  # Width of the dot field display
        self.height = int(height)  # Height of the dot field display

        # Resize the surface to the new size
        self.surface = pygame.transform.scale(self.surface, (width, height))

        # Set the opacity of the resized surface
        if opacity is not None:
            self.opacity = opacity
        self.surface.set_alpha(self.opacity)

        # Resize Dots
        self.dot_size_range = (self.dot_size_range[0] * ratio,
                               self.dot_size_range[1] * ratio)
        # Change dot count for density
        self.dot_count = int(self.dot_count * ratio)

        # Re-generate dots
        self._generate_dots()
