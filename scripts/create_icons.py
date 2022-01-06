"""Script to create a set of images."""

from pathlib import Path

from PIL import Image, ImageDraw


def text(output_path):
    """Create a set of images for testing purposes."""
    output_path = Path(output_path)
    image = Image.new("RGB", (200, 200), "green")
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), output_path.name)
    image.save(output_path)


if __name__ == "__main__":
    fnames = [Path(f"image_{i:02}.jpg") for i in range(1, 21)]
    for name in fnames:
        text(Path("./images") / name)
