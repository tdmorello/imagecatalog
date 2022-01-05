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
        self.set_font("helvetica", size=10)
        self.rows = rows
        self.cols = cols
        self.set_title(title)
        self.set_author(author)
        self.set_keywords(keywords)

    @property
    def rows(self) -> int:
        """Number of rows per page."""
        return self._rows

    @rows.setter
    def rows(self, value) -> None:
        self._rows = self._verify_int(value)

    @property
    def cols(self) -> int:
        """Number of columns per page."""
        return self._cols

    @cols.setter
    def cols(self, value) -> None:
        self._cols = self._verify_int(value)

    def header(self, txt=None):  # noqa: D102
        ...

    def footer(self, txt=None):  # noqa: D102
        ...

    def insert_table(
        self,
        images: List[Union[PathLike, PIL.Image.Image]],
        labels: Optional[List[str]] = None,
        notes: Optional[List[str]] = None,
        rows: int = 4,
        cols: int = 3,
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
            raise ValueError("`images`, `labels`, and `notes` must be the same length.")

        if labels is None:
            labels = self._get_labels_from_images(images)
        if notes is None:
            notes = [""] * len(images)

        rows, cols = self._verify_int(rows), self._verify_int(cols)
        w = self.epw / cols
        h = self.eph / rows

        for i, (im, lb, nt) in enumerate(zip(images, labels, notes)):
            # check if building cell will trigger a new page
            if self.will_page_break(h):
                self.add_page()

            self._build_cell(im, lb, nt, w, h)
            # `(i + 1) % cols` is 0 on the last column of the row
            if ((i + 1) % cols) == 0:
                self.ln()

    def _build_cell(self, image, label, note, w, h):
        """Builds a multicell within a multicell."""
        x_start, y_start = self.x, self.y
        values = {"label": label, "image": image, "note": note}
        for key, item in values.items():
            inner_w = w
            inner_h = h / len(values)

            # handle data categories separately
            if key == "label":
                self.multi_cell(w=inner_w, h=inner_h, txt=f"{key}: {item}", ln=2)
            elif key == "image":
                self.multi_cell(w=inner_w, h=inner_h, txt=f"{key}: {item}", ln=2)
            elif key == "note":
                self.multi_cell(w=inner_w, h=inner_h, txt=f"{key}: {item}", ln=2)
            else:
                self.multi_cell(w=inner_w, h=inner_h, txt=f"{key}: {item}", ln=2)

        self.x, self.y = x_start, y_start
        self.multi_cell(w=w, h=h, txt="", border=1, ln=3)

    @staticmethod
    def _get_labels_from_images(images) -> List[str]:
        """Return labels as strings from image filename when possible."""

        def get_label(fname):
            try:
                return Path(fname).name
            except TypeError:
                return ""

        return [get_label(im) for im in images]

    @staticmethod
    def _verify_int(value) -> int:
        """Verify that `value` is a whole number."""
        if value != int(value):
            raise ValueError("Value should be an integer.")
        else:
            return int(value)

    def create(self, images, labels, notes, rows, cols):
        """Generate the PDF."""
        self.add_page()
        self.insert_table(images, labels, notes, rows, cols)


if __name__ == "__main__":
    catalog = Catalog()
    images = labels = [f"image_{i}.jpg" for i in range(12)]
    notes = [f"note for {im}" for im in images]
    catalog.create(images, labels, notes, rows=3, cols=4)
    catalog.output("test.pdf")
