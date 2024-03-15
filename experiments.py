from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import json
import numpy as np
import math
import raytracer
import renderer
import surface
import ray
from lens import Lens
from aperture import Aperture
from material import MaterialLibrary, Material
import scipy
import timeit
import itertools
import os

PAGE_WIDTH = 1600
PAGE_HEIGHT = 800
FAST = True


def equivalent_focal_length(focal_lengths):
    # Probably based on thin lens approximation
    n = len(focal_lengths)
    focal_indices = list(range(n))
    numerator = np.prod(focal_lengths)
    unique_combinations = list(set(itertools.combinations(focal_indices, n-1)))
    denominator = sum([np.prod([focal_lengths[i] for i in comb]) for comb in unique_combinations])
    return numerator / denominator


if __name__ == "__main__":

    material_library = MaterialLibrary('materials.json')

    lens_library = {}

    lens_directory = 'LensLibrary'
    lens_json = os.listdir(lens_directory)
    for f in lens_json:
        with open('{}/{}'.format(lens_directory, f)) as json_file:
            lens_library.update(json.load(json_file))


    im = renderer.Renderer(PAGE_WIDTH, PAGE_HEIGHT, scale=10)

    lenses = []

    # 26mm f/2 4 element lens
    l = Lens([0, 0], material_library, lens_dict=lens_library.get("LA1027"), fast=True)
    lenses.append(l)
    l = Lens([0.1 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LC2679"), direction='right', fast=True)
    lenses.append(l)
    l = Aperture([4 + l.pos[0] + l.thickness, 0], 50.4, 24 / math.pow(2, 0.5*3))
    lenses.append(l)
    l = Lens([0.1 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LA1509"), direction='right', fast=True)
    lenses.append(l)
    l = Lens([0.1 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LA1805"), direction='right', fast=True)
    lenses.append(l)


    # l = Lens([0.1 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("AL2550"), fast=True)
    # lenses.append(l)
    # l = Lens([0.1 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LC2679"), direction='right', fast=True)
    # lenses.append(l)
    # l = Aperture([4 + l.pos[0] + l.thickness, 0], 50.4, 22 / math.pow(2, 0.5*2))
    # lenses.append(l)
    # l = Lens([0.1 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LA1509"), direction='right', fast=True)
    # lenses.append(l)
    # l = Lens([0.1 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LA1805"), direction='right', fast=True)
    # lenses.append(l)


    # 30mm f/4 lens using Cooke Triplet design
    # l = Lens([0, 0], material_library, lens_dict=lens_library.get("LA1074"), fast=True)
    # lenses.append(l)
    # l = Aperture([0.1 + l.pos[0] + l.thickness, 0], 25.4, 10)
    # lenses.append(l)
    # l = Lens([1 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LD2060"), fast=True)
    # lenses.append(l)
    # l = Aperture([1 + l.pos[0] + l.thickness, 0], 25.4, 4.6)
    # lenses.append(l)
    # l = Lens([0 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LA1074"), direction='right', fast=True)
    # lenses.append(l)

    # 31mm f/2 lens using 4 elements
    # l = Lens([0, 0], material_library, lens_dict=lens_library.get("LA1805"), fast=True)
    # lenses.append(l)
    # l = Aperture([0.1 + l.pos[0] + l.thickness, 0], 25.4, 12.7)
    # lenses.append(l)
    # l = Lens([.1 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LB1378"), fast=True)
    # lenses.append(l)
    # l = Lens([.5 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LD2060"), fast=True)
    # lenses.append(l)
    # l = Aperture([1 + l.pos[0] + l.thickness, 0], 25.4, 8.5)
    # lenses.append(l)
    # l = Lens([0.1 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LA1560"), direction='right', fast=True)
    # lenses.append(l)

    # l = Aperture([0, 0], 25.4, 8.5)
    # lenses.append(l)


    focal_lengths = []
    for l in lenses:
        try:
            focal_lengths.append(l.focal_length)
        except AttributeError:
            pass
    print("focal lengths: {}".format(focal_lengths))

    efl = equivalent_focal_length(focal_lengths)
    print("efl: {}".format(efl))

    F_STOP = 4

    SENSOR_DIAGONAL = math.sqrt(23.6**2 + 15.7**2)
    FOV = 2 * math.atan(SENSOR_DIAGONAL / (2 * efl))
    ANGLE = FOV / 2
    LIGHT_WIDTH = 22
    NUM_RAYS = 100

    emitter0 = ray.Emitter([5,0], NUM_RAYS, 'directed', [.4, .7], angle=0, size=LIGHT_WIDTH, magnitude=100)
    emitter1 = ray.Emitter([5,0], NUM_RAYS, 'directed', [.4, .7], angle=ANGLE, size=LIGHT_WIDTH)
    # emitter0 = ray.Emitter([5,0], NUM_RAYS, 'point', [.4, .7], angle=0, size=math.pi/90, magnitude=1000)
    # emitter1 = ray.Emitter([5,0], NUM_RAYS, 'point', [.4, .7], angle=ANGLE, size=math.pi/90, magnitude=1000)

    im.draw_grid([10, 10])

    for curr_lens in lenses:
        for eq in range(curr_lens.num_equations):
            im.draw_equation(curr_lens.equation, 0, 1, 0.01, args=[eq])


    def compute(emitter, assembly):
        compute_rays = emitter.rays
        total_rays = emitter.rays
        for curr_object in assembly:
            for i in range(2):
                computed_rays = []
                for curr_ray in compute_rays:
                    rays, hit = raytracer.raytrace(curr_ray, curr_object, atmo=material_library.get('Air'), fast=FAST)
                    for computed_ray in rays:
                        computed_rays.append(computed_ray)
                total_rays = total_rays + computed_rays
                compute_rays = computed_rays
        return total_rays, compute_rays

    total, computed = compute(emitter0, lenses)
    center_rays = len(computed)
    all_rays = total
    final_rays = computed

    final_angles = [final_rays[i].angle for i in range(len(final_rays))]
    theta = (max(final_angles) - min(final_angles))/2
    numerical_aperture = 1.0 * math.sin(theta)
    f_number = 1 / (2 * numerical_aperture)
    print("Theta: {} NA: {} F-Stop: {}".format(theta, numerical_aperture, f_number))

    total, computed = compute(emitter1, lenses)
    edge_rays = len(computed)
    all_rays = all_rays + total
    final_rays = final_rays + computed

    light_ratio = edge_rays/center_rays
    try:
        f_stops = math.log(light_ratio, 2)
    except ValueError:
        f_stops = math.nan
    print("Center rays: {} Edge rays: {} Ratio: {} Stops: {}".format(center_rays, edge_rays, light_ratio, f_stops))

    for i in range(len(all_rays)):
        # if i % 10 == 0:
        #     im.draw_ray(all_rays[i])
        #     im.draw_ray(all_rays[i-1])
        im.draw_ray(all_rays[i])

    # img = np.asarray(im.image)
    # plt.imshow(img)
    # plt.show()
    # im.save_image("31mm-f2-4elem")

    im.show_image()
