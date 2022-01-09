"""Test suite."""

import subprocess
import sys

import pytest
from PIL import Image

from imagecatalog import Catalog, create_catalog


@pytest.fixture
def sample_image_dir(tmp_path):
    # create sample data
    for i in range(12):
        fpath = tmp_path / f"image_{i:02}.jpg"
        image = Image.new("RGB", (200, 200), "gray")
        image.save(fpath)

    return tmp_path


def test_cli_from_files(sample_image_dir):

    # image_dir = sample_image_dir
    # output = sample_image_dir / "output.pdf"

    # cmd = f"{sys.executable} -m imagecatalog -i {str(image_dir)} -f '*.jpg' --rows 4 --cols 3 {str(output)}"
    # res = subprocess.run(cmd.split(), capture_output=True)

    # assert output.exists()
    ...


def test_cli_from_csv():
    ...


def test_catalog_from_files(sample_image_dir):
    """Catalog can be created from files."""

    # create sample data
    image_dir = sample_image_dir

    catalog = Catalog()
    catalog.set_title("test catalog")
    images = [image_dir / f"image_{i:02}.jpg" for i in range(12)]
    labels = [f"Image {i}" for i in range(len(images))]
    notes = [f"image {i} note" for i in range(len(images))]
    catalog.add_page()
    catalog.build_table(images, labels, notes, 4, 3)
    catalog.output(image_dir / "catalog.pdf")

    # TODO read back pdf, search text fields, count number of images


def test_catalog_from_memory(tmp_path):
    """Catalog class creates PDF."""
    catalog = Catalog()
    catalog.set_title("test catalog")
    images = [f"images/image_{i:02}.jpg" for i in range(12)]
    labels = [f"Image {i}" for i in range(len(images))]
    notes = [f"image {i} note" for i in range(len(images))]
    catalog.add_page()
    catalog.build_table(images, labels, notes, 4, 3)
    catalog.output(tmp_path / "catalog.pdf")

    # TODO read back pdf, search text fields, count number of images


def test_create_catalog_func():
    """Convenience function creates PDF."""
    ...
