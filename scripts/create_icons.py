"""Script to create a set of images."""

from pathlib import Path

from PIL import Image, ImageDraw


def create_sample_image(output_path):
    """Create a set of images for testing."""
    output_path = Path(output_path)
    image = Image.new("RGB", (200, 200), "green")
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), output_path.name)
    image.save(output_path)


if __name__ == "__main__":
    with open("images/sample.csv", "w") as fp:
        fp.write("image,label,note\n")
        for i in range(12):
            fpath = f"images/image_{i:02}.jpg"
            create_sample_image(fpath)
            fp.write(f"{fpath},Image {i},image {i} note\n")
