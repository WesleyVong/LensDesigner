from PIL import Image, ImageDraw
import numpy as np
import lens

l = lens.Lens()
l.LoadLibrary("Thorlabs.json")
l.LoadPreset("AL2550")