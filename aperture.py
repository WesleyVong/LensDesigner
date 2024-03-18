import math

import surface
from surface import Surface
from material import Material


class Aperture(Surface):
    def __init__(self, pos, outer_diameter, inner_diameter, thickness=1):
        self._pos = pos
        self._outer_diameter = outer_diameter
        self._inner_diameter = inner_diameter
        self._outer_radius = outer_diameter/2
        self._inner_radius = inner_diameter/2
        self._thickness = thickness
        self._dy = (outer_diameter - inner_diameter)/2
        self._start_t = 0
        mat = Material()
        mat.load_values("Wall", "air", [], [], 0, 100, 0)
        self._material = mat

    def equation(self, t, n=0):
        t = t - math.floor(t)
        if n == 0:
            pos_x = self._pos[0]
            pos_y = self._pos[1] + self._inner_radius + (t * 2 * self._dy)
        elif n == 1:
            pos_x = self._pos[0]
            pos_y = self._pos[1] - self._inner_radius - (t * 2 * self._dy)
        elif n == 2:
            pos_x = self._pos[0] + self._thickness
            pos_y = self._pos[1] + self._inner_radius + (t * 2 * self._dy)
        else:
            pos_x = self._pos[0] + self._thickness
            pos_y = self._pos[1] - self._inner_radius - (t * 2 * self._dy)
        return [pos_x, pos_y]

    def tangent(self, t, n=0):
        return [0, 1]

    def normal(self, t, n=0):
        return [1, 0]

    @property
    def num_equations(self):
        return 4

    @property
    def material(self):
        return self._material

    @property
    def thickness(self):
        return self._thickness

    @property
    def pos(self):
        return self._pos