import numpy as np

class Ray:
    def __init__(self, pos ,angle, microns=0.6):
        self.pos = pos
        self.angle = angle
        self.microns = microns
        self.start = 0
        self.end = 100000
        self._dx = np.cos(self.angle)
        self._dy = np.sin(self.angle)

    def Equation(self, t):
        return [self._dx*t + self.pos[0], self._dy*t + self.pos[1]]

    # Sets the last value of t of the ray
    def SetEnd(self, end):
        self.end = end

    # Sets the last value of t of the ray
    def SetStart(self, start):
        self.start = start

    @property
    def dx(self):
        return self._dx

    @property
    def dy(self):
        return self._dy