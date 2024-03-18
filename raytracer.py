import math
import scipy
import surface
from ray import Ray, Emitter
from material import Material

EPSILON = 0.00001


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


def calculate_guess(ray: Ray, surf: surface.Surface):
    # Makes a guess on where the intersection is.
    # This is done crudely by finding when the ray x is equal to the lens x
    dx = surf.pos[0] - ray.pos[0]
    r_t = dx / ray.dx
    s_t = 0
    return [r_t, s_t]


def raytrace_multi(rays, surf: surface.Surface, atmosphere: Material, fast=False, epsilon=0.001):
    hit_rays = []
    pass_rays = []
    new_rays = []
    for r in rays:
        result, hit = raytrace(r, surf, atmosphere, fast, epsilon)
        if hit:
            hit_rays.append(r)
            new_rays = new_rays + result
        else:
            pass_rays.append(r)
    return new_rays, pass_rays, hit_rays


def raytrace(ray: Ray, surf: surface.Surface, atmo: Material, fast=False, epsilon=0.001):
    # Finds intersection between ray and surface
    # Atmo represents the surrounding material i.e. air
    min_t = [math.inf, math.inf]
    min_e = -1
    for e in range(surf.num_equations):
        root = scipy.optimize.root(distance, x0=calculate_guess(ray, surf),
                                   args=(ray.equation, surf.equation, 0, e),
                                   method='hybr',
                                   options={'maxfev': 50})
        root_fun = root.get('fun')
        if abs(root_fun[0]) < EPSILON and abs(root_fun[1]) < EPSILON:
            t = root.get('x')
            if 0 <= t[0] < min_t[0]:
                min_t = t
                min_e = e
    if min_e == -1:
        # If there are no hits, then nothing
        return [], False

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
        # There are no refractions, but there is a hit
        if angles_num == 0:
            return [], True
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
