from PIL import Image, ImageDraw
import numpy as np
from ray import Ray


class Renderer:
    def __init__(self, width=512, height=512, scale=1, bg=(255,255,255)):
        self.width = width
        self.height = height
        self.scale = scale
        self.bg = bg
        self.image = Image.new(mode="RGB", size=(self.width, self.height), color = bg)
        self.drawing = ImageDraw.Draw(self.image)

    # Converts x and y values to local grid
    # Local grid centers image around 0,0
    def convert_xy(self, coords):
        new_x = int(self.width / 2 + coords[0] * self.scale)
        new_y = int(self.height / 2 - coords[1] * self.scale)
        return new_x, new_y

    # Draws parametric equation
    def draw_equation(self, f, tmin, tmax, step=-1,color=(0,0,0), args=[]):
        if step == -1:
            step = 1/self.scale
        prev_dist = np.inf
        for t in np.arange(tmin, tmax+step, step):
            coords = f(t, *args)
            if np.isnan(coords[0]) or np.isnan(coords[1]):
                return
            local_coords = self.convert_xy(coords)
            dist = coords[0]**2 + coords[1]**2
            if local_coords[0] < 0 or local_coords[0] >= self.width:
                if dist >= prev_dist:
                    return
                prev_dist = dist
                continue
            elif local_coords[1] >= self.height or local_coords[1] < 0:
                if dist >= prev_dist:
                    return
                prev_dist = dist
                continue
            self.drawing.point(local_coords, fill=color)
            # self.image.putpixel(localCoords, color)

    def draw_ray(self, ray: Ray):
        start_pos = self.convert_xy(ray.equation(0))
        end_pos = self.convert_xy(ray.equation(ray.end_t))
        mixed_color = [0,0,0]
        for wavelength in ray.wavelengths:
            color = wavelength_to_rgb(wavelength)
            mixed_color[0] += color[0]
            mixed_color[1] += color[1]
            mixed_color[2] += color[2]
        num_wavelengths = len(ray.wavelengths)
        mixed_color[0] /= num_wavelengths
        mixed_color[1] /= num_wavelengths
        mixed_color[2] /= num_wavelengths
        # print((int(mixed_color[0]), int(mixed_color[1]), int(mixed_color[2])))
        self.drawing.line([start_pos,end_pos],fill=(int(mixed_color[0]), int(mixed_color[1]), int(mixed_color[2])))

    def draw_lens(self, l, detail=50):
        points = []
        for i in np.linspace(l.start, l.end, detail):
            points.append(tuple(self.convert_xy(l.FrontEquation(i))))
        for i in np.linspace(l.end, l.start, detail):
            points.append(tuple(self.convert_xy(l.BackEquation(i))))
        self.drawing.polygon(points, outline=(0,0,0))

    def draw_grid(self, interval=(10,10), color=(100,100,100)):
        for x in range(-int(self.width / 2), int(self.width / 2)):
            for y in range(-int(self.height / 2), int(self.height / 2)):
                if x % (interval[0]) == 0 and y % (interval[1]) == 0:
                    local_coords = self.convert_xy((x,y))
                    if local_coords[0] < 0 or local_coords[0] >= self.width:
                        continue
                    if local_coords[1] >= self.height or local_coords[1] < 0:
                        continue
                    self.image.putpixel(local_coords, color)

    def show_image(self):
        self.image.show()

    def save_image(self, name="img"):
        self.image.save("{}.png".format(name))


def wavelength_to_rgb(microns):
    wavelength = microns * 1000
    r = 0
    g = 0
    b = 0
    factor =1
    if 380 <= wavelength < 440:
        r = -(wavelength - 400) / (440 - 380)
        g = 0
        b = 1
    elif 440 <= wavelength < 490:
        r = 0
        g = (wavelength - 440) / (490 - 440)
        b = 1
    elif 490 <= wavelength < 510:
        r = 0
        g = 1
        b = -(wavelength - 510) / (510-490)
    elif 510 <= wavelength < 580:
        r = (wavelength - 510) / (580 - 510)
        g = 1
        b = 0
    elif 580 <= wavelength < 645:
        r = 1
        g = -(wavelength - 645) / (645 - 580)
        b = 0
    elif 645 <= wavelength < 781:
        r = 1
        g = 0
        b = 0
    else:
        r = 0
        g = 0
        b = 0

    if 380 <= wavelength < 420:
        factor = 0.3 + 0.7 * (wavelength - 380) / (420 - 380)
    elif 420 <= wavelength < 701:
        factor = 1
    elif 701 <= wavelength < 781:
        factor = 0.3 + 0.7 * (780 - wavelength) / (780 - 700)
    else:
        factor = 0
    r = r * factor
    g = g * factor
    b = b * factor
    return int(r * 255), int(g*255), int(b*255)