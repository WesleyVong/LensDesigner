from abc import ABC, abstractmethod, abstractproperty
import numpy as np
from material import Material

class Surface(ABC):
    def __init__(self, pos, mat: Material = None):
        self._pos = pos
        self._material = mat
    @abstractmethod
    # Returns [x,y] values for an equation given [0<=t<=1]
    # If t < 0 or t > 1, it loops around
    def equation(self, t):
        pass

    @property
    def material(self):
        return self._material
    @material.setter
    def material(self, material):
        self._material = material

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def material(self, pos):
        self._pos = pos


class Polygon(Surface):
    def __init__(self, pos, vertices, mat: Material = None):
        self._pos = pos
        self._vertices = []
        for vert in vertices:
            self._vertices.append([vert[0] + pos[0], vert[1] + pos[1]])
        self._vertexNum = len(self._vertices)
        self._edgeNum = self._vertexNum
        self._material = mat

        # Edge format: dx, dy
        self._edges = []
        tmp_verts = self._vertices
        tmp_verts.append(self._vertices[0])
        for i in range(self._edgeNum):
            vert0 = tmp_verts[i]
            vert1 = tmp_verts[i+1]
            dx = vert1[0] - vert0[0]
            dy = vert1[1] - vert0[1]
            self._edges.append([dx, dy])

    def equation(self, t):
        t = t - np.floor(t)
        t_scaled = t / (1 / self._edgeNum)
        edge = self._edges[int(np.floor(t_scaled))]
        progress = t_scaled - np.floor(t_scaled)
        pos = self._vertices[int(np.floor(t_scaled))]
        dx = progress * edge[0]
        dy = progress * edge[1]
        return [pos[0]+dx, pos[1]+dy]

class Ray(Surface):
    def __init__(self, pos, ang, mag=1, mat: Material = None):
        self._pos = pos
        self._dx = np.cos(ang) * mag
        self._dy = np.sin(ang) * mag
        self._material = mat

    def equation(self, t):
        pos_x = self._pos[0] + t * self._dx
        pos_y = self._pos[1] + t * self._dy
        return [pos_x, pos_y]
