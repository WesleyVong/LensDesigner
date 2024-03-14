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
                                   options={'maxfev': 20})
        if root.get('success'):
            t = root.get('x')
            if 0 <= t[0] < min_t[0]:
                min_t = t
                min_e = e
        # else:
        #     print(root)
    if min_e == -1:
        return [ray], False

    hit_pos = ray.equation(min_t[0] + EPSILON)
    ray.end_t = min_t[0]

    r_tangent = ray.tangent(min_t[0])
    r_tangent_angle = math.atan2(r_tangent[1], r_tangent[0])
    s_ortho = surf.normal(min_t[1], min_e)
    s_ortho_angle = math.atan2(s_ortho[1], s_ortho[0])

    theta = r_tangent_angle - s_ortho_angle

    if abs(theta) > math.pi / 2:  # Ray is entering object
        n0_mat = atmo
        n1_mat = surf.material
        s_ortho_angle_out = s_ortho_angle + math.pi
        theta_incident = theta + math.pi
    else:
        n0_mat = surf.material
        n1_mat = atmo
        s_ortho_angle_out = s_ortho_angle
        theta_incident = theta

    new_rays = []
    angles = []
    new_wavelengths = []

    for wavelength in ray.wavelengths:
        n0 = n0_mat.get_ior(wavelength)
        n1 = n1_mat.get_ior(wavelength)
        if n0 == 0 or n1 == 0:
            continue
        angle = calculate_refraction(theta_incident, n0, n1)
        angle = s_ortho_angle_out + angle
        if math.isnan(angle):
            continue
        if fast:
            angles.append(angle)
            new_wavelengths.append(wavelength)
            continue
        new_ray = Ray(hit_pos, angle, mag=100, wavelengths=[wavelength])
        new_rays.append(new_ray)

    if fast:
        angles_num = len(angles)
        if angles_num == 0:
            return new_rays
        diff = abs(max(angles) - min(angles))
        angles_avg = sum(angles) / angles_num
        if diff > epsilon:
            for i in range(angles_num):
                # If the difference between light scatter is greater than EPSILON, we use separate rays
                new_ray = Ray(hit_pos, angles[i], mag=100, wavelengths=[new_wavelengths[i]])
                new_rays.append(new_ray)
        else:
            new_ray = Ray(hit_pos, angles_avg, mag=100, wavelengths=new_wavelengths)
            new_rays.append(new_ray)

    return new_rays, True
