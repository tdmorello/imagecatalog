"""A python class to create a contact sheet with labels and notes."""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

import PIL
from fpdf import FPDF
from PIL.Image import Image

PathLike = Union[str, os.PathLike]

logger = logging.getLogger(__name__)


class Catalog(FPDF):
    """Class to create a contact sheet from images, labels, and notes."""

    def __init__(self, rows=4, cols=4, title=None, author=None, keywords=None):
        """Initialize the Catalog class."""
        super().__init__()
        self.set_font("helvetica", size=10)
        self.rows = rows
        self.cols = cols
        self.set_title(title if title is not None else "[No Title]")
        self.set_author(author if author is not None else "[No Author]")
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
        self.set_font("helvetica", "B", 10)
        self.cell(0, 10, self.title, 0, 0, align="L")
        self.ln()

    def footer(self, txt=None):  # noqa: D102
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()} / {self.pages_count}", 0, 0, align="L")
        timestamp = datetime.now().strftime("%b %d, %Y at %H:%M:%S")
        self.cell(0, 10, f"Created {timestamp}", 0, 0, align="R")
        self.ln()

    def insert_table(
        self,
        images: List[Union[PathLike, Image]],
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
            labels = [self._get_image_name(im) for im in images]
        if notes is None:
            notes = [""] * len(images)

        rows, cols = self._verify_int(rows), self._verify_int(cols)
        w = self.epw / cols
        h = (self.eph - 10) / rows

        for i, (im, lb, nt) in enumerate(zip(images, labels, notes)):
            # check if building cell will trigger a new page
            if self.will_page_break(h):
                self.add_page()

            self._build_cell(im, lb, nt, w, h)
            # new line after last column of row
            if ((i + 1) % cols) == 0:
                self.ln()

    def _build_cell(self, image, label, note, w, h):
        """Builds a multicell within a multicell."""
        x_start, y_start = self.x, self.y
        values = {"label": label, "image": image, "note": note}

        # same font as label
        self.set_font("helvetica", style="B", size=8)
        h_lbl = self.font_size + 2
        # same font as note
        self.set_font("helvetica", style="I", size=8)
        h_nte = (
            len(self.multi_cell(w=w, txt=note, split_only=True)) * self.font_size + 1
        )
        h_img = h - h_lbl - h_nte

        for key, value in values.items():
            if key == "label":
                self._insert_label(w=w, h=h_lbl, txt=value)
            elif key == "image":
                self._insert_image(w=w, h=h_img, img=value)
            elif key == "note":
                self._insert_note(w=w, h=h_nte, txt=value)
            # handle extra key/values
            elif isinstance(value, str):
                ...
            else:
                raise ValueError(f"Cannot handle `{type(value)}` type")

        self.x, self.y = x_start, y_start
        self.multi_cell(w=w, h=h, txt="", border=1, ln=3)

    def _insert_label(self, w: int, h: int, txt: str) -> None:
        self.set_font("helvetica", style="B", size=8)
        self.multi_cell(w=w, h=h, txt=txt, align="C", border=1, ln=2)

    def _insert_image(self, w: int, h: int, img: Union[PathLike, Image]) -> None:
        image_name = self._get_image_name(img)
        try:
            self.image(img, x=self.x, y=self.y, w=w, h=h, alt_text=image_name)
            self.multi_cell(w=w, h=h, txt="", ln=2)
        except (PIL.UnidentifiedImageError, FileNotFoundError) as e:
            logger.warning(str(e))
            self.multi_cell(w=w, h=h, txt=image_name, align="C", ln=2)

    def _insert_note(self, w: int, h: int, txt: str) -> None:
        # color trigger keywords for labels?
        self.set_font("helvetica", style="I", size=8)
        self.multi_cell(w=w, txt=txt, ln=2)

    @staticmethod
    def _get_image_name(image: Union[PathLike, Image]) -> str:
        """Returns the filename for an image."""
        # REFACTOR
        try:
            return Path(image).name  # type: ignore
        except TypeError:
            pass
        try:
            return image.filename  # type: ignore
        except AttributeError:
            return ""

    @staticmethod
    def _verify_int(value) -> int:
        """Verifies that `value` is a whole number."""
        if value != int(value):
            raise ValueError("Value should be an integer")
        else:
            return int(value)

    def create(self, images, rows, cols, labels=None, notes=None):
        """Generate the PDF."""
        self.add_page()
        self.insert_table(images, labels, notes, rows, cols)


if __name__ == "__main__":
    catalog = Catalog()
    images = [Path(f"./images/image_{i:02}.jpg") for i in range(15)]
    notes = ["blue: DAPI, green: latexin, red: parvalbumin" for _ in images]
    catalog.title = "Title of the page [animal, section series]"
    catalog.create(images, rows=5, cols=3, labels=None, notes=notes)
    catalog.output("test.pdf")
