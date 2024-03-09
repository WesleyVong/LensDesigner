from PIL import Image, ImageDraw
import numpy as np
import scipy
import timeit

import ray
import lens

class Renderer:
    def __init__(self, width=512, height=512, scale=1,bg=(255,255,255)):
        self.width = width
        self.height = height
        self.scale = scale
        self.bg = bg
        self.image = Image.new(mode="RGB", size=(self.width, self.height), color = bg)
        self.drawing = ImageDraw.Draw(self.image)

    # Converts x and y values to local grid
    # Local grid centers image around 0,0
    def ConvertXY(self, coords):
        newX = int(self.width / 2 + coords[0] * self.scale)
        newY = int(self.height / 2 - coords[1] * self.scale)
        return (newX, newY)

    # Draws parametric equation
    def DrawEquation(self, f, tmin, tmax, step=-1,color=(0,0,0), args=[]):
        if step == -1:
            step = 1/self.scale
        inDrawing = True
        prevDist = np.inf
        for t in np.arange(tmin, tmax+step, step):
            coords = f(t, *args)
            if np.isnan(coords[0]) or np.isnan(coords[1]):
                return
            localCoords = self.ConvertXY(coords)
            dist = coords[0]**2 + coords[1]**2
            if localCoords[0] < 0 or localCoords[0] >= self.width:
                if dist >= prevDist:
                    return
                prevDist = dist
                continue
            elif localCoords[1] >= self.height or localCoords[1] < 0:
                if dist >= prevDist:
                    return
                prevDist = dist
                continue
            self.drawing.point(localCoords, fill=color)
            # self.image.putpixel(localCoords, color)

    def DrawRay(self, r):
        startXY = self.ConvertXY(r.Equation(r.start))
        endXY = self.ConvertXY(r.Equation(r.end))
        self.drawing.line([startXY,endXY],fill=(WavelengthToRGB(r.microns)))

    def DrawLens(self, l, detail=50):
        points = []
        for i in np.linspace(l.start, l.end, detail):
            points.append(tuple(self.ConvertXY(l.FrontEquation(i))))
        for i in np.linspace(l.end, l.start, detail):
            points.append(tuple(self.ConvertXY(l.BackEquation(i))))
        self.drawing.polygon(points, outline=(0,0,0))

    def DrawGrid(self, interval=(10,10), color=(100,100,100)):
        for x in range(-int(self.width / 2), int(self.width / 2)):
            for y in range(-int(self.height / 2), int(self.height / 2)):
                if x % (interval[0]) == 0 and y % (interval[1]) == 0:
                    localCoords = self.ConvertXY((x,y))
                    if localCoords[0] < 0 or localCoords[0] >= self.width:
                        continue
                    if localCoords[1] >= self.height or localCoords[1] < 0:
                        continue
                    self.image.putpixel(localCoords, color)

    def ShowImage(self):
        self.image.show()

    def SaveImage(self, name="img"):
        self.image.save("{}.png".format(name))

def WavelengthToRGB(microns):
    wavelength = microns * 1000
    r = 0
    g = 0
    b = 0
    factor =1
    if 380 <= wavelength < 440:
        r = -(wavelength - 400) / (440 - 380)
        g = 0
        b = 1
    elif 440 <= wavelength < 490:
        r = 0
        g = (wavelength - 440) / (490 - 440)
        b = 1
    elif 490 <= wavelength < 510:
        r = 0
        g = 1
        b = -(wavelength - 510) / (510-490)
    elif 510 <= wavelength < 580:
        r = (wavelength - 510) / (580 - 510)
        g = 1
        b = 0
    elif 580 <= wavelength < 645:
        r = 1
        g = -(wavelength - 645) / (645 - 580)
        b = 0
    elif 645 <= wavelength < 781:
        r = 1
        g = 0
        b = 0
    else:
        r = 0
        g = 0
        b = 0

    if 380 <= wavelength < 420:
        factor = 0.3 + 0.7 * (wavelength - 380) / (420 - 380)
    elif 420 <= wavelength < 701:
        factor = 1
    elif 701 <= wavelength < 781:
        factor = 0.3 + 0.7 * (780 - wavelength) / (780 - 700)
    else:
        factor = 0
    r = r * factor
    g = g * factor
    b = b * factor
    return (int(r * 255), int(g*255), int(b*255))