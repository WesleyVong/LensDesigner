import json
import numpy as np
import raytracer
import ray
from lens import Lens
from material import MaterialLibrary, Material
import timeit


FAST = True

material_library = MaterialLibrary('materials.json')

with open('Thorlabs.json') as json_file:
    lens_library = json.load(json_file)

initial_rays = []
for i in np.linspace(-9,9,1000):
    initial_rays.append(ray.Ray([-20,i], 0,100, wavelengths=[.4, .7]))
l = Lens([0,0], material_library, fast=True)
l.load_from_dict(lens_library.get("AL2550"))


def compute():
    first_hit = []
    for ray in initial_rays:
        rays = raytracer.raytrace(ray, l, atmo=material_library.get('Air'), fast=FAST)
        for r in rays:
            first_hit.append(r)

    second_hit = []
    for ray in first_hit:
        rays = raytracer.raytrace(ray, l, atmo=material_library.get('Air'), fast=FAST)
        for r in rays:
            second_hit.append(r)
    all_rays = initial_rays + first_hit + second_hit
    return all_rays


def benchmark(iter=100):
    elapsed = []
    for i in range(iter):
        start_time = timeit.default_timer()
        compute()
        elapsed.append(timeit.default_timer() - start_time)
        print("iter: {} elapsed: {}".format(i, elapsed[-1]))
    return sum(elapsed) / len(elapsed)


avg_time = benchmark(10)
print("average time: {}".format(avg_time))