from abc import ABC, abstractmethod, abstractproperty
import math
from material import Material


class Surface(ABC):
    @abstractmethod
    # Returns [x,y] values for an equation given
    # t_norm determines whether t is normalized to 0<=t<=1
    def equation(self, t, n=0):
        pass

    @abstractmethod
    # Returns tangent vector for equation
    def tangent(self, t, n=0):
        pass

    @abstractmethod
    # Returns normal vector for equation
    def normal(self, t, n=0):
        pass

    @property
    @abstractmethod
    def num_equations(self):
        pass

    @property
    def material(self):
        return None

    @property
    def pos(self):
        pass

    def normalize(self, x, y):
        mag = math.sqrt(x ** 2 + y ** 2)
        if mag == 0:
            return [0, 0]
        return [x / mag, y / mag]


# class Polygon(Surface):
#     def __init__(self, pos, vertices, mat: Material = None):
#         self._pos = pos
#         self._vertices = []
#         for vert in vertices:
#             self._vertices.append([vert[0] + pos[0], vert[1] + pos[1]])
#         self._vertexNum = len(self._vertices)
#         self._edgeNum = self._vertexNum
#         self._material = mat
#
#         # Edge format: dx, dy
#         self._edges = []
#         tmp_verts = self._vertices
#         tmp_verts.append(self._vertices[0])
#         for i in range(self._edgeNum):
#             vert0 = tmp_verts[i]
#             vert1 = tmp_verts[i + 1]
#             dx = vert1[0] - vert0[0]
#             dy = vert1[1] - vert0[1]
#             self._edges.append([dx, dy])
#
#     def equation(self, t, n=0):
#         t = t - math.floor(t)  # Wrap the t value between 0 and 1
#         edge = self._edges[n]  # Find which edge we are on
#         pos = self._vertices[n]  # Find the position of the starting vertex
#         dx = t * edge[0]  # Calculate Offset for dx and dy
#         dy = t * edge[1]
#         return [pos[0] + dx, pos[1] + dy]
#
#     def tangent(self, t, n=0):
#         edge = self._edges[n]
#         return self.normalize(edge[0], edge[1])
#
#     @property
#     def num_equations(self):
#         return self._edgeNum

    @property
    def material(self):
        return self._material
