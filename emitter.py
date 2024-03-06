import ray
import numpy as np

class Emitter:
    # Takes position, number of rays,
    def __init__(self, pos, rayNum, dir = 0, size=1, arc=np.pi/2, microns=0.6, type="point"):
        self.pos = pos
        self.dir = dir
        self.size = size
        self.arc = arc
        self._rayNum = rayNum
        self.type = type
        self._microns = microns

        if type == "point":
            self.rays = self.GenPointRays()
        if type == "plane":
            self.rays = self.GenPlaneRays()
        if type == "arc":
            self.rays = self.GenArcRays()



    def GenPointRays(self):
        rays = []
        angles = np.linspace(-np.pi, np.pi - (2 * np.pi / self._rayNum), self._rayNum)
        for angle in angles:
            newRay = ray.Ray(self.pos, angle, microns=self._microns)
            rays.append(newRay)
        return rays

    def GenPlaneRays(self):
        rays = []
        # Get direction of Ray
        xydir = np.array([np.cos(self.dir), np.sin(self.dir)])

        # Calculate normal of direction
        xystep = np.random.rand(2)
        xystep = xystep - xystep.dot(xydir) * xydir
        xystep = xystep / np.linalg.norm(xystep)
        xstep = xystep[0] * self.size /2
        ystep = xystep[1] * self.size /2

        coords = np.linspace([self.pos[0]-xstep,self.pos[1]-ystep],[self.pos[0]+xstep,self.pos[1]+ystep],self._rayNum)
        for coord in coords:
            newRay = ray.Ray(coord, self.dir, microns=self._microns)
            rays.append(newRay)
        return rays

    def GenArcRays(self):
        rays = []
        angles = np.linspace(self.dir - (self.arc/2), self.dir + (self.arc/2), self._rayNum)
        for angle in angles:
            newRay = ray.Ray(self.pos, angle, microns=self._microns)
            rays.append(newRay)
        return rays

    @property
    def raynum(self):
        return self._rayNum

    @property
    def microns(self):
        return self._microns