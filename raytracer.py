import math
import scipy
import surface
from ray import Ray
from material import Material

EPSILON = 0.0001


def distance(T, f0, f1, n0=0, n1=0):
    # Distance between point intersections
    pos0 = f0(T[0], n0)
    pos1 = f1(T[1], n1)
    # Distanced multiplied to allow for more precise root optimization
    return [(pos0[0] - pos1[0]), (pos0[1] - pos1[1])]


def calculate_refraction(theta, n0, n1):
    # Using Snell's Law
    sin_ref = (n0/n1) * math.sin(theta)
    if -1 < sin_ref < 1:
        return math.asin(sin_ref)
    return math.nan


def raytrace(ray: Ray, surf: surface.Surface, atmo: Material, fast=False, epsilon=0.001):
    # Finds intersection between ray and surface
    # Atmo represents the surrounding material i.e. air
    min_t = [math.inf, math.inf]
    min_e = -1
    for e in range(surf.num_equations):
        root = scipy.optimize.root(distance, x0=[0, 0],
                                   args=(ray.equation, surf.equation, 0, e),
                                   method='hybr',
                                   tol=0.001,
                                   options={'maxfev': 40})
        if root.get('success'):
            t = root.get('x')
            if 0 <= t[0] < min_t[0]:
                min_t = t
                min_e = e
        else:
            print(root)

    if min_e == -1:
        return []

    hit_pos = ray.equation(min_t[0] + EPSILON)
    ray.end_t = min_t[0]

    r_tangent = ray.tangent(min_t[0])
    r_tangent_angle = math.atan(r_tangent[1]/r_tangent[0])
    s_tangent = surf.tangent(min_t[1], min_e)
    s_ortho = [-s_tangent[1], s_tangent[0]]
    s_ortho_angle = math.atan(s_ortho[1]/s_ortho[0])

    theta = s_ortho_angle - r_tangent_angle

    print("r_tangent_angle: {} s_ortho_angle: {} theta: {}".format(r_tangent_angle, s_ortho_angle, theta))

    new_rays = []
    object_material = surf.material

    angles = []

    for wavelength in ray.wavelengths:
        if ray.hits % 2 == 0:  # Either hasn't hit anything or just left an object
            n0 = atmo.get_ior(wavelength)
            n1 = object_material.get_ior(wavelength)
        else:
            n0 = object_material.get_ior(wavelength)
            n1 = atmo.get_ior(wavelength)
        angle = s_ortho_angle - calculate_refraction(theta, n0, n1)
        if fast:
            angles.append(angle)
            continue
        if math.isnan(angle):
            continue
        new_ray = Ray(hit_pos, angle, mag=100, wavelengths=[wavelength], hits=ray.hits + 1)
        new_rays.append(new_ray)

    if fast:
        angles_num = len(angles)
        diff = abs(max(angles) - min(angles))
        angles_avg = sum(angles) / angles_num
        if diff > epsilon:
            for i in range(angles_num):
                # If the difference between light scatter is greater than EPSILON, we use separate rays
                new_ray = Ray(hit_pos, angles[i], mag=100, wavelengths=[ray.wavelengths[i]], hits=ray.hits + 1)
                new_rays.append(new_ray)
        else:
            new_ray = Ray(hit_pos, angles_avg, mag=100, wavelengths=ray.wavelengths, hits=ray.hits + 1)
            new_rays.append(new_ray)

    return new_rays
