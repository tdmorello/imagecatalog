# imagecatalog

Create a PDF contact sheet from a list of files.

## Installation

Install from PyPI

```bash
pip install imagecatalog
```

or get latest dev version from GitHub.

```bash
pip install git+https://github.com/tdmorello/imagecatalog.git
```

---

### Command line usage

```bash
imagecatalog -h
```

```bash
imagecatalog -i images/ -f '*.jpg' --title 'Image Catalog' example.pdf
```

[PDF output](https://github.com/tdmorello/imagecatalog/blob/main/resources/example.pdf)

File paths and metadata can also be supplied from a csv file with headers "image", "label", "note"

```bash
$ head -n5 sample.csv
image,label,note
images/image_00.jpg,Image 0,image 0 note
images/image_01.jpg,Image 1,image 1 note
images/image_02.jpg,Image 2,image 2 note
images/image_03.jpg,Image 3,image 3 note
```

```bash
imagecatalog --csv sample.csv --title 'Image Catalog from CSV' example_csv.pdf
```

[PDF output](https://github.com/tdmorello/imagecatalog/blob/main/resources/example.pdf)

---

### Script usage

```python
from imagecatalog import Catalog

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
notes = [f"note for image {i}" for i in range(len(images))]

# generate the pdf
catalog.create(images, labels=labels, notes=notes, rows=4, cols=3)

# save
catalog.output("example.pdf")
```

---

## Contributions

`imagecatalog` uses `poetry` for building and package management. Pull requests are welcome.
