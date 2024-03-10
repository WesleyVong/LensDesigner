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


if __name__ == '__main__':
    WAVELENGTH_R = 0.700  # 700nm
    WAVELENGTH_V = 0.400  # 400nm
    FLANGE_DISTANCE = 18    # 18mm for Sony E mount
    SENSOR_HEIGHT = 25.1    # Width of Sony APS-C Sensor

    f = open("Thorlabs.json")
    lib = json.load(f)

    lens3 = lensassembly.LensAssembly([0,0],lib, sensorOffset=FLANGE_DISTANCE, sensorHeight=SENSOR_HEIGHT)
    lens3.AddLens("AL2550")
    print(lens3)

    DIR = 15 * np.pi/180

    RAYS = 1000
    PLANE_WIDTH = 18
    lights = []
    lights.append(emitter.Emitter([-1000, 0],RAYS,0,PLANE_WIDTH, microns=WAVELENGTH_R,type="plane"))
    lights.append(emitter.Emitter([-1000, 0], RAYS, 0, PLANE_WIDTH, microns=WAVELENGTH_V, type="plane"))

    def benchmark(iter=100):
        elapsed = []
        for i in range(iter):
            startTime = timeit.default_timer()
            RayTrace(lights, lens3)
            elapsed.append(timeit.default_timer() - startTime)
            print("iter: {} elapsed: {}".format(i, elapsed[-1]))
        return sum(elapsed) / len(elapsed)


    avg_time = benchmark(10)
    print("average time: {}".format(avg_time))


