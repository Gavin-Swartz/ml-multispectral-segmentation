import os
import rasterio
from pathlib import Path
from PIL import Image
import numpy as np


def get_rgb(red, green, blue):
    rgb = np.stack([
        red,
        green,
        blue
    ], axis=-1)

    # Normalize
    rgb = rgb.astype(float)
    rgb -= rgb.min()
    rgb /= rgb.max()

    # To uint8
    rgb = (rgb * 255).astype(np.uint8)

    return rgb


def main():
    data_dir = 'data/'
    for file in os.listdir(data_dir):
        file = os.path.join(data_dir, file)
        with rasterio.open(file) as tif:
            bands = tif.read()

        # RGB image
        red = bands[3]
        green = bands[2]
        blue = bands[1]
        rgb = get_rgb(red, green, blue)

        output_file = os.path.join(data_dir, Path(file).stem) + '.png'
        im = Image.fromarray(rgb)
        im.save(output_file)

        # Masks
        # TODO

        print(file, 'processed')


if __name__ == "__main__":
    main()