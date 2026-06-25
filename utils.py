from PIL import Image
import numpy as np


def load_image(path):
    img = Image.open(path).convert("RGB")
    return np.array(img)

def save_image(array, path):
    if '.' not in path:
        path += '.png'
    img = Image.fromarray(array.astype(np.uint8))
    img.save(path)

def resize_image(array, target_shape):
    h, w = target_shape[:2]
    img = Image.fromarray(array.astype(np.uint8))
    img = img.resize((w, h), Image.LANCZOS)
    return np.array(img)