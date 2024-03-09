import multiprocessing
import queue

import numpy as np
import scipy
from PIL import Image
import PIL
import timeit
import matplotlib.pyplot as plt
import json
from multiprocessing import Process

import lens
import ray
import renderer
import emitter
import ior
import raytracer
import lensassembly

def RayTrace(lights, assembly):
    rays = np.array([])
    # Rays that go through the final glass element
    finalrays = np.array([])
    lenses = assembly.lenses
    for light in lights:
        rays = np.append(rays,light.rays)
        airIOR = ior.AirRefractiveIndex(light.microns)
        for r in light.rays:
            # rays.append(r)
            incidentray = r
            for i in range(len(lenses)):
                l = lenses[i]
                refracted = raytracer.GenerateRefractedRay(incidentray, l, airIOR, l.GetIOR(light.microns))
                rays = np.append(rays, refracted)
                if len(refracted) < 2:
                    break
                if i == len(lenses) - 1:
                    finalrays = np.append(finalrays,refracted[1])
                incidentray = refracted[1]

    return rays, finalrays
# Calculates the amount of hits on the sensor
def CalculateHits(finalrays, assembly, sensorDivision = 1000):
    sensorHeight2 = assembly.sensorHeight / 2
    division = sensorDivision / sensorHeight2 / 2

    sensorHit = np.zeros(sensorDivision)
    for r in finalrays:
        intersection = raytracer.CalculateIntersection(r.Equation, assembly.SensorEquation)
        if not intersection[1]:
            continue
        if intersection[0][0] < 0:
            continue
        if np.abs(intersection[0][1]) > sensorHeight2:
            continue
        intersectionIdx = (intersection[0][1]+sensorHeight2)*division
        sensorHit[int(intersectionIdx)] = sensorHit[int(intersectionIdx)]+1

    return sensorHit

def OptimizeHelper(lights, assembly):
    rays, finalrays =RayTrace(lights, assembly)
    sensorHit = CalculateHits(finalrays, assembly)
    hitStdev = np.std(sensorHit)
    percentHit = np.sum(sensorHit)/(lights[0].raynum * len(lights))
    return hitStdev, percentHit


def OptimizeFunc(offsets, assembly):
    startTime = timeit.default_timer()
    offsets = offsets * OPTIMIZE_SCALE_FACTOR
    for idx  in range(len(offsets)):
        assembly.SetOffset(idx + 1, offsets[idx])

    hitStdev = np.zeros(3)
    percentHit = np.zeros(3)

    lights = []
    lights.append(emitter.Emitter([-1000, 0], RAYS, 0, PLANE_WIDTH, microns=WAVELENGTH_R, type="plane"))
    lights.append(emitter.Emitter([-1000, 0], RAYS, 0, PLANE_WIDTH, microns=WAVELENGTH_V, type="plane"))

    hitStdev[0], percentHit[0] = OptimizeHelper(lights, assembly)

    lights = []
    lights.append(emitter.Emitter([-1000, -emity],RAYS,DIR,size=PLANE_WIDTH, microns=WAVELENGTH_R,type="plane"))
    lights.append(emitter.Emitter([-1000, -emity], RAYS, DIR, size=PLANE_WIDTH, microns=WAVELENGTH_V, type="plane"))
    hitStdev[1], percentHit[1] = OptimizeHelper(lights, assembly)

    # lights = []
    #
    # lights.append(emitter.Emitter([-1000, emity], RAYS, -DIR, size=PLANE_WIDTH, microns=WAVELENGTH_R, type="plane"))
    # lights.append(emitter.Emitter([-1000, emity], RAYS, -DIR, size=PLANE_WIDTH,microns=WAVELENGTH_V, type="plane"))
    # hitStdev[2], percentHit[2] = OptimizeHelper(lights, assembly)

    results = np.array([hitStdev[0], hitStdev[1], 1-(percentHit[0] * percentHit[1])])
    weights = np.array([1,0.5,1])

    score = np.sum(results * weights)

    print("Offsets: {} Results: {} Score: {} Time: {}".format(offsets, results, score, timeit.default_timer() - startTime))
    return score


def DrawImage(rays, assembly,imageSize=[2000,1000], saveName="default"):
    startTime = timeit.default_timer()

    lenses = assembly.lenses
    PAGE_WIDTH = imageSize[0]
    PAGE_HEIGHT = imageSize[1]

    im = renderer.Renderer(PAGE_WIDTH, PAGE_HEIGHT, scale=10)
    for l in lenses:
        im.DrawLens(l)

    im.DrawEquation(assembly.SensorEquation, -assembly.sensorHeight/2, assembly.sensorHeight/2)

    im.DrawGrid((10, 10))

    for r in rays:
        im.DrawRay(r)

    print("Draw time: {}".format(timeit.default_timer() - startTime))

    # im.ShowImage()
    im.SaveImage(saveName)

if __name__ == '__main__':
    startTime = timeit.default_timer()
    WAVELENGTH_R = 0.700  # 700nm
    WAVELENGTH_V = 0.400  # 400nm
    FLANGE_DISTANCE = 18    # 18mm for Sony E mount
    SENSOR_HEIGHT = 25.1    # Width of Sony APS-C Sensor

    f = open("Thorlabs.json")
    lib = json.load(f)

    lens3 = lensassembly.LensAssembly([0,0],lib, sensorOffset=FLANGE_DISTANCE, sensorHeight=SENSOR_HEIGHT)
    lens3.AddLens("LB1811")
    # lens3.AddLens("LA1805")# 30mm Focal Length PlanoConvex
    # lens3.AddLens("LD2297",5.4)# -25mm Focal Length BiConcave
    # lens3.AddLens("LA1805",5,"right")# 30mm Focal Length PlanoConvex
    # print(lens3)

    DIR = 15 * np.pi/180

    RAYS = 500
    PLANE_WIDTH = 16
    ARC = np.pi / 75
    emity = (1000 / np.cos(DIR)) * np.sin(DIR)
    lights = []
    lights.append(emitter.Emitter([-1000, 0],RAYS,0,PLANE_WIDTH, microns=WAVELENGTH_R,type="plane"))
    lights.append(emitter.Emitter([-1000, 0], RAYS, 0, PLANE_WIDTH, microns=WAVELENGTH_V, type="plane"))
    # lights.append(emitter.Emitter([-1000, -emity],RAYS,DIR,size=PLANE_WIDTH, microns=WAVELENGTH_R,type="plane"))
    # lights.append(emitter.Emitter([-1000, -emity], RAYS, DIR, size=PLANE_WIDTH, microns=WAVELENGTH_V, type="plane"))
    # lights.append(emitter.Emitter([-1000, emity], RAYS, -DIR, size=PLANE_WIDTH, microns=WAVELENGTH_R, type="plane"))
    # lights.append(emitter.Emitter([-1000, emity], RAYS, -DIR, size=PLANE_WIDTH,microns=WAVELENGTH_V, type="plane"))

    # lightR = emitter.Emitter([-1000 / 4, -176.3 / 4],RAYS,DIR,size=20,arc=ARC, microns=WAVELENGTH_R,type="arc")
    # lightG = emitter.Emitter([-1000 / 4, 0], RAYS, 0, size=20, arc=ARC, microns=WAVELENGTH_G, type="arc")
    # lightV = emitter.Emitter([-1000 / 4, 176.3 / 4], RAYS, -DIR, size=20,arc=ARC,microns=WAVELENGTH_V, type="arc")

    # rays = RayTrace(lights, lens3)
    # DrawImage(rays,lens3,saveName="CookeTriplet")
    #
    OPTIMIZE_SCALE_FACTOR = 1000000

    cons = ({'type': 'ineq', 'fun': lambda x:  x[0]},
           {'type': 'ineq', 'fun': lambda x:  x[1]},
           {'type': 'ineq', 'fun': lambda x:  x[2]})

    x0 = np.array([3,3])
    bounds = [(2/OPTIMIZE_SCALE_FACTOR,1),(2/OPTIMIZE_SCALE_FACTOR,1)]

    # scipy.optimize.minimize(OptimizeFunc, x0  / OPTIMIZE_SCALE_FACTOR, (lens3),
    #                         constraints=cons, method='Nelder-Mead',bounds=bounds, options={"maxiter":1000})

    lights = []
    lights.append(emitter.Emitter([-1000, 0],RAYS,0,PLANE_WIDTH, microns=WAVELENGTH_R,type="plane"))
    lights.append(emitter.Emitter([-1000, 0], RAYS, 0, PLANE_WIDTH, microns=WAVELENGTH_V, type="plane"))
    # lights.append(emitter.Emitter([-1000, -emity],RAYS,DIR,size=PLANE_WIDTH, microns=WAVELENGTH_R,type="plane"))
    # lights.append(emitter.Emitter([-1000, -emity], RAYS, DIR, size=PLANE_WIDTH, microns=WAVELENGTH_V, type="plane"))
    # lights.append(emitter.Emitter([-1000, emity], RAYS, -DIR, size=PLANE_WIDTH, microns=WAVELENGTH_R, type="plane"))
    # lights.append(emitter.Emitter([-1000, emity], RAYS, -DIR, size=PLANE_WIDTH,microns=WAVELENGTH_V, type="plane"))

    rays, finalrays = RayTrace(lights, lens3)

    sensorHit = CalculateHits(finalrays, lens3)

    sensorHeight = len(sensorHit)/2

    print("Raytrace time: {}".format(timeit.default_timer() - startTime))
    plt.plot(np.linspace(-sensorHeight,sensorHeight,len(sensorHit)),sensorHit/(RAYS*2))
    plt.savefig('CookeTriplet-plt.png')
    # plt.show()

    lights = []
    lights.append(emitter.Emitter([-1000, 0],20,0,PLANE_WIDTH, microns=WAVELENGTH_R,type="plane"))
    lights.append(emitter.Emitter([-1000, 0], 20, 0, PLANE_WIDTH, microns=WAVELENGTH_V, type="plane"))
    # lights.append(emitter.Emitter([-1000, -emity],20,DIR,size=PLANE_WIDTH, microns=WAVELENGTH_R,type="plane"))
    # lights.append(emitter.Emitter([-1000, -emity], 20, DIR, size=PLANE_WIDTH, microns=WAVELENGTH_V, type="plane"))
    # lights.append(emitter.Emitter([-1000, emity], 20, -DIR, size=PLANE_WIDTH, microns=WAVELENGTH_R, type="plane"))
    # lights.append(emitter.Emitter([-1000, emity], 20, -DIR, size=PLANE_WIDTH,microns=WAVELENGTH_V, type="plane"))

    rays, finalrays = RayTrace(lights, lens3)

    DrawImage(rays, lens3, saveName="CookeTriplet")

