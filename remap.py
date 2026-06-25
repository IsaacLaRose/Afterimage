import numpy as np
from PIL import Image
from utils import resize_image



def remap_pixels(substance,template, n_bands=30):
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

    band_size = len(flat) // n_bands
    frames = []

    for band in range(1, n_bands + 1):
        current = flat.copy()
        count = band_size * band

        for i in range(count):
            current[template_sort[i]] = flat[substance_sort[i]]

        frame = current.reshape(template.shape).astype(np.uint8)
        frames.append(Image.fromarray(frame))

    newarr = current.reshape(template.shape)
    frames = [Image.fromarray(substance)] * 5 + frames + [frames[-1]] * 5
    return newarr, frames