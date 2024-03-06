import numpy as np
import ior
import json

class Lens(object):
    def __init__(self, pos=[0,0], dir="left", config={}):
        self._pos = pos
        self._dir = dir
        self._library = {}
        self._config = config
        if self._config != {}:
         self.PreCalculate()

    def Configure(self, diameter, radius,thickness, conic=0, coeff=[], radius2=0, conic2=0, coeff2=[], material="BK7", type="biconvex", focalLength=0):
        self._config["alias"] = "None"
        self._config["diameter"] = diameter
        self._config["radius"] = radius
        self._config["conic"] = conic
        self._config["coeff"] = coeff
        self._config["radius2"] = radius2
        self._config["conic2"] = conic2
        self._config["coeff2"] = coeff2
        self._config["thickness"] = thickness
        self._config["material"] = material
        self._config["focalLength"] = focalLength
        self.PreCalculate()

    # Precalculates commonly used values
    def PreCalculate(self):
        self._start = -int(self._config["diameter"]/2)
        self._end = int(self._config["diameter"] / 2)

        # Front Surface
        type = self._config["type"]
        self._r = self._config["radius"]
        self._k = self._config["conic"]
        self._c = np.asarray(self._config["coeff"])

        if type == "biconvex" or type == "planoconvex":
            pass
        if type == "biconcave" or type == "planoconcave":
            self._r = -self._r
            self._c = -self._c

        # Back Surface
        self._r2 = self._config.get("radius2")
        self._k2 = self._config.get("conic2")
        self._c2 = np.asarray(self._config.get("coeff2"))
        if self._r2 == None or self._k2 == None:
            self._r2 = self._config["radius"]
            self._k2 = self._config["conic"]
            self._c2 = np.asarray(self._config["coeff"])

        if type == "planoconvex" or type == "planoconcave":
            self._r2 = 0
            self._c2 = np.array([])
        if type == "biconvex":
            self._r2 = -self._r2
            self._c2 = -self._c2
        if type == "biconcave":
            pass

        if self._dir == "left":
            pass
        if self._dir == "right":
            tmpr = self._r
            tmpc = self._c
            self._r = -self._r2
            self._c = -self._c2
            self._r2 = -tmpr
            self._c2 = -tmpc

        if self._k >= 1:
            self._max = np.inf
        else:
            self._max = np.sqrt(self._r ** 2 / (1 + self._k)) - 0.001

        if self._k2 >= 1:
            self._max2 = np.inf
        else:
            self._max2 = np.sqrt(self._r2**2/(1+self._k2)) - 0.001

    def FrontEquation(self, t):
        res = self.Surface(t, self._r, self._k, self._c, self._max)
        return [res[0]+self._pos[0], res[1]+self._pos[1]]

    def BackEquation(self, t):
        res = self.Surface(t, self._r2, self._k2, self._c2, self._max2)
        return [res[0]+self._pos[0]+self._config["thickness"], res[1]+self._pos[1]]

    def Surface(self, t, r,k,c, max):
        y = t
        x = 0
        if t >= max:
            t = max
        if t <= -max:
            t = -max

        if r == 0:
            return [x, y]
        sphr = t ** 2 / (r * (1 + np.sqrt(1 - (1 + k) * (t ** 2) / (r ** 2))))
        poly = 0
        for idx in range(len(c)):
            poly = poly + c[idx] * t ** ((idx + 2) * 2)
        x = (poly + sphr)

        return [x,y]

    def GetIOR(self, microns):
        return  ior.GetIOR(microns, self._config["material"])

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, conf):
        self._config = conf

    @property
    def start(self):
        return self._start
    @property
    def end(self):
        return self._end