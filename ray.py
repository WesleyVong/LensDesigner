import numpy as np
from surface import Surface


class Ray(Surface):
    def __init__(self, pos, ang, mag=1, wavelengths=[]):
        self._pos = pos
        self._dx = np.cos(ang) * mag
        self._dy = np.sin(ang) * mag
        self._wavelengths = wavelengths

    def equation(self, t, n=0):
        t = t - np.floor(t)
        pos_x = self._pos[0] + t * self._dx
        pos_y = self._pos[1] + t * self._dy
        return [pos_x, pos_y]

    @property
    def num_equations(self):
        return 1
