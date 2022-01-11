"""Test suite."""

import inspect
import subprocess
import sys
from itertools import islice
from pathlib import Path
from random import randrange
from typing import List, Tuple

import PIL
import pytest
from PIL.Image import Image

from imagecatalog import Catalog, create_catalog
from imagecatalog.__main__ import filter_files, main


def make_random_image(im_size: Tuple[int, int]) -> Image:
    """Makes a random image of specified size."""

    def make_random_pixel():
        return (randrange(0, 256), randrange(0, 256), randrange(0, 256))

    data = [make_random_pixel() for _ in range(im_size[0] * im_size[1])]
    im = PIL.Image.new("RGB", im_size)
    im.putdata(data)
    return im


def make_sample_images(n: int, im_size: Tuple[int, int] = (128, 128)) -> List[Image]:
    return [make_random_image(im_size) for _ in range(n)]


def make_sample_files(
    dir, n: int, im_size: Tuple[int, int] = (128, 128), ext: str = ".jpg"
) -> List[str]:
    images = [im for im in make_sample_images(n, im_size)]

    def save_image(fpath, im):
        im.save(fpath)
        return fpath

    return [save_image(dir / f"image_{i:02}{ext}", im) for i, im in enumerate(images)]


def test_catalog_from_memory(tmp_path):
    """Catalog creates PDF from images in memory."""
    catalog = Catalog()
    catalog.set_title("test catalog")
    images = make_sample_images(5)
    labels = [f"Image {i}" for i in range(len(images))]
    notes = [f"image {i} note" for i in range(len(images))]
    catalog.add_page()
    catalog.build_table(images, labels, notes, 2, 2)

    # test that images ran onto next page
    assert catalog.pages_count == 2

    catalog.output(tmp_path / "catalog.pdf")
    assert (tmp_path / "catalog.pdf").exists()
    # TODO read back pdf, search text fields, count number of images


def test_catalog_from_files(tmp_path):
    """Catalog creates PDF from image files."""
    catalog = Catalog()
    catalog.set_title("test catalog")
    images = make_sample_files(tmp_path, 1)
    for im in images:
        assert im.exists()
    catalog.add_page()
    catalog.build_table(images)
    catalog.output(tmp_path / "catalog.pdf")
    assert (tmp_path / "catalog.pdf").exists()


def test_catalog_file_not_found(tmp_path):
    catalog = Catalog()
    catalog.set_title("test catalog")
    images = [tmp_path / "nothing.jpg"]
    catalog.add_page()
    catalog.build_table(images)
    pdffile = tmp_path / "catalog.pdf"
    catalog.output(pdffile)
    assert pdffile.exists()


@pytest.mark.parametrize(
    "rows,is_error",
    [(1, False), (1.0, False), (1.1, True)],
    ids=["int_no_error", "float_no_error", "float_error"],
)
def test_catalog_checks_integer(rows, is_error):
    catalog = Catalog()
    images = make_sample_images(1)
    catalog.add_page()
    if is_error:
        with pytest.raises(ValueError):
            catalog.build_table(images, rows=rows)
    else:
        catalog.build_table(images, rows=rows)


def test_catalog_checks_input_lengths():
    """Catalog class creates PDF."""
    catalog = Catalog()
    catalog.set_title("test catalog")
    images = make_sample_images(1)
    labels = [f"Image {i}" for i in range(2)]
    catalog.add_page()

    with pytest.raises(ValueError):
        catalog.build_table(images, labels)


def test_create_catalog(tmp_path):
    """Convenience function creates PDF."""
    images = make_sample_images(9)
    create_catalog(tmp_path / "catalog.pdf", images)


def test_create_catalog_has_all_args():
    func_sig = inspect.signature(create_catalog)
    method_sig = inspect.signature(Catalog.build_table)
    # ignore first value which is 'self'
    for value in islice(method_sig.parameters.values(), 1, None):
        assert value in func_sig.parameters.values()


# TODO keep the option for multiple regex filters?
files_list = [
    (["file.jpg", "file.png"], ".*", ["file.jpg", "file.png"]),
    (["file.jpg", "file.png"], r".*\.jpg", ["file.jpg"]),
]


@pytest.mark.parametrize(
    "files,pattern,expected",
    files_list,
)
def test_filter_files(files, pattern, expected):
    """Files are properly filtered by glob patterns."""
    assert filter_files(files, pattern) == expected


def test_cli_entrypoint(tmp_path):
    output = tmp_path / "output.pdf"
    files = map(str, make_sample_files(tmp_path, 1))
    cmd = f"{sys.executable} -m imagecatalog -i {' '.join(files)} -o {output}"
    subprocess.run(cmd.split())

    assert output.exists()


def test_cli_from_files(monkeypatch, tmp_path):
    output = tmp_path / "output.pdf"
    files = map(str, make_sample_files(tmp_path, 1))
    argv = f"imagecatalog -i {' '.join(files)} -o {str(output)}".split()
    monkeypatch.setattr("sys.argv", argv)
    main()
    assert output.exists()


def test_cli_from_csv(monkeypatch, tmp_path):
    csvfile = tmp_path / "sample.csv"
    with open(csvfile, "w") as fp:
        fp.write("image,label,note\n")
        images = make_sample_files(tmp_path, 1)
        for i, im in enumerate(images):
            assert Path(im).exists()
            fp.write(f"{im},,")
    output = tmp_path / "catalog.pdf"
    argv = f"imagecatalog --csv {str(csvfile)} -o {str(output)}".split()
    monkeypatch.setattr("sys.argv", argv)
    main()
    assert output.exists()


def test_cli_options(monkeypatch, tmp_path):
    output = tmp_path / "output.pdf"
    files = map(str, make_sample_files(tmp_path, 1))
    argv = (
        f"imagecatalog -i {' '.join(files)} "
        "--orientation landscape "
        "--autocontrast "
        "--invert "
        "--grayscale "
        f"-o {output}".split()
    )
    monkeypatch.setattr("sys.argv", argv)
    main()
    assert output.exists()


def test_cli_output_already_exists(monkeypatch, tmp_path):
    output = tmp_path / "catalog.pdf"
    output.touch()
    argv = f"imagecatalog -i {tmp_path} -o {output}"
    monkeypatch.setattr("sys.argv", argv.split())
    with pytest.raises(FileExistsError):
        main()
