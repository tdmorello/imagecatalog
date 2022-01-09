"""Test suite."""

from pathlib import Path

from PIL import Image

from imagecatalog import Catalog, create_catalog


def test_cli_from_files():
    ...


def test_cli_from_csv():
    ...


def test_catalog_from_files(tmp_path):
    """Catalog can be created from files."""

    # create sample data
    for i in range(12):
        fpath = tmp_path / f"image_{i:02}.jpg"
        image = Image.new("RGB", (200, 200), "gray")
        image.save(fpath)

    catalog = Catalog()
    catalog.set_title("test catalog")
    images = [tmp_path / f"image_{i:02}.jpg" for i in range(12)]
    labels = [f"Image {i}" for i in range(len(images))]
    notes = [f"image {i} note" for i in range(len(images))]
    catalog.add_page()
    catalog.build_table(images, labels, notes, 4, 3)
    catalog.output(tmp_path / "catalog.pdf")

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
