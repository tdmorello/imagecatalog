"""Create a contact sheet PDF with labels and notes.

Todo:
    * todo1

"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Union

import PIL
from fpdf import FPDF
from PIL.Image import Image

PathLike = Union[str, bytes, Path]

logger = logging.getLogger(__name__)


def create_catalog(
    fname: PathLike,
    images: List[Union[PathLike, Image]],
    labels: Optional[List[str]] = None,
    notes: Optional[List[str]] = None,
    orientation: str = "portrait",
    rows: int = 4,
    cols: int = 3,
):
    """Convenience method to generate an image catalog and save as PDF.

    Args:
        fname: pdf output filename
        images: list of images
        labels: list of labels for images,
            should be same length as ``images``, displayed above image. If
            `None`, labels will be file names (if available). Defaults
            to `None`.
        notes: list of notes for images,
            should be same length as ``images``, displayed below image. Defaults
            to `None`.
        orientation: page orientation, possible values are "portrait" (can be
                abbreviated "P") or "landscape" (can be abbreviated "L"). Default
                to "portrait".
        rows: number of rows per page
        cols: number of columns per page
    """
    catalog = Catalog(orientation)
    catalog.add_page()
    catalog.build_table(images, labels, notes, rows, cols)
    catalog.output(fname)


class Catalog(FPDF):
    """A class to create contact sheets from images, labels, and notes.

    Example:
        >>> # generate sample data
        >>> from PIL import Image
        >>> images = [Image.new("RGB", (200, 200), "gray") for _ in range(9)]
        >>> labels = [f"Image {i}" for i in range(9)]
        >>> notes = [f"image {i} note" for i in range(9)]
        >>> from imagecatalog import Catalog
        >>> catalog = Catalog()
        >>> # optionally add a title
        >>> catalog.set_title("Image Catalog")
        >>> catalog.add_page()
        >>> catalog.build_table(images, labels, notes, rows=4, cols=3)
        >>> catalog.output("image_catalog.pdf")
    """

    def __init__(
        self,
        orientation: str = "portrait",
        unit: str = "mm",
        format: str = "A4",
        **kwargs,
    ):  # noqa: D107
        """Instantiate an FPDF object.

        Args:
            orientation: page orientation, possible values are "portrait" (can be
                abbreviated "P") or "landscape" (can be abbreviated "L"). Default
                to "portrait".
            unit: possible values are "pt", "mm", "cm", "in", or a number
            format: possible values are "a3", "a4", "a5", "letter", "legal" or a tuple
                (width, height) expressed in the given unit. Default to "a4".
            **kwargs: keyword arguments passed to `fpdf.FPDF`
        """
        super().__init__(orientation=orientation, unit=unit, format=format, **kwargs)
        self.set_font("helvetica", size=10)

    def header(self):  # noqa: D102
        try:
            self.set_font("helvetica", "B", 10)
            self.cell(0, 10, self.title, 0, 0, align="L")
        except AttributeError:
            pass
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
            images: list of images
            labels: list of labels for images,
                should be same length as ``images``, displayed above image. If
                `None`, labels will be file names (if available). Defaults to `None`.
            notes: list of notes for images,
                should be same length as ``images``, displayed below image. Defaults
                to `None`.
            rows: number of rows per page. Defaults to `4`.
            cols: number of columns per page. Defaults to `3`.

        Raises:
            ValueError: if ``images`` and ``labels`` (if supplied) and notes (if
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
        x_start, y_start = self.x, self.y
        values = {"label": label, "image": image, "note": note}

        # REFACTOR is it possible to get font height without switching
        self.set_font("helvetica", style="B", size=8)  # same font as label
        h_lbl = self.font_size + 2
        # REFACTOR see above refactor note
        self.set_font("helvetica", style="I", size=8)  # same font as note
        h_nte = (
            len(self.multi_cell(w=w, txt=note, split_only=True)) * self.font_size + 1
        )
        h_img = h - h_lbl - h_nte

        for key, value in values.items():
            if key == "label":
                self._insert_label(w=w, h=h_lbl, txt=value)
            elif key == "image":
                self._insert_image(w=w, h=h_img, img=value)
            else:
                self._insert_note(w=w, h=h_nte, txt=value)
            # TODO handle extra key/values
            # elif isinstance(value, str):

        self.x, self.y = x_start, y_start
        self.multi_cell(w=w, h=h, border=1, ln=3)

    def _insert_label(self, w: int, h: int, txt: str) -> None:
        self.set_font("helvetica", style="B", size=8)
        self.cell(w=w, h=h, txt=txt, align="C", border=1, ln=2)

    def _insert_image(self, w: int, h: int, img: Union[PathLike, Image]) -> None:
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
        # TODO color trigger keywords for labels?
        self.set_font("helvetica", style="I", size=8)
        self.multi_cell(w=w, txt=txt, ln=2)

    @staticmethod
    def _dims_to_fit(img: Image, size: Tuple[int, int]) -> Tuple[int, int]:
        w, h = size
        im_w, im_h = img.width, img.height
        scale = (w / im_w) if (im_w / im_h) >= (w / h) else (h / im_h)

        return (int(im_w * scale), int(im_h * scale))

    @staticmethod
    def _get_image_name(image: Union[PathLike, Image]) -> str:
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
        if value != int(value):
            raise ValueError("Value should be an integer")
        else:
            return int(value)
