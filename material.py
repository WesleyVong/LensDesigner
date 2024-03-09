import numpy as np
import warnings
import json


class MaterialLibrary:
    def __init__(self, f: str):
        with open(f) as json_file:
            materials = json.load(json_file)
        material_names = list(materials)
        self._library = {}
        for name in material_names:
            mat = Material()
            mat.load_from_dict(materials.get(name))
            self._library[name] = mat

    def get(self, name):
        return self._library.get(name)

class Material:
    def __init__(self):
        # Material Name
        self._name = None
        # Dispersion Formula Type:
        #   air, sellmeier
        self._formula = None
        # B and C coefficients for Sellmeier equation
        self._b = []
        self._c = []
        # Maximum and Minimum defined wavelength (um)
        self._minMicrons = 0
        self._maxMicrons = 0

    def load_values(self, name: str, formula: str, b, c, min_microns: float, max_microns: float):
        self._name = name
        self._formula = formula
        self._b = b
        self._c = c
        self._minMicrons = min_microns
        self._maxMicrons = max_microns

    def load_from_dict(self, d: dict):
        self._name = d.get('name', None)
        self._formula = d.get('formula', None)
        self._b = d.get('bVals', [])
        self._c = d.get('cVals', [])
        self._minMicrons = d.get('minMicrons', 0)
        self._maxMicrons = d.get('maxMicrons', 0)

    def get_ior(self, microns):
        if self._formula is None:
            raise Exception("No formula defined for the material: {}".format(self._name))
        if microns > self._maxMicrons or microns < self._minMicrons:
            warnings.warn("Wavelength exceeds defined wavelength range for the material: {}".format(self._name))

        # wavelength squared
        lsq = microns ** 2

        if self._formula == 'air':
            # n minus 1
            nm1 = self._b[0] / (self._c[0] - (1 / lsq)) + self._b[1] / (self._c[1] - (1 / lsq))
            return nm1 + 1

        if self._formula == 'sellmeier':
            # n squared minus 1
            nsqm1 = ((self._b[0] * lsq) / (lsq - self._c[0]) +
                     (self._b[1] * lsq) / (lsq - self._c[1]) +
                     (self._b[2] * lsq) / (lsq - self._c[2]))
            return np.sqrt(nsqm1 + 1)
