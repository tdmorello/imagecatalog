"""CLI entry point to package."""

import argparse
import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple, Union

import imagecatalog

PathLike = Union[str, bytes, Path]


def filter_files(files: List, pattern: str) -> List[str]:
    """Filter files list by regex pattern.

    Args:
        files: list of filename string(s)
        pattern: list of glob pattern(s)

    Returns:
        filtered list of filenames
    """
    r = re.compile(pattern)
    return list(filter(r.match, files))


def parse_csv(csvfile: str) -> Tuple[List[str], List[str], List[str]]:
    """Open and parse csv.

    Args:
        csvfile: path to csvfile

    Returns:
        a tuple of lists for images, labels, and notes
    """
    with open(csvfile) as fp:
        D: Dict[str, list] = {"image": [], "label": [], "note": []}
        reader = csv.DictReader(fp)
        for row in reader:
            for key, val in row.items():
                D[key.lower()].append(val)
    return D["image"], D["label"], D["note"]


def main():
    """CLI entrypoint.

    Raises:
        ValueError: no images in image list
        FileExistsError: output file already exists
    """
    DEFAULTS = {"rows": 4, "cols": 3, "orientation": "portrait"}

    parser = argparse.ArgumentParser("imagecatalog")

    input_args = parser.add_mutually_exclusive_group(required=True)
    input_args.add_argument(
        "-i",
        "--input",
        help="image file(s)",
        nargs="+",
        metavar="IMAGE",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="pdf file",
        metavar="PDF",
        required=True,
    )
    input_args.add_argument(
        "-s",
        "--csv",
        help="create catalog from csv file with headers 'images,labels,notes'",
        metavar="CSV",
    )

    parser.add_argument(
        "-e",
        "--regex",
        help="filter file list by regex pattern",
        metavar="REGEX",
    )

    pdf_args = parser.add_argument_group("pdf options")
    pdf_args.add_argument(
        "-r",
        "--rows",
        type=int,
        help=f"number of table rows per page, defaults to {DEFAULTS['rows']}",
    )
    pdf_args.add_argument(
        "-c",
        "--cols",
        type=int,
        help=f"number of table columns per page, defaults to {DEFAULTS['cols']}",
    )
    pdf_args.add_argument(
        "--orientation",
        type=str,
        choices=["landscape", "portrait"],
        help=(
            f"landscape or portrait orientation, defaults to {DEFAULTS['orientation']}"
        ),
    )
    pdf_args.add_argument(
        "--author",
        type=str,
        help="document author",
    )
    pdf_args.add_argument(
        "--title",
        type=str,
        help="document title",
    )
    pdf_args.add_argument(
        "--keywords",
        type=str,
        help="document keywords",
    )

    img_args = parser.add_argument_group("image options")
    img_args.add_argument(
        "--autocontrast",
        help="apply autocontrast to images",
        action="store_true",
        default=False,
    )
    img_args.add_argument(
        "--grayscale",
        help="convert color images to grayscale",
        action="store_true",
        default=False,
    )
    img_args.add_argument(
        "--invert",
        help="invert image colors",
        action="store_true",
        default=False,
    )
    # TODO split channels feature
    # img_args.add_argument(
    #     "--channel",
    #     help="if multi-channel image, only display this channel",
    #     metavar="CHAN",
    # )

    other_args = parser.add_argument_group("other options")
    other_args.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="verbose output",
    )
    other_args.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="quite output",
    )
    other_args.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="force overwrite output",
    )

    args = parser.parse_args()

    if args.orientation in [None, "portrait"]:
        args.orientation = "portrait"
        args.rows = args.rows or DEFAULTS["rows"]
        args.cols = args.cols or DEFAULTS["cols"]
    else:
        args.orientation = args.orientation
        # if unassigned for landscape orientation, flip default rows and cols
        args.rows = args.rows or DEFAULTS["cols"]
        args.cols = args.cols or DEFAULTS["rows"]

    if Path(args.output).exists() and not args.force:
        raise FileExistsError("PDF file already exists.")

    if args.input:
        images = filter_files(args.input, args.regex or ".*")
        labels = None
        notes = None

    else:
        images, labels, notes = parse_csv(args.csv)

    # create the image catalog
    catalog = imagecatalog.Catalog(orientation=args.orientation)

    # set metadata
    catalog.set_title(args.title if args.title is not None else "")
    catalog.set_author(args.author if args.author is not None else "")
    catalog.set_keywords(args.keywords if args.keywords is not None else "")

    catalog.add_page()
    catalog.build_table(
        images,
        labels=labels,
        notes=notes,
        rows=args.rows,
        cols=args.cols,
        autocontrast=args.autocontrast,
        grayscale=args.grayscale,
        invert=args.invert,
    )
    catalog.output(args.output)

    if Path(args.output).exists():
        print(f"Image catalog written to {args.output}")


if __name__ == "__main__":
    main()
