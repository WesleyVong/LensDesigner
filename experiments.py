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
FAST = True

material_library = MaterialLibrary('materials.json')

with open('Thorlabs.json') as json_file:
    lens_library = json.load(json_file)


im = renderer.Renderer(PAGE_WIDTH, PAGE_HEIGHT, scale=10)
initial_rays = []
lenses = []
for i in np.linspace(-9, 9, 20):
    initial_rays.append(ray.Ray([-20, i], 0,100, wavelengths=[.4, .7]))

# l = Lens([0, 0], material_library, lens_dict=lens_library.get("LD2297"), fast=True)

l = Lens([0, 0], material_library, lens_dict=lens_library.get("LA1805"), fast=True)
lenses.append(l)
l = Lens([5.4 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LD2297"), fast=True)
lenses.append(l)
l = Lens([5.4 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LA1805"), direction='right', fast=True)
lenses.append(l)

im.draw_grid([10, 10])

for curr_lens in lenses:
    for eq in range(curr_lens.num_equations):
        im.draw_equation(curr_lens.equation, 0, 1, 0.01, args=[eq])


def compute():
    compute_rays = initial_rays
    all_rays = initial_rays
    for curr_lens in lenses:
        for i in range(2):
            hits = []
            computed_rays = []
            for curr_ray in compute_rays:
                rays = raytracer.raytrace(curr_ray, curr_lens, atmo=material_library.get('Air'), fast=FAST)
                for computed_ray in rays:
                    computed_rays.append(computed_ray)
            all_rays = all_rays + computed_rays
            compute_rays = computed_rays

    # first_hit = []
    # for ray in initial_rays:
    #     rays = raytracer.raytrace(ray, l, atmo=material_library.get('Air'), fast=FAST)
    #     for r in rays:
    #         first_hit.append(r)
    #
    # second_hit = []
    # for ray in first_hit:
    #     rays = raytracer.raytrace(ray, l, atmo=material_library.get('Air'), fast=FAST)
    #     for r in rays:
    #         second_hit.append(r)
    # all_rays = initial_rays + first_hit + second_hit
    return all_rays


all_rays = compute()
for ray in all_rays:
    im.draw_ray(ray)

im.show_image()
im.save_image('cooke-triplet')
