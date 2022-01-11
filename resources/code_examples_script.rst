.. code-block::python

    from imagecatalog import Catalog

    # Catalog inherits from FPDF
    # see https://github.com/PyFPDF/fpdf2 for more methods
    catalog = Catalog()

    # optionally add a title
    catalog.set_title("Image Catalog")

    # grab a set of existing images from a local directory
    images = [f"images/image_{i:02}.png" for i in range(12)]

    # optionally add labels (defaults to filenames)
    labels = [f"Image {i}" for i in range(len(images))]

    # optionally add notes
    notes = [f"note for image {i}" for i in range(len(images))]

    # generate the pdf
    catalog.add_page()
    catalog.build_table(images, labels, notes, rows=4, cols=3)

    # save
    catalog.output("example.pdf")
