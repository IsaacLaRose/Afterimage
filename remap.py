import numpy as np
import anim
from PIL import Image
from utils import resize_image




def remap_pixels(substance,template, mode):
    original_substance = substance.copy()
    substance = resize_image(substance, template.shape)

    #Flatten images into array
    flat = substance.reshape(-1,3)
    flat2 = template.reshape(-1,3)

    #sort based on pixel brightness
    brightness1 = flat.mean(axis=1)
    brightness2 = flat2.mean(axis=1)
    substance_sort = np.argsort(brightness1)
    template_sort = np.argsort(brightness2)

    newarr = np.zeros_like(flat)


    #choice between animation
    if mode == "travel":
        frames = anim.travel(flat, template, substance_sort, template_sort)
        newarr = np.array(frames[-1])  # grab before padding
        frames = [Image.fromarray(substance)] * 8 + frames + [frames[-1]] * 8

    if mode == "band":
        frames = anim.band(flat, template, substance, substance_sort, template_sort)
        newarr = np.array(frames[-1])  # grab before padding
        frames = [Image.fromarray(substance)] * 8 + frames + [frames[-1]] * 8

    return newarr, frames