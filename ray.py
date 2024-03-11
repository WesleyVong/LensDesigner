import math
from surface import Surface
from material import Material


class Ray(Surface):
    def __init__(self, pos, ang, mag=1, wavelengths=[], hits=0):
        self._pos = pos
        self._ang = ang
        self._dx = math.cos(ang)
        self._dy = math.sin(ang)
        self._wavelengths = wavelengths
        self._hits = hits
        self._start_t = 0
        self._end_t = mag

        self._tangent = [math.cos(ang), math.sin(ang)]

    def equation(self, t, n=0):
        # t = t - np.floor(t)
        pos_x = self._pos[0] + t * self._dx
        pos_y = self._pos[1] + t * self._dy
        return [pos_x, pos_y]

    def tangent(self, t, n=0):
        return self._tangent

    @property
    def num_equations(self):
        return 1

    @property
    def wavelengths(self):
        return self._wavelengths

    @property
    def hits(self):
        return self._hits

    @hits.setter
    def hits(self, hits):
        self._hits = hits

    @property
    def end_t(self):
        return self._end_t

    @end_t.setter
    def end_t(self, end_t):
        self._end_t = end_t
