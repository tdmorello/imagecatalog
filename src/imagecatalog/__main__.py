"""CLI entry point to package."""

import argparse
import csv
import fnmatch
from pathlib import Path
from typing import List, Union

import imagecatalog  # noqa:

PathLike = Union[str, bytes, Path]


def filter_files(files: List, pattern: List[str]):
    """Filter files list by pattern."""
    sets = [set(fnmatch.filter(files, p)) for p in pattern]
    return list(set.intersection(*sets)).sort()


def main():
    """CLI entrypoint."""
    DEFAULTS = {"rows": 4, "cols": 3}

    parser = argparse.ArgumentParser("catalog")
    parser.add_argument("output", help="path to output destination", metavar="FILE")

    input_args = parser.add_mutually_exclusive_group(required=True)
    input_args.add_argument(
        "-i", "--input", help="path to image folder", metavar="FOLDER"
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
        default=DEFAULTS["rows"],
        help=f"number of table rows per page, defaults to {DEFAULTS['rows']}",
    )
    pdf_args.add_argument(
        "-c",
        "--cols",
        type=int,
        default=DEFAULTS["cols"],
        help=f"number of table columns per page, defaults to {DEFAULTS['cols']}",
    )
    pdf_args.add_argument("--author", type=str, help="document author")
    pdf_args.add_argument("--title", type=str, help="document title")
    pdf_args.add_argument("--keywords", type=str, help="document keywords")

    other_args = parser.add_argument_group("other options")
    other_args.add_argument(
        "-v", "--verbose", action="store_true", help="verbose output"
    )
    other_args.add_argument("-q", "--quiet", action="store_true", help="quite output")

    # DEBUG
    # args = parser.parse_args()
    args = parser.parse_args(
        "--csv images/sample.csv --filter *.jpg output.pdf".split()
    )

    if args.input:
        images = args.input
        labels = None
        notes = None
        images = filter_files(images, args.filter if args.filter else "*")
    else:
        with open(args.csv) as fp:
            D = {"images": [], "labels": [], "notes": []}
            reader = csv.DictReader(fp)
            for row in reader:
                {D[key.lower()].append(val) for key, val in row.items()}
        # filters will not apply to csv input
        images, labels, notes = D["images"], D["labels"], D["notes"]

    # create the image catalog
    catalog = imagecatalog.Catalog()

    # # set metadata
    catalog.set_title(args.title if args.title is not None else "")
    catalog.set_author(args.author if args.author is not None else "")
    catalog.set_keywords(args.keywords if args.keywords is not None else "")

    catalog.create(images, args.rows, args.cols, labels=labels, notes=notes)
    catalog.output(args.output)


if __name__ == "__main__":
    main()
