import numpy as np
from PIL import Image


def travel(flat, template, substance_sort, template_sort, n_frames=30):
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
    return frames

def band(flat, template, substance, substance_sort, template_sort, n_bands=30):


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
    return frames
