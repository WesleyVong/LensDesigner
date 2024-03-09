from PIL import Image, ImageDraw
import timeit
import numpy as np
import renderer
import surface
import ray
from lens import Lens
from material import Material
import scipy

PAGE_WIDTH = 1000
PAGE_HEIGHT = 1000

im = renderer.Renderer(PAGE_WIDTH, PAGE_HEIGHT, scale=10)
s = surface.Polygon([0,0], [[-10,-10],[0,10],[10,-10],[5,-20]])
r = ray.Ray([-20,0],0,50)
l = Lens([0,0], Material())
l.load_values(20,10,20, k0=0)


def distance(T, f0, f1, n0=0, n1=0):
    # Distance between point intersections
    pos0 = f0(T[0], n0)
    pos1 = f1(T[1], n1)
    # print("{} {} {}".format(T,pos0, pos1))
    return [pos0[0] - pos1[0], pos0[1] - pos1[1]]

def minimize_val(T, f0, f1):
    # Distance between point intersections
    pos0 = f0(T[0])
    pos1 = f1(T[1])
    point_dist = (pos0[0] - pos1[0])**2 + (pos0[1] - pos1[1])**2
    # t_dist = T[0]
    return point_dist + T[0]


im.DrawGrid([10,10])
im.DrawEquation(r.equation, 0, 1, 0.01, (255,0,0))
for e in range(s.num_equations):
    im.DrawEquation(s.equation, 0, 1, 0.01, args=[e])
for e in range(l.num_equations):
    im.DrawEquation(l.equation, 0, 1, 0.01, args=[e])

intercepts = []
for e in range(l.num_equations):
    intercepts.append(scipy.optimize.root(distance, [0,0], args=(r.equation, l.equation, 0, e), options={'maxfev': 10}))

for i in intercepts:
    print("Success: {} Location: {} Iters: {}".format(i.get("success"), i.get("x"), i.get("nfev")))

# int0 = scipy.optimize.root(distance, [0,0.25], args=(r.equation, l.equation))
# print("Intersection 0")
# print(int0)
#
# r = surface.Ray(r.equation(int0.get("x")[0]+0.001),-np.pi/2,50)
# im.DrawEquation(r.equation, 0, 1, 0.001, (0,255,0))
#
# int0 = scipy.optimize.root(distance, [1,0.75], args=(r.equation, l.equation))
# # int0 = scipy.optimize.minimize(minimize_val, [1,0.5], bounds=[(0,1),(0,1)], args=(r.equation, l.equation), method="Nelder-Mead")
# print("Intersection 1")
# print(int0)
#
# r = surface.Ray(r.equation(int0.get("x")[0]+0.001),-np.pi/2,50)
# im.DrawEquation(r.equation, 0, 1, 0.001, (0,0,255))



im.ShowImage()
