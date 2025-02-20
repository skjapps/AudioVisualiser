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
        for i in range(self.dot_count):
            self.dots.append(self._generate_dot())

    def update(self, bass_reading, dot_count, dots_speed_factor):
        # Clear the dot field surface
        self.surface.fill((255, 255, 255))
        self.surface.set_colorkey((255, 255, 255))

        # Update dot count
        self._update_dot_count(dot_count)
        self._update_dots_speed(dots_speed_factor)

        # Update and render dots
        if dot_count > 0:
            for dot in self.dots:
                x, y, size, speed, phase = dot
                # dot[3] is dot's original speed
                speed = dot[3] * self.speed_factor * bass_reading  # Adjust speed based on bass reading

                # Update X pos
                if self.direction == "right":
                    x += speed
                    if x > self.width:
                        x = 0
                elif self.direction == "left":
                    x -= speed
                    if x < 0:
                        x = self.width

                # Apply sine wave motion to the y-coordinate
                y += int(math.sin(x / 20 + phase) * 10)
                
                # Render
                pygame.draw.circle(self.surface, self.dot_color, (int(x), int(y)), size)

                # Store new xpos
                dot[0] = x

    def _generate_dot(self):
        x = random.randint(0, self.width)
        y = random.randint(0, self.height)
        # Min size 1
        size = max(random.uniform(self.dot_size_range[0], self.dot_size_range[1]), 1)
        speed = random.uniform(1, self.speed_factor) * (size / self.dot_size_range[1])
        phase = random.uniform(0, 2 * math.pi)  # Random phase for sine wave motion

        return [x, y, size, speed, phase]
    
    def _update_dot_count(self, dot_count):        
        # Adding Dots
        if dot_count > self.dot_count:
            self.dots.extend(self._generate_dot() for _ in range(dot_count - self.dot_count))
        
        # Removing Dots
        elif dot_count < self.dot_count:
            self.dots = self.dots[:dot_count]
        
        # Update dot count
        self.dot_count = dot_count

    def _update_dots_speed(self, dots_speed_factor):
        # Update all dots speed if changed  
        if self.speed_factor != dots_speed_factor:
            for dot in self.dots:
                dot[3] = random.uniform(1, self.speed_factor) * (dot[2] / self.dot_size_range[1])

            self.speed_factor = dots_speed_factor

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
        self.dots = []
        for i in range(self.dot_count):
            self.dots.append(self._generate_dot())
