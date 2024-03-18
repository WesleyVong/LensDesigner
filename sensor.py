import math
from surface import Surface
from material import Material


class Sensor(Surface):
    def __init__(self, pos, size):
        self._pos = pos
        self._size = size
        self._dy = size
        mat = Material()
        mat.load_values("Wall", "air", [], [], 0, 100, 0)
        self._material = mat

    def equation(self, t, n=0):
        t = t - math.floor(t)
        pos_x = self._pos[0]
        pos_y = self._pos[1] + (t-0.5) * self._dy
        return [pos_x, pos_y]

    def tangent(self, t, n=0):
        return [0, 1]

    def normal(self, t, n=0):
        return [1, 0]

    @property
    def num_equations(self):
        return 1

    @property
    def material(self):
        return self._material

    @property
    def thickness(self):
        return 0.1

    @property
    def pos(self):
        return self._pos
