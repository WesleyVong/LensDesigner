from PIL import Image, ImageDraw
import json
import numpy as np
import raytracer
import renderer
import surface
import ray
from lens import Lens
from material import MaterialLibrary, Material
import scipy
import timeit

PAGE_WIDTH = 2000
PAGE_HEIGHT = 1000
EPSILON = 0.00001
FAST = True

material_library = MaterialLibrary('materials.json')

with open('Thorlabs.json') as json_file:
    lens_library = json.load(json_file)


im = renderer.Renderer(PAGE_WIDTH, PAGE_HEIGHT, scale=10)
initial_rays = []
for i in np.linspace(-9,9,10):
    initial_rays.append(ray.Ray([-20,i], 0,100, wavelengths=[.4, .7]))
l = Lens([0,0], material_library, fast=True)
# l.load_values(20,10,20, r1=-20, material='BK7')
l.load_from_dict(lens_library.get("AL2550"))


def distance(T, f0, f1, n0=0, n1=0):
    # Distance between point intersections
    pos0 = f0(T[0], n0)
    pos1 = f1(T[1], n1)
    print("T: {} pos0: {} pos1: {}".format(T, pos0, pos1))
    # Distanced multiplied to allow for more precise root optimization
    return [(pos0[0] - pos1[0])*10, (pos0[1] - pos1[1])*10]


def minimize_val(T, f0, f1):
    # Distance between point intersections
    pos0 = f0(T[0])
    pos1 = f1(T[1])
    point_dist = (pos0[0] - pos1[0])**2 + (pos0[1] - pos1[1])**2
    # t_dist = T[0]
    return point_dist + T[0]


im.DrawGrid([10,10])

for e in range(l.num_equations):
    im.DrawEquation(l.equation, 0, 1, 0.01, args=[e])

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

all_rays = compute()
for ray in all_rays:
    im.draw_ray(ray)
#
#
# # root = scipy.optimize.root(distance, x0=[0, 0], args=(first_hit[1].equation, l.equation, 0, 2),
# #                                    options={'maxfev': 50,
# #                                             'xtol': EPSILON})
# # print(root)
# #
im.ShowImage()