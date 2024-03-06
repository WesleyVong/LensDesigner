import lens
import numpy as np
import json

# Generates Lens Assembly
class LensAssembly(object):
    # Pass in position of assembly and catalog of lenses
    def __init__(self, pos,  catalog,sensorOffset = 50, sensorHeight=40):
        self._pos = pos
        self._catalog = catalog
        self._lenses = []
        self._offsets = []
        self._sensorHeight = 40
        self._sensorOffset = 20

    def __str__(self):
        ret = ""
        for idx in range(len(self._lenses)):
            l = self._lenses[idx]
            ret = ret + ("Lens {}: offset: {}, type: {}, focallength: {}, material: {}\n"
                         "\t Description: {}\n").format(idx, self._offsets[idx], l.config.get("type"), l.config.get("focalLength"), l.config.get("material"), l.config.get("description"))
        return ret

    def AddLens(self, lensConfig, offset=0,dir="left"):
        if type(lensConfig) == str:
            self._lenses.append(lens.Lens(self._pos, dir, self._catalog[lensConfig]))
        elif type(lensConfig) == dict:
            self._lenses.append(lens.Lens(self._pos, dir, lensConfig))
        else:
            raise Exception("lens has unexpected value {}".format(type(lensConfig)))
        self._offsets.append(offset)
        self.CalculateLensPosition()

    def SetOffset(self, idx, offset):
        self._offsets[idx] = offset
        self.CalculateLensPosition()

    def CalculateLensPosition(self):
        numLenses = len(self._lenses)
        if numLenses <= 0:
            return
        prevX = self._pos[0]
        prevThickness = 0
        for i in range(numLenses):
            lensX = prevX + self._offsets[i] + prevThickness
            prevX = lensX
            prevThickness = self._lenses[i].config["thickness"]
            self._lenses[i].pos = [prevX, self._pos[1]]

    def SensorEquation(self, t):
        lastLens = self._lenses[-1]
        return [lastLens.pos[0] + lastLens.config["thickness"] + self._sensorOffset,t]

    @property
    def lenses(self):
        return self._lenses

    @property
    def sensorHeight(self):
        return self._sensorHeight