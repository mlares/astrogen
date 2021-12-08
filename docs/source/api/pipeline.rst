pipeline module
======================

The data reduction pipeline is implemented through a bonobo pipeline,
within an ETL (extract-transform-load) model, with the following steps:

+-----------------------------+----------------------------------------------------+
| action                      | routine                                            |
+=============================+====================================================+
| read table from AAA         |    - :meth:`pipeline.S01_read_aaa_table`           |
+-----------------------------+----------------------------------------------------+
| merge with tables from      |  - :meth:`pipeline.S02_add_OAC_data`               |
| institutes                  |  - :meth:`pipeline.S02_add_IATE_data`              |
|                             |  - :meth:`pipeline.S02_add_IALP_data`              |
|                             |  - :meth:`pipeline.S02_add_ICATE_data`             |
|                             |  - :meth:`pipeline.S02_add_GAE_data`               |
|                             |                                                    |
+-----------------------------+----------------------------------------------------+
| merge with data from CONICET| - :meth:`pipeline.S02_add_CONICET_data`            |
+-----------------------------+----------------------------------------------------+
| add gender                  | - :meth:`pipeline.S03_add_gender`                  |
+-----------------------------+----------------------------------------------------+
| add age                     | - :meth:`pipeline.S03_add_age`                     |
+-----------------------------+----------------------------------------------------+
| clean papers                |  - :meth:`pipeline.S04_pub_get_ads_entries`        |
|                             |  - :meth:`pipeline.S04_pub_get_orcids`             |
|                             |  - :meth:`pipeline.S04_pub_journal_index`          |
|                             |                                                    |
+-----------------------------+----------------------------------------------------+
| add journal index           |                                                    |
|                             |  - :meth:`pipeline.S04_pub_clean_papers`           |
|                             |                                                    |
+-----------------------------+----------------------------------------------------+
| add publication metrics     |                                                    |
|                             |  - :meth:`pipeline.S04_pub_value_added`            |
|                             |                                                    |
+-----------------------------+----------------------------------------------------+
| visual check                |                                                    |
|                             |  - :meth:`pipeline.S04_make_pages`                 |
|                             |  - :meth:`pipeline.S04_load_check_filters`         |
+-----------------------------+----------------------------------------------------+
| anonymize                   | - :meth:`pipeline.S05_anonymize`                   |
+-----------------------------+----------------------------------------------------+

In what follows we describe each step separately.
 

The module :meth:`pipeline` contains the steps fot the data reduction pipeline.


The steps are 

- S01: read base table (AAA)
- S02: add institutes and cic data
    In these steps the following columns are added:

    - cic
    - docencia
    - area
    - orcid
    - use_orcid

    The steps are contained in the following functions:

    - :meth:`pipeline.S02_add_OAC_data`
    - :meth:`pipeline.S02_add_IATE_data`
    - :meth:`pipeline.S02_add_IALP_data`
    - :meth:`pipeline.S02_add_ICATE_data`
    - :meth:`pipeline.S02_add_GAE_data`
    - :meth:`pipeline.S02_add_CIC_data`

- S03: add metadata for authors
    - S03_add_gender
    - S03_add_age
    - S03_clean_and_sor
- S04: add publications data
    - :meth:`pipeline.S04_pub_get_ads_entries`
    - :meth:`pipeline.S04_pub_get_orcids`
    - :meth:`pipeline.S04_pub_journal_index`
    - :meth:`pipeline.S04_pub_clean_papers`
    - :meth:`pipeline.S04_make_pages`
    - :meth:`pipeline.S04_pub_value_added`

API documentation for the code in **pipeline.py**:

.. automodule:: pipeline
    :members:
    :undoc-members:
    :show-inheritance:
