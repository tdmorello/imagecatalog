"""Script to create a set of images."""

from pathlib import Path
from random import randrange
from typing import List, Tuple, Union

from PIL import Image, ImageDraw

PathLike = Union[str, bytes, Path]


def make_random_image(im_size, single_color):
    def make_random_hex():
        return f"#{randrange(0x1000000):06x}"

    def make_random_pixel():
        return (randrange(0, 256), randrange(0, 256), randrange(0, 256))

    if single_color:
        im = Image.new("RGB", im_size, make_random_hex())
    else:
        data = [make_random_pixel() for _ in range(im_size[0] * im_size[1])]
        im = Image.new("RGB", im_size)
        im.putdata(data)

    return im


def make_sample_images(n, im_size=(128, 128), single_color=True):
    return [make_random_image(im_size, single_color) for _ in range(n)]


def make_sample_files(
    dir, n, ext=".jpg", im_size=(128, 128), single_color=True, namestamp=True
):
    images = [im for im in make_sample_images(n, im_size, single_color)]

    def save_image(fpath, im):
        if namestamp:
            draw = ImageDraw.Draw(im)
            draw.text((10, 10), Path(fpath).name)
        im.save(fpath)
        return fpath

    return [
        save_image(Path(dir) / f"image_{i:02}{ext}", im) for i, im in enumerate(images)
    ]


if __name__ == "__main__":
    images = make_sample_files("images", 15)
    with open("images/sample.csv", "w") as fp:
        fp.write("image,label,note\n")
        for i, fpath in enumerate(images):
            fp.write(f"{fpath},Image {i},image {i} note\n")
