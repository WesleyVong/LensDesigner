import numpy as np
import scipy
import ray
import lens
import timeit

# Calculates refraction angle using Snell's law
# Input: angle of incidence (radians), material 1 refractive index, material 2 refractive index
def CalculateRefraction(angle, n1, n2):
    # sin of the angle of refraction
    sref = (n1/n2) * np.sin(angle)
    if sref > 1 or sref < -1:
        return np.nan
    ret = np.arcsin(sref)
    return ret

# Calculates intersection point, T for both parametric equations
def CalculateIntersection(f0, f1, x0=[0,0]):
    def DistanceFunc(T):
        r0 = f0(T[0])
        r1 = f1(T[1])
        return [r0[0] - r1[0], r0[1] - r1[1]]
    try:
        root = scipy.optimize.fsolve(DistanceFunc, x0=x0)
    except RuntimeError:
        return [[np.nan,np.nan], False]
    if np.isnan(root[0]) or np.isnan(root[1]):
        return [[np.nan,np.nan], False]
    return [root, True]

# Calculates the tangent slope of a parametric equation f(t) at point t
# Epsilon determines how close to t the tangent should be estimated
def CalculateTangent(f, t, epsilon = 0.001):
    xy0 = f(t+epsilon)
    xy1 = f(t-epsilon)
    return [xy0[0] - xy1[0], xy0[1] - xy1[1]]

# Calculates the normal vector of a vector input
def CalculateNormal(xy):
    x = -xy[1]
    y = xy[0]
    return [x,y]

# Calculates indicent angle between two equations at a given point
# In this case, T is derived from result.x
def CalculateIncidentAngle(f0, f1, T):
    startTime = timeit.default_timer()
    f0t = CalculateTangent(f0, T[0])
    f1t = CalculateTangent(f1, T[1])
    # Find normal of tangent
    f1n = CalculateNormal(f1t)
    if (f0t[0] == 0):
        f01 = np.pi/2
    else:
        f0a = np.arctan(f0t[1] / f0t[0])
    if (f1n[0] == 0):
        f1na = np.pi/2
    else:
        f1na = np.arctan(f1n[1] / f1n[0])
    angle = f0a - f1na

    return angle

# Calculates the refracted ray given the:
# Ray Object, Lens Object, IOR of material 1 and IOR of material 2, wavelength of light
def GenerateRefractedRay(r, l, n0, n1):
    radius = l.config["diameter"]/2
    ### Front Surface ###
    req = r.Equation
    leq = l.FrontEquation

    x0 = [(l.pos[0] - r.pos[0]) / r.dx, 0]
    if (x0[0] < 0):
        return []
    intersection = CalculateIntersection(req, leq, x0=x0)

    if not intersection[1]:
        return []
    if np.abs(intersection[0][1]) > radius:
        return []

    incident = CalculateIncidentAngle(req, leq, intersection[0])
    refraction = CalculateRefraction(incident, n0, n1)

    # Find normal to front or back surface
    lt = CalculateTangent(leq, intersection[0][1])
    ln = CalculateNormal(lt)

    # Find normal angle relative to x axis
    la = np.arctan(ln[1]/ln[0])

    # Ray angle
    ra = la + refraction

    fRay = ray.Ray(req(intersection[0][0]-0.001), ra,r.microns)

    r.SetEnd(intersection[0][0])

### Back Surface ###
    req = fRay.Equation
    leq = l.BackEquation

    x0 = [(l.pos[0] - r.pos[0]) / r.dx, 0]
    # x0 = [np.sqrt((l.pos[0]-r.pos[0])**2 + (l.pos[1]-r.pos[1])**2), 0]
    if (x0[0] < 0):
        return [fRay]
    intersection = CalculateIntersection(req, leq, x0=x0)
    if not intersection[1]:
        return [fRay]
    if np.abs(intersection[0][1]) > radius:
        return [fRay]

    incident = CalculateIncidentAngle(req, leq, intersection[0])
    refraction = CalculateRefraction(incident, n1, n0)

    # Find normal to front or back surface
    lt = CalculateTangent(leq, intersection[0][1])
    ln = CalculateNormal(lt)

    # Find normal angle relative to x axis
    la = np.arctan(ln[1] / ln[0])

    # Ray angle
    ra = la + refraction

    bRay = ray.Ray(req(intersection[0][0]-0.001), ra, r.microns)

    fRay.SetEnd(intersection[0][0])

    return  [fRay, bRay]