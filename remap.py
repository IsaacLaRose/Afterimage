import numpy as np

from utils import resize_image



def remap_pixels(substance,template):
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

    #actually remapping time
    for i in range(len(flat2)):
        newarr[template_sort[i]] = flat[substance_sort[i]]

    #unflatten
    newarr = newarr.reshape(template.shape)

    return newarr