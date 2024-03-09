import numpy as np
from surface import Surface
from material import Material, MaterialLibrary
import json

# EPSILON = np.finfo(np.float32).eps
EPSILON = 1e-5


def aspheric_lens_equation(t, r, k=0, a=[]):
    conic = t ** 2 / (r * (1 + np.sqrt(1 - (1 + k) * (t ** 2) / (r ** 2))))
    poly = 0
    for idx in range(len(a)):
        poly = poly + a[idx] * t ** ((idx + 2) * 2)
    return poly + conic


class Lens(Surface):
    def __init__(self, pos, library: MaterialLibrary, dir='left'):
        self._library = library
        self._pos = pos
        self._dir = dir
        self._material = Material()
        self._material_name = ""
        self._diameter = 0
        self._radius = self._diameter / 2
        self._thickness = 0
        self._r0 = np.inf
        self._k0 = 0
        self._a0 = np.asarray([0])
        self._r1 = np.inf
        self._k1 = 0
        self._a1 = []
        self._type = None
        self._bound0 = 0
        self._bound1 = 0
        self._edge_thickness = 0

    def load_values(self, diameter, thickness, r0, material, k0=0, a0=[], r1=np.inf, k1=0, a1=[], type=None):
        self._diameter = diameter
        self._radius = self._diameter / 2
        self._thickness = thickness
        self._r0 = r0
        if self._r0 == 0:
            self._r0 = np.inf
        self._k0 = k0
        self._a0 = np.asarray(a0)
        self._r1 = r1
        if self._r1 == 0:
            self._r1 = np.inf
        self._k1 = k1
        self._a1 = a1
        self._type = type
        self._material_name = material

        self.setup()

    def load_from_dict(self, d: dict):
        self._diameter = d.get('diameter', 0)
        self._radius = self._diameter / 2
        self._thickness = d.get('thickness', 0)
        self._r0 = d.get('r0', np.inf)
        if self._r0 == 0:
            self._r0 = np.inf
        self._k0 = d.get('k0', 0)
        self._a0 = np.asarray(d.get('a0', []))
        self._r1 = d.get('r1', np.inf)
        if self._r1 == 0:
            self._r1 = np.inf
        self._k1 = d.get('k1', 0)
        self._a1 = np.asarray(d.get('a1', []))
        self._type = d.get('type', None)
        self._material_name = d.get('material', '')

        self.setup()

    def setup(self):
        # Front Surface
        lens_type = self._type

        if lens_type is not None:
            if lens_type == "biconvex" or lens_type == "planoconvex":
                pass
            if lens_type == "biconcave" or lens_type == "planoconcave":
                self._r0 = -self._r0
                self._a0 = -self._a0

            # Back Surface
            if np.isinf(self._r1):
                self._r1 = -self._r0
                self._k1 = self._k0
                self._a1 = -np.array(self._a0)

            if type == "planoconvex" or type == "planoconcave":
                self._r1 = np.inf
            if type == "biconvex":
                self._r1 = -self._r1
                self._a1 = -self._a1
            if type == "biconcave":
                pass

        if self._dir == "left":
            pass
        if self._dir == "right":
            tmpr = self._r0
            tmpa = self._a0
            self._r0 = -self._r1
            self._a0 = -self._a1
            self._r1 = -tmpr
            self._a1 = -tmpa

        self.calculate_bounds()
        self._material = self._library.get(self._material_name)

    def calculate_bounds(self):
        if self._k0 > -1:
            if self._radius >= np.sqrt(self._r0 ** 2 / (1 + self._k0)) - EPSILON:
                raise Exception("Lens radius is beyond lens equation")
        bound_x0 = aspheric_lens_equation(self._radius, self._r0, self._k0, self._a0)

        if self._k0 > -1:
            if self._radius >= np.sqrt(self._r1 ** 2 / (1 + self._k1)) - EPSILON:
                raise Exception("Lens radius is beyond lens equation")
        bound_x1 = aspheric_lens_equation(self._radius, self._r1, self._k1, self._a1)

        self._bound0 = bound_x0
        self._bound1 = bound_x1

        edge0 = bound_x0
        edge1 = self._thickness + bound_x1

        self._edge_thickness = np.abs(edge1 - edge0)

    def equation(self, t, n=0):
        t = t - np.floor(t)
        if n == 0:    # Surface 1
            t_scaled = (t - 0.5) * 2
            t_scaled = t_scaled * self._radius
            x = aspheric_lens_equation(t_scaled, self._r0, self._k0, self._a0)
            return [self._pos[0] + x, self._pos[1] + t_scaled]
        elif n == 1:  # Top Connecting Line
            t_scaled = t * self._edge_thickness
            x = self._pos[0] + self._bound0 + t_scaled
            return [x, self._pos[1] + self._radius]
        elif n == 2:  # Surface 2
            t_scaled = (t - 0.5) * 2
            t_scaled = t_scaled * self._radius
            x = aspheric_lens_equation(t_scaled, self._r1, self._k1, self._a1)
            return [self._pos[0] + self._thickness + x, self._pos[1] - t_scaled]
        else:   # Bottom Connecting Line
            t_scaled = t * self._edge_thickness
            x = self._pos[0] + self._thickness + self._bound1 - t_scaled
            return [x, self._pos[1] - self._radius]

    def tangent(self, t, n=0):
        pos0 = self.equation(t+EPSILON, n)
        pos1 = self.equation(t-EPSILON, n)
        dx = pos1[0] - pos0[0]
        dy = pos1[1] - pos0[1]
        return self.normalize(dx, dy)


    @property
    def material(self):
        return self._material

    @property
    def num_equations(self):
        return 4
