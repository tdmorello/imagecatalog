.. code-block:: bash

   imagecatalog -i images/*.png -o example.pdf --title 'Image Catalog'


.. code-block:: bash

   imagecatalog   \
    -i images/*.png \
    -o example_landscape.pdf \
    --rows 2   \
    --cols 4   \
    --orientation landscape \
    --title 'Catalog with Landscape Layout' \

File paths and metadata can also be supplied from a csv file with headers "image", "label", "note"


.. code-block:: bash

   $ head -n5 sample.csv
   image,label,note
   images/image_00.png,Image 0,image 0 note
   images/image_01.png,Image 1,image 1 note
   images/image_02.png,Image 2,image 2 note
   images/image_03.png,Image 3,image 3 note


.. code-block:: bash

   imagecatalog --csv sample.csv --title 'Catalog from CSV' -o example_csv.pdf

Other features: apply image filters

.. code-block:: bash

   imagecatalog -i images/*.png -o catalog.pdf \
      --invert    \
      --grayscale \
      --autocontrast

Integrate with shell utilities

.. code-block:: bash

   find . -ctime 1d | xargs imagecatalog -o catalog.pdf -i

Use regular expressions to filter files

.. code-block:: bash

   imagecatalog -i images/*.png -o catalog.pdf --regex '.*(1|2).*'
