from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import json
import numpy as np
import math
import statistics
import raytracer
import renderer
import surface
import ray
from lens import Lens
from aperture import Aperture
from sensor import Sensor
from material import MaterialLibrary, Material
import scipy
import timeit
import itertools
import os

PAGE_WIDTH = 1000
PAGE_HEIGHT = 1000
PAGE_SCALE = 7
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

    SENSOR_DIAGONAL = math.sqrt(23.5**2 + 15.6**2)

    material_library = MaterialLibrary('materials.json')

    lens_library = {}

    lens_directory = 'LensLibrary'
    lens_json = os.listdir(lens_directory)
    for f in lens_json:
        with open('{}/{}'.format(lens_directory, f)) as json_file:
            lens_library.update(json.load(json_file))

    im = renderer.Renderer(PAGE_WIDTH, PAGE_HEIGHT, scale=PAGE_SCALE)
    lenses = []

    # 4 Element 30mm f/2
    NAME = "30mm_f2_4_element"
    LIGHT_WIDTH = 18
    l = Lens([0, 0], material_library, lens_dict=lens_library.get("LA1422"),
             fast=True)
    lenses.append(l)
    l = Aperture([0.1 + l.pos[0] + l.thickness, 0], 50.4, 20 / math.pow(2, 0.5 * 2))
    print(20 / math.pow(2, 0.5 * 2))
    lenses.append(l)
    l = Lens([.1 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LC2679"),
             direction='right', fast=True)
    lenses.append(l)
    l = Lens([2.5 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LB1596"),
             fast=True, direction='right')
    lenses.append(l)
    l = Lens([0.1 + l.pos[0] + l.thickness, 0], material_library, lens_dict=lens_library.get("LA1422"),
             fast=True, direction='right')
    lenses.append(l)
    a = Aperture([0.1 + l.pos[0] + l.thickness, 0], 50.4, 25.4)
    lenses.append(a)
    s = Sensor([24 + l.pos[0] + l.thickness, 0], 43.2)
    lenses.append(s)


    focal_lengths = []
    for l in lenses:
        try:
            focal_lengths.append(l.focal_length)
        except AttributeError:
            pass

    efl = equivalent_focal_length(focal_lengths)
    print("focal lengths: {} efl: {}".format(focal_lengths, efl))

    FOV = 2 * math.atan(SENSOR_DIAGONAL / (2 * efl))
    ANGLE = FOV / 2
    NUM_RAYS = 1000

    emitter0 = ray.Emitter([5,0], NUM_RAYS, 'directed', [.4, .7], angle=0, size=LIGHT_WIDTH, magnitude=100)
    emitter1 = ray.Emitter([5,0], NUM_RAYS, 'directed', [.4, .7], angle=ANGLE, size=LIGHT_WIDTH)
    # 150mm Close focusing
    # emitter0 = ray.Emitter([5,0], NUM_RAYS, 'point', [.4, .7], angle=0, size=math.pi/25, magnitude=300)
    # emitter1 = ray.Emitter([5,0], NUM_RAYS, 'point', [.4, .7], angle=ANGLE, size=math.pi/25, magnitude=300)

    im.draw_grid([10, 10])

    for curr_lens in lenses:
        for eq in range(curr_lens.num_equations):
            im.draw_equation(curr_lens.equation, 0, 1, 0.01, args=[eq])


    def compute(emitter, assembly):
        compute_rays = emitter.rays
        total_rays = emitter.rays
        sensor_rays = []
        for curr_object in assembly:
            for i in range(curr_object.num_equations):
                new_rays, pass_rays, hit_rays = raytracer.raytrace_multi(compute_rays, curr_object,
                                                                         material_library.get('Air'), FAST)
                if type(curr_object) == Sensor:
                    sensor_rays = hit_rays
                else:
                    compute_rays = new_rays + pass_rays
                    total_rays = total_rays + compute_rays
        return total_rays, compute_rays, sensor_rays

    def calculate_hits(hit_array, count=1000, density=100.0):
        hits = np.zeros(count)
        if len(hit_array) <= 1:
            return hits
        hit_positions = [int(h.equation(h.end_t)[1]*density) for h in hit_array]
        hit_range = max(hit_positions) - min(hit_positions)
        hit_mean = statistics.mean(hit_positions)
        hit_stdev = statistics.stdev(hit_positions)
        print("Range: {} Mean: {} StDev: {}".format(hit_range, hit_mean, hit_stdev))
        for h in hit_positions:
            y = h
            if abs(y) < (count/2):
                y = y + int(count/2)
                hits[y] += 1
        return hits


    total, computed, sensor_hits = compute(emitter0, lenses)
    center_rays = len(sensor_hits)
    all_rays = total
    final_rays = computed

    # Diagonal pixels are 255.3 px/mm * 43.2mm full frame
    print("Center Data:")
    pixels = int(255.3 * 43.2)
    hit_density = calculate_hits(sensor_hits, pixels, density=255.3)

    final_angles = [sensor_hits[i].angle for i in range(len(sensor_hits))]
    theta = (max(final_angles) - min(final_angles))/2
    numerical_aperture = 1.0 * math.sin(theta)
    if numerical_aperture != 0:
        f_number = 1 / (2 * numerical_aperture)
    else:
        f_number = 0
    print("Theta: {} NA: {} F-Stop: {}".format(theta, numerical_aperture, f_number))

    total, computed, sensor_hits = compute(emitter1, lenses)
    edge_rays = len(sensor_hits)
    all_rays = all_rays + total
    final_rays = final_rays + computed

    # Diagonal pixels are 145.5 px/mm * 43.2mm full frame
    print("Edge Data:")
    pixels = int(255.3 * 43.2)
    hit_density = hit_density + calculate_hits(sensor_hits, pixels, density=255.3)

    light_ratio = edge_rays/center_rays
    try:
        f_stops = math.log(light_ratio, 2)
    except ValueError:
        f_stops = math.nan
    print("Center rays: {} Edge rays: {} Ratio: {} Vignette Stops: {}".format(center_rays, edge_rays, light_ratio, f_stops))

    for i in range(len(all_rays)):
        if i % int(NUM_RAYS/20) == 0:
            im.draw_ray(all_rays[i])
            im.draw_ray(all_rays[i-1])

    fig, axs = plt.subplots(1, 2, figsize=(10,5))
    # image_plot = plt.subplot(1,2,1)
    # sensor_hit_plot = plt.subplot(1,2,2)

    axs[1].plot(np.linspace(-43.2/2 * 255.3, 43.2/2 * 255.3, pixels), hit_density)

    img = im.image
    axs[0].imshow(img, extent=[(-PAGE_WIDTH/2)/PAGE_SCALE,
                               (PAGE_WIDTH/2)/PAGE_SCALE,
                               (-PAGE_HEIGHT/2)/PAGE_SCALE,
                               (PAGE_HEIGHT/2)/PAGE_SCALE])
    plt.show()



    # for i in range(len(all_rays)):
    #     im.draw_ray(all_rays[i])
    # im.save_image(NAME)
    # im.show_image()
