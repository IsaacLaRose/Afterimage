from PIL import Image
import numpy as np


def load_image(path):
    img = Image.open(path).convert("RGBA")
    background = Image.new("RGBA", img.size, (255, 255, 255, 255))
    background.paste(img, mask=img.split()[3])
    return np.array(background.convert("RGB"))

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