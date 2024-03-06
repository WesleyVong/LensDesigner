from PIL import Image, ImageDraw
import timeit
import renderer
import surface

PAGE_WIDTH = 1000
PAGE_HEIGHT = 1000

im = renderer.Renderer(PAGE_WIDTH, PAGE_HEIGHT, scale=10)
s = surface.Polygon([0,0], [[-10,-10],[0,10],[10,-10],[5,-20]])

im.DrawEquation(s.equation, 0, 1, 0.001)

im.ShowImage()
