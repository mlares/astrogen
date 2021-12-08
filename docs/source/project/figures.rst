Figures
===============================

The figures to analyze the performance in the astronomy career
according to genders can be easily generated with provided code.

The code is located in `ASTROGEN/astrogen/dataviz <https://github.com/mlares/astrogen/tree/main/astrogen/dataviz>`_, and plots are saved into astrogen/figures.

Data to make these plots is in the file astrogen_DB_anonymized.db,
which must be placed in astrogen/data/redux, and can be downloaded
from dryad...


UNC
--------

.. code-block:: bash

   cd astrogen/astrogen/dataviz
   python visualize_unc



.. image:: ../../../figures/graduates_by_year.png
    :width: 400
    :align: center

.. image:: ../../../figures/time_to_graduation.png
    :width: 400
    :align: center

.. image:: ../../../figures/dropout_rates_normalized.png
    :width: 400
    :align: center




CONICET
--------

.. code-block:: bash

   cd astrogen/astrogen/dataviz
   python visualize_conicet

.. image:: ../../../figures/violins_conicet.png
    :width: 400
    :align: center

.. image:: ../../../figures/vio.png
    :width: 400
    :align: center



PUBLICATIONS
----------------

.. code-block:: bash

   cd astrogen/astrogen/dataviz
   python visualize_publications
