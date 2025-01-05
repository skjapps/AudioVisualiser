import math
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def ease_in_out_cosine(t):
    """Eases value from 0 to 1 using cosine interpolation.

    At t=0, returns 0. At t=1, returns 1. At t=0.5, returns 0.5.
    """
    return abs(math.cos(math.pi * t))

def ease_in_out_sine(t):
    """Eases value from 0 to 1 using sine interpolation.

    At t=0, returns 0. At t=1, returns 1. At t=0.5, returns 1.
    """
    return abs(math.sin(math.pi * t))

def sine_2_t(t):
    """Eases value from 0 to 1 using sine interpolation of 2 cycles.

    At t=0, returns 0. At t=1, returns 0. At t=0.25, returns 1.
    At t=0.75, returns -1.
    """
    return math.sin(math.pi * 2 * t)

def cosine_2_t(t):
    """Eases value from 0 to 1 using cosine interpolation of 2 cycles.

    At t=0, returns 1. At t=1, returns 1. At t=0.25, returns 0.
    At t=0.75, returns 0.
    """
    return math.cos(math.pi * 2 * t)
    
