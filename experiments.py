from PIL import Image, ImageDraw
import timeit
import renderer
import surface

PAGE_WIDTH = 1000
PAGE_HEIGHT = 1000

im = renderer.Renderer(PAGE_WIDTH, PAGE_HEIGHT, scale=10)
s = surface.Polygon([0,0], [[-10,-10],[0,10],[10,-10],[5,-20]])
r = surface.Ray([-10,0],0,100)

def distance(pos0, pos1):
    return (pos1[0] - pos0[0])**2 + (pos1[1] - pos0[1])**2



im.DrawEquation(s.equation, 0, 1, 0.001)
im.DrawEquation(r.equation, 0, 1, 0.001)

im.ShowImage()
