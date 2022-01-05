"""A python class to create a contact sheet with labels and notes."""

import os
from pathlib import Path
from typing import List, Optional, Union

import PIL.Image
from fpdf import FPDF

PathLike = Union[str, bytes, os.PathLike]


class Catalog(FPDF):
    """Class to create a contact sheet from images, labels, and notes."""

    def __init__(self, rows=4, cols=4, title=None, author=None, keywords=None):
        """Initialize the Catalog class."""
        super().__init__()

        self.rows = rows
        self.cols = cols

        self.title = title
        self.author = author
        self.keywords = keywords

    def header(self):  # noqa: D102
        ...

    def footer(self):  # noqa: D102
        ...

    def insert_table(
        self,
        images: List[Union[PathLike, PIL.Image.Image]],
        labels: Optional[List[str]] = None,
        notes: Optional[List[str]] = None,
    ):
        """Insert the catalog table into the pdf.

        Args:
            images (List[Union[PathLike, Image]]): list of images
            labels (Optional[List[str]], optional): list of labels for images,
                should be same length as `images`, displayed above image. If
                `None`, labels will be file names (if available).
                Defaults to None.
            notes (Optional[List[str]], optional): list of notes for images,
                should be same length as `images`, displayed below image.
                Defaults to None.

        Raises:
            ValueError: if images and labels (if supplied) and notes (if
            supplied) are not equal lengths.
        """
        # check that supplied arguments are same length
        if (labels is not None and len(labels) != len(images)) or (
            notes is not None and len(notes) != len(images)
        ):
            raise ValueError(
                "`images`, `labels`, and `notes` must be the same length."
            )

        if labels is None:
            labels = self._get_labels_from_images(images)
        if notes is None:
            notes = [""] * len(images)

        cells = [  # noqa
            self._build_cell(im, lb, nt)
            for im, lb, nt in zip(images, labels, notes)
        ]

    @staticmethod
    def _get_labels_from_images(images) -> List[str]:
        def get_label(fname):
            try:
                return Path(fname).name
            except TypeError:
                return ""

        return [get_label(im) for im in images]

    def _build_cell(self, image, label, note):
        # set of instructions given a starting coordinate?
        # alt. build row by row
        ...

    def create(self):
        """Generate the PDF."""
        self.add_page()
        self.insert_table()
