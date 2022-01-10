"""CLI entry point to package."""

import argparse
import csv
import fnmatch
from pathlib import Path
from typing import Dict, List, Tuple, Union

import imagecatalog

PathLike = Union[str, bytes, Path]


def filter_files(files: List, pattern: List[str]) -> List[str]:
    """Filter files list by pattern.

    Args:
        files: list of filename string(s)
        pattern: list of glob pattern(s)

    Returns:
        list of filenames filtered by glob pattern
    """
    sets = [set(fnmatch.filter(files, p)) for p in pattern]
    return sorted(list(set.intersection(*sets) if len(sets) > 1 else sets[0]))


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
    parser.add_argument(
        "output",
        help="path to output destination",
        metavar="FILE",
    )

    input_args = parser.add_mutually_exclusive_group(required=True)
    input_args.add_argument(
        "-i",
        "--input",
        help="path to image folder",
        metavar="FOLDER",
    )
    input_args.add_argument(
        "--csv",
        help=(
            "create catalog from csv file, formatted with headers `images,labels,notes`"
        ),
        metavar="CSVFILE",
    )

    parser.add_argument(
        "-f",
        "--filter",
        help=(
            "append a glob pattern to a set of file filters, note: filters return the "
            "intersection of all globs; filters are not applied to input from csv"
        ),
        action="append",
        metavar="PATTERN",
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
    pdf_args.add_argument(
        "--orientation",
        type=str,
        choices=["landscape", "portrait"],
        help=(
            f"landscape or portrait orientation, defaults to {DEFAULTS['orientation']}"
        ),
    )

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

    if Path(args.output).exists():
        raise FileExistsError("PDF file already exists.")

    if args.input:
        images = filter_files(
            [str(f) for f in Path(args.input).glob("*")],
            args.filter if args.filter else ["*"],
        )
        labels = None
        notes = None

    else:
        images, labels, notes = parse_csv(args.csv)

    if len(images) == 0:
        raise ValueError("No images found. Exiting.")

    # create the image catalog
    catalog = imagecatalog.Catalog(orientation=args.orientation)

    # # set metadata
    catalog.set_title(args.title if args.title is not None else "")
    catalog.set_author(args.author if args.author is not None else "")
    catalog.set_keywords(args.keywords if args.keywords is not None else "")

    catalog.add_page(orientation=args.orientation)
    catalog.build_table(images, labels, notes, args.rows, args.cols)
    catalog.output(args.output)

    if Path(args.output).exists():
        print(f"Image catalog written to {args.output}")


if __name__ == "__main__":
    main()
