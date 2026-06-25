import numpy as np
from PIL import Image
from utils import resize_image



def remap_pixels(substance,template, n_frames=40):
    substance = resize_image(substance, template.shape)

    #Flatten images into array
    flat = substance.reshape(-1,3)
    flat2 = template.reshape(-1,3)

    #sort based on pixel brightness
    brightness1 = flat.mean(axis=1)
    brightness2 = flat2.mean(axis=1)
    substance_sort = np.argsort(brightness1)
    template_sort = np.argsort(brightness2)

    h, w = template.shape[:2]
    start_positions = np.array(np.unravel_index(substance_sort, (h, w))).T
    end_positions = np.array(np.unravel_index(template_sort, (h, w))).T
    colors = flat[substance_sort]

    frames = []

    for frame_idx in range(n_frames):
        t = frame_idx / (n_frames - 1)
        canvas = np.zeros((h, w, 3), dtype=np.uint8)

        current_positions = (start_positions + (end_positions - start_positions) * t).astype(int)

        ys = np.clip(current_positions[:, 0], 0, h - 1)
        xs = np.clip(current_positions[:, 1], 0, w - 1)

        canvas[ys, xs] = colors
        frames.append(Image.fromarray(canvas))

    newarr = canvas
    frames = [frames[0]] * 5 + frames + [frames[-1]] * 5
    return newarr, frames