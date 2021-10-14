pipeline module
======================

This module contains the steps fot the data reduction pipeline


The steps are 

- S01: read base table (AAA)
- S02: add institutes and cic data
- S03: add metadata for authors
- S04: add publications dat

S01: read base table
~~~~~~~~~~~~~~~~~~~~

S02: add institutes and cic data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In these steps the following columns are added:
- cic
- docencia
- area
- orcid
- use_orcid

The steps are contained in the following functions:
- S02_add_OAC_data
- S02_add_IATE_data
- S02_add_UNLP_data
- S02_add_ICATE_data
- S02_add_GAE_data
- S02_add_CIC_data


S03: add metadata for authors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- S03_add_gender
- S03_add_age
- S03_clean_and_sor

S04: add publications dat
~~~~~~~~~~~~~~~~~~~~~~~~~~

- S04_pub_get_ads_entries
- S04_pub_get_orcids
- S04_pub_journal_index
- S04_pub_clean_papers
- S04_make_pages
- S04_pub_value_added

API documentation:

.. automodule:: pipeline
    :members:
    :undoc-members:
    :show-inheritance:
