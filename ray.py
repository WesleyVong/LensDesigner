import math
import numpy as np
from surface import Surface
from material import Material


class Ray(Surface):
    def __init__(self, pos, ang, mag=1, wavelengths=[]):
        self._pos = pos
        self._ang = ang
        self._dx = math.cos(ang)
        self._dy = math.sin(ang)
        self._wavelengths = wavelengths
        self._start_t = 0
        self._end_t = mag

        self._tangent = [math.cos(ang), math.sin(ang)]

    def __str__(self):
        return 'Type: Ray, Position: {}, Angle: {}, Wavelengths: {}'.format(self._pos, self._ang, self._wavelengths)

    def equation(self, t, n=0):
        # t = t - np.floor(t)
        pos_x = self._pos[0] + t * self._dx
        pos_y = self._pos[1] + t * self._dy
        return [pos_x, pos_y]

    def tangent(self, t, n=0):
        return self._tangent

    def normal(self, t, n=0):
        if self._tangent[0] < 0:
            return [self._tangent[1], -self._tangent[0]]
        else:
            return [-self._tangent[1], self._tangent[0]]

    @property
    def num_equations(self):
        return 1

    @property
    def wavelengths(self):
        return self._wavelengths

    @property
    def pos(self):
        return self._pos

    @property
    def dx(self):
        return self._dx

    @property
    def dy(self):
        return self._dy

    @property
    def angle(self):
        return self._ang

    @property
    def end_t(self):
        return self._end_t

    @end_t.setter
    def end_t(self, end_t):
        self._end_t = end_t


class Emitter():
    def __init__(self, pos, num_rays, emit_type, wavelengths, angle=0, magnitude=100, size=1):
        self._pos = pos
        self._num_rays = num_rays
        self._emit_type = emit_type
        self._angle = angle
        self._magnitude = magnitude
        self._size = size
        self._rays = []
        self._wavelengths = wavelengths

        if emit_type == 'plane':            # Standard plane with rays following an angle
            self.generate_plane()
        if emit_type == 'directed':    # Plane with rays directed towards pos with given angle
            self.generate_directed()
        if emit_type == 'point':        # Point source with clamped arc
            self.generate_point()

    def generate_plane(self):
        dx = math.cos(self._angle + math.pi/2) * self._size/2
        dy = math.sin(self._angle + math.pi/2) * self._size/2
        x = self._pos[0]
        y = self._pos[1]
        ray_pos = np.linspace([x - dx, y - dy], [x + dx, y + dy], self._num_rays)
        for pos in ray_pos:
            self._rays.append(Ray(pos, self._angle, self._magnitude, self._wavelengths))

    def generate_directed(self):
        dx = math.cos(self._angle + math.pi/2) * self._size/2
        dy = math.sin(self._angle + math.pi/2) * self._size/2
        x = self._pos[0] - math.cos(self._angle) * self._magnitude/2
        y = self._pos[1] - math.sin(self._angle) * self._magnitude/2
        ray_pos = np.linspace([x - dx, y - dy], [x + dx, y + dy], self._num_rays)
        for pos in ray_pos:
            self._rays.append(Ray(pos, self._angle, self._magnitude, self._wavelengths))

    def generate_point(self):
        x = self._pos[0] - math.cos(self._angle) * self._magnitude/2
        y = self._pos[1] - math.sin(self._angle) * self._magnitude/2
        ang_min = self._angle - self._size/2
        ang_max = self._angle + self._size/2
        pos = [x, y]
        ray_angle = np.linspace(ang_min, ang_max, self._num_rays)
        for ang in ray_angle:
            self._rays.append(Ray(pos, ang, self._magnitude, self._wavelengths))

    @property
    def rays(self):
        return self._rays

    @property
    def num_rays(self):
        return self._num_rays

    @property
    def wavelengths(self):
        return self._wavelengths
