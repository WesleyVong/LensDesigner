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

PAGE_WIDTH = 1000
PAGE_HEIGHT = 500
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

    with open('thorlabs.json') as json_file:
        lens_library = json.load(json_file)

    im = renderer.Renderer(PAGE_WIDTH, PAGE_HEIGHT, scale=10)

    lenses = []

    # l = Lens([0, 0], material_library, lens_dict=lens_library.get("LA1289"), fast=True)
    # lenses.append(l)
    # l = Aperture([0.1 + l.pos[0] + l.thickness, 0], 25.4, 12.7)
    # lenses.append(l)
    # l = Lens([.1 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LB1378"), fast=True)
    # lenses.append(l)
    # l = Lens([.5 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LD2060"), fast=True)
    # lenses.append(l)
    # l = Aperture([1 + l.pos[0] + l.thickness, 0], 25.4, 10)
    # lenses.append(l)
    # l = Lens([.1 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LA1560"), direction='right', fast=True)
    # lenses.append(l)


    # l = Lens([0, 0], material_library, lens_dict=lens_library.get("LA1074"), fast=True)
    # lenses.append(l)
    # l = Aperture([0.1 + l.pos[0] + l.thickness, 0], 25.4, 10)
    # lenses.append(l)
    # l = Lens([1 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LD2060"), fast=True)
    # lenses.append(l)
    # l = Aperture([1 + l.pos[0] + l.thickness, 0], 25.4, 5)
    # lenses.append(l)
    # l = Lens([0 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LA1074"), direction='right', fast=True)
    # lenses.append(l)

    l = Lens([0, 0], material_library, lens_dict=lens_library.get("LA1805"), fast=True)
    lenses.append(l)
    l = Aperture([0.01 + l.pos[0] + l.thickness, 0], 25.4, 12.7)
    lenses.append(l)
    l = Lens([.01 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LB1378"), fast=True)
    lenses.append(l)
    l = Lens([.5 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LD2060"), fast=True)
    lenses.append(l)
    l = Aperture([1 + l.pos[0] + l.thickness, 0], 25.4, 8.5)
    lenses.append(l)
    l = Lens([0.1 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LA1560"), direction='right', fast=True)
    lenses.append(l)


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
    LIGHT_WIDTH = 20
    NUM_RAYS = 20
    initial_rays = []
    for i in np.linspace(-LIGHT_WIDTH/2, LIGHT_WIDTH/2, NUM_RAYS):
        initial_rays.append(ray.Ray([-20, i], 0, 100, wavelengths=[.4]))



    # Get direction of Ray
    # xydir = np.array([math.cos(ANGLE), math.sin(ANGLE)])
    #
    # # Calculate normal of direction
    # xystep = np.random.rand(2)
    # xystep = xystep - xystep.dot(xydir) * xydir
    # xystep = xystep / np.linalg.norm(xystep)
    # xstep = xystep[0] * LIGHT_WIDTH / 2
    # ystep = xystep[1] * LIGHT_WIDTH / 2
    #
    # x = math.cos(ANGLE)*-20
    # y = math.sin(ANGLE)*-20 - 2
    #
    # coords = np.linspace([x - xstep, y - ystep], [x + xstep, y + ystep], NUM_RAYS)
    # for coord in coords:
    #     initial_rays.append(ray.Ray(coord, ANGLE, 100, wavelengths=[.4, .7]))

    im.draw_grid([10, 10])

    for curr_lens in lenses:
        for eq in range(curr_lens.num_equations):
            im.draw_equation(curr_lens.equation, 0, 1, 0.01, args=[eq])


    def compute(lights, assembly):
        compute_rays = lights
        total_rays = lights
        for curr_object in assembly:
            for i in range(2):
                computed_rays = []
                for curr_ray in compute_rays:
                    rays = raytracer.raytrace(curr_ray, curr_object, atmo=material_library.get('Air'), fast=FAST)
                    for computed_ray in rays:
                        computed_rays.append(computed_ray)
                total_rays = total_rays + computed_rays
                compute_rays = computed_rays
        return total_rays, compute_rays


    all_rays, final_rays = compute(initial_rays, lenses)
    # final_angles = [final_rays[i].angle for i in range(len(final_rays))]
    # theta = (max(final_angles) - min(final_angles))/2
    # numerical_aperture = 1.0 * math.sin(theta)
    # f_number = 1 / (2 * numerical_aperture)
    # print("Theta: {} NA: {} F-Stop: {}".format(theta, numerical_aperture, f_number))
    for ray in all_rays:
        im.draw_ray(ray)

    img = np.asarray(im.image)
    plt.imshow(img)
    plt.show()
    # im.show_image()
    # im.save_image('cooke-triplet')
