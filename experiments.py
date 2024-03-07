from PIL import Image, ImageDraw
import timeit
import renderer
import surface
from lens import Lens
from material import Material
import scipy

PAGE_WIDTH = 1000
PAGE_HEIGHT = 1000

im = renderer.Renderer(PAGE_WIDTH, PAGE_HEIGHT, scale=10)
s = surface.Polygon([0,0], [[-10,-10],[0,10],[10,-10],[5,-20]])
r = surface.Ray([-10,0],0,10)
l = Lens([0,0], Material())
l.load_values(20,20,20, k0=0)


def distance(T):
    pos0 = s.equation(T[0])
    pos1 = r.equation(T[1])
    return [pos0[0] - pos1[0], pos0[1] - pos1[1]]


im.DrawEquation(s.equation, 0, 1, 0.001)
im.DrawEquation(r.equation, 0, 1, 0.001)
im.DrawEquation(l.equation, 0, 1, 0.001)


# res = scipy.optimize.fsolve(distance, [0,0], full_output=True)
# print(res[2])

im.ShowImage()
