from abc import ABC, abstractmethod
import numpy as np

class Surface(ABC):
    @abstractmethod
    def equation(self, t):
        pass

class Polygon(Surface):
    def __init__(self, pos, vertices):
        self._pos = pos
        self._vertices = []
        for vert in vertices:
            self._vertices.append([vert[0] + pos[0], vert[1] + pos[1]])
        self._vertexNum = len(self._vertices)
        self._edgeNum = self._vertexNum

        # Edge format: dx, dy
        self._edges = []
        tmpVerts = self._vertices
        tmpVerts.append(self._vertices[0])
        for i in range(self._edgeNum):
            vert0 = tmpVerts[i]
            vert1 = tmpVerts[i+1]
            dx = vert1[0] - vert0[0]
            dy = vert1[1] - vert0[1]
            self._edges.append([dx, dy])

    def equation(self, t):
        if t < 0:
            return self._vertices[0]
        if t >= 1:
            return self._vertices[-1]
        t_scaled = t / (1 / self._edgeNum)
        edge = self._edges[int(np.floor(t_scaled))]
        progress = t_scaled - np.floor(t_scaled)
        pos = self._vertices[int(np.floor(t_scaled))]
        dx = progress * edge[0]
        dy = progress * edge[1]
        return [pos[0]+dx, pos[1]+dy]
