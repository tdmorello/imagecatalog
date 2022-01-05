"""CLI entry point to package."""

import argparse

import imagecatalog


def filter_files(pattern):
    """Filter files list by pattern."""
    ...


def main():
    """CLI entrypoint."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "output", help="path to output destination", metavar="FILE"
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-i", "--input", help="path to image folder", metavar="FOLDER"
    )
    input_group.add_argument(
        "--from-csv", help="create catalog from csv file", metavar="CSVFILE"
    )

    parser.add_argument(
        "-f",
        "--filter",
        help="filter image files with a pattern",
        metavar="PATTERN",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="verbose output"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="quite output"
    )

    group = parser.add_argument_group("pdf options")
    group.add_argument("-r", "--rows", help="number of table rows per page")
    group.add_argument("-c", "--cols", help="number of table columns per page")
    group.add_argument("--author", help="document author")
    group.add_argument("--title", help="document title")
    group.add_argument("--keywords", help="document keywords")

    args = parser.parse_args("-i file.txt output.pdf".split())

    # create the image catalog
    catalog = imagecatalog.Catalog()

    # set metadata
    catalog.set_title(args.title)
    catalog.set_author(args.author)
    catalog.set_keywords(args.keywords)

    catalog.create()
    catalog.output(args.output)


if __name__ == "__main__":
    main()
