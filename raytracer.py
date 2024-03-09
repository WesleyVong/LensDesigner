import numpy as np
import scipy
import surface
from ray import Ray
from material import Material

EPSILON = 0.00001


def distance(T, f0, f1, n0=0, n1=0):
    # Distance between point intersections
    pos0 = f0(T[0], n0)
    pos1 = f1(T[1], n1)
    # Distanced multiplied to allow for more precise root optimization
    return [(pos0[0] - pos1[0])*100, (pos0[1] - pos1[1])*100]


def calculate_refraction(theta, n0, n1):
    # Using Snell's Law
    sin_ref = (n0/n1) * np.sin(theta)
    if sin_ref > 1 or sin_ref < -1:
        return np.nan
    return np.arcsin(sin_ref)


def raytrace(ray: Ray, surf: surface.Surface, atmo: Material):
    # Finds intersection between ray and surface
    # Atmo represents the surrounding material i.e. air
    intersect_t = []
    min_t = [np.inf, np.inf]
    min_e = -1
    for e in range(surf.num_equations):
        root = scipy.optimize.root(distance, x0=[0, 0], args=(ray.equation, surf.equation, 0, e),
                                   options={'maxfev': 50,
                                            'xtol': EPSILON})
        # if e == 2:
        #     print(root)
        if root.get('success'):
            t = root.get('x')
            if 0 <= t[0] < min_t[0]:
                min_t = t
                min_e = e

    if min_e == -1:
        return []

    hit_pos = ray.equation(min_t[0] + EPSILON)
    ray.end_t = min_t[0]

    r_tangent = ray.tangent(min_t[0])
    s_tangent = surf.tangent(min_t[1], min_e)
    s_ortho = [-s_tangent[1], s_tangent[0]]

    dot = np.dot(r_tangent, s_ortho)
    theta = np.arccos(dot)
    if s_ortho[1] < 0:
        theta = -theta

    new_rays = []
    object_material = surf.material

    for wavelength in ray.wavelengths:
        if ray.hits % 2 == 0:  # Either hasn't hit anything or just left an object
            n0 = atmo.get_ior(wavelength)
            n1 = object_material.get_ior(wavelength)
        else:
            n0 = object_material.get_ior(wavelength)
            n1 = atmo.get_ior(wavelength)
        angle = calculate_refraction(theta, n0, n1)
        if np.isnan(angle):
            continue
        new_ray = Ray(hit_pos, angle, mag=100, wavelengths=[wavelength], hits=ray.hits+1)
        new_rays.append(new_ray)
    return new_rays
