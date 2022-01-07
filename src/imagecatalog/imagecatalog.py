"""A python class to create a contact sheet with labels and notes."""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Union

import PIL
from fpdf import FPDF
from PIL.Image import Image

PathLike = Union[str, bytes, Path]

logger = logging.getLogger(__name__)


class Catalog(FPDF):
    """A class to create contact sheets from images, labels, and notes."""

    def __init__(self):
        """Initialize the Catalog class."""
        super().__init__()
        self.set_font("helvetica", size=10)

    def header(self):  # noqa: D102
        self.set_font("helvetica", "B", 10)
        self.cell(0, 10, self.title, 0, 0, align="L")
        self.ln()

    def footer(self):  # noqa: D102
        self.set_font("helvetica", "I", 8)
        # NOTE: is there a way to avoid hard-coding this?
        self.set_y(-15)
        self.cell(0, 10, f"Page {self.page_no()} / {self.pages_count}", 0, 0, align="L")
        timestamp = datetime.now().strftime("%b %d, %Y at %H:%M:%S")
        self.cell(0, 10, f"Created {timestamp}", 0, 0, align="R")
        self.ln()

    def build_table(
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
            rows (int, optional): number of rows per page. Defaults to 4.
            cols (int, optional): number of columns per page. Defaults to 3.

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
            # check if building a new cell will trigger a page break
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

        # REFACTOR is it possible to get font height without switching
        # same font as label
        self.set_font("helvetica", style="B", size=8)
        h_lbl = self.font_size + 2
        # REFACTOR see above refactor note
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
            # TODO handle extra key/values
            elif isinstance(value, str):
                ...
            else:
                raise ValueError(f"Cannot handle `{type(value)}` type")

        self.x, self.y = x_start, y_start
        self.multi_cell(w=w, h=h, border=1, ln=3)

    def _insert_label(self, w: int, h: int, txt: str) -> None:
        """Place a label at the specified location and move to the next cell."""
        self.set_font("helvetica", style="B", size=8)
        self.cell(w=w, h=h, txt=txt, align="C", border=1, ln=2)

    def _insert_image(self, w: int, h: int, img: Union[PathLike, Image]) -> None:
        """Place an image at the specified location and move to the next cell."""
        image_name = self._get_image_name(img)
        try:
            if not isinstance(img, Image):
                img = PIL.Image.open(img)

            im_w, im_h = self._dims_to_fit(img, (w, h))
            x = self.x + ((w - im_w) / 2)
            y = self.y + ((h - im_h) / 2)

            self.image(img, x=x, y=y, w=im_w, h=im_h, alt_text=image_name)
            self.multi_cell(w=w, h=h, ln=2)
        except (PIL.UnidentifiedImageError, FileNotFoundError) as e:
            logger.warning(str(e))
            self.cell(w=w, h=h, txt=image_name, align="C", ln=2)

    def _insert_note(self, w: int, h: int, txt: str) -> None:
        """Place a note at the specified location and move to the next cell."""
        # TODO color trigger keywords for labels?
        self.set_font("helvetica", style="I", size=8)
        self.multi_cell(w=w, txt=txt, ln=2)

    @staticmethod
    def _dims_to_fit(img: Image, size: Tuple[int, int]) -> Tuple[int, int]:
        """Return new dimensions to fit image in a space."""
        w, h = size
        im_w, im_h = img.width, img.height
        scale = (w / im_w) if (im_w / im_h) >= (w / h) else (h / im_h)

        return (int(im_w * scale), int(im_h * scale))

    @staticmethod
    def _get_image_name(image: Union[PathLike, Image]) -> str:
        """Returns the filename for an image."""
        try:
            return Path(image).name  # type: ignore
        except TypeError:
            pass
        try:
            return image.filename  # type: ignore
        except AttributeError:
            return "[image name unavailable]"

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
        self.build_table(images, labels, notes, rows, cols)


if __name__ == "__main__":
    # from imagecatalog import Catalog

    # Catalog inherits from FPDF
    # see https://github.com/PyFPDF/fpdf2 for more methods
    catalog = Catalog()
    # optionally add a title
    catalog.set_title("Image Catalog")
    # grab a set of existing images from a local directory
    images = [f"images/image_{i:02}.jpg" for i in range(12)]
    # optionally add labels (defaults to filename)
    labels = [f"Image {i}" for i in range(len(images))]
    # optionally add notes
    notes = [f"image {i} note" for i in range(len(images))]
    # generate the pdf
    catalog.create(images, labels=labels, notes=notes, rows=4, cols=3)
    # save
    catalog.output("example.pdf")
