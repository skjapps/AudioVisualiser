import pygame
from OpenGL.GL import *
import numpy as np

class OpenGLConverter():
    
    # Go from pygame surface to a GL texture.
    @staticmethod
    def surfaceToTexture(pygame_surface, texId):
        width, height = pygame_surface.get_size()
        surface_array = pygame.surfarray.pixels3d(pygame_surface)
        rgb_surface = surface_array.swapaxes(0, 1).astype(np.uint8).tobytes()

        glBindTexture(GL_TEXTURE_2D, texId)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, rgb_surface)
        glBindTexture(GL_TEXTURE_2D, 0)

    def setupOpenGL(view_width, view_height):
        # OpenGL setup.
        glViewport(0, 0, view_width, view_height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, view_width, view_height, 0, -1, 1)  # Top-left origin
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        #glClearColor(0.0, 0.0, 0.0, 0.0)
        glDisable(GL_DEPTH_TEST) # Not 3d
        glDisable(GL_LIGHTING) # Not required for this demo
        #glEnable(GL_BLEND)
        #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Setup GL texture.
        texId = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texId)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, view_width, view_height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)

        glEnable(GL_TEXTURE_2D)

        return texId
    
    def drawOpenGL(texId, w, h):
        glBindTexture(GL_TEXTURE_2D, texId)

        # Draw a textured quad equivalent to the pygame surface.
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(0, 0)                            # Top-left corner.
        glTexCoord2f(1, 0); glVertex2f(w, 0)               # Top-right corner.
        glTexCoord2f(1, 1); glVertex2f(w, h)  # Bottom-right corner.
        glTexCoord2f(0, 1); glVertex2f(0, h)               # Bottom-left corner.
        glEnd()

        glBindTexture(GL_TEXTURE_2D, 0)
