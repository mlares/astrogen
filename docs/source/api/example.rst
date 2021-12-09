Example
======================

This project is organized as an API to be used from a python prompt.

Steps:

- Complete the configuration of the experiment
- All the settings of the experimets are parsed from the configuration
  files using configparser.

Installation
............

First, download the latest version of the code repository `ASTROGEN <https://github.com/mlares/astrogen>`_ in GitHub.

.. code-block:: bash

    $ git clone git@github.com:mlares/astrogen.git


The code has been tested in the following python versions:

+ 3.8.5


The list of requirements is given in the file "requirements.txt":

+ ads==0.12.3
+ bonobo==0.6.4
+ jellyfish==0.8.9
+ Jinja2==2.11.3
+ kaleido==0.2.1
+ matplotlib==3.5.0
+ nltk==3.6.5
+ openpyxl==3.0.9
+ pandas==1.3.4
+ plotly==5.4.0
+ scipy==1.7.3
+ seaborn==0.11.2
+ scikit-learn==1.0.1

However, in order to reproduce the plots from the SQL database, the
following packages will suffice:

+ scipy==1.7.3
+ matplotlib==3.5.0
+ seaborn==0.11.2
+ pandas==1.3.4
+ plotly==5.4.0
+ kaleido==0.2.1



In order to run the data pipeline, which connects to the ADS online database,
an API KEY is required. Documentation for obtaining and using this key can be found in the `ADS API documentation <https://ui.adsabs.harvard.edu/help/api/>`_.


.. code-block:: bash

    $ conda create --name astrogen

The recommended method is to create a virtual environment
(using either conda or virtualenv) and then:

.. code-block:: bash

    pip install -r requirements.txt


Data
..............


The file that needs to be copied is:

astrogen_DB_anonymous.db

and must be placed in the directory data/redux.






Full run
..............

The full run data is not available since it contains personal data.
Here we privide a guide to run the full data reduction pipeline.
The first step is to make spreadsheets with the following data:







Configuration
..............

The main configurations are set in a configuration file writen in a
configuration file.

An example of the configuration file is as follows:

.. code-block::

   # _____________________________________________________
   [experiment] # EXPERIMENT ID

   # Experiment ID.  Useful to compare and save experiments.
   # A directory will be created with this name under [out]dir_output
   experiment_ID = TRNT_001

   # _____________________________________________________
   [dirs] # Directory structure (relative to: astrogen/)

   # locations of data files
   datadir_root = data/

   # locations of external data files
   # relative to $datadir_root
   datadir_external = external

   # locations of interim data files
   # relative to $datadir_root
   datadir_interim = interim

   # locations of raw data files
   # relative to $datadir_root
   datadir_raw = raw

   # locations of redux data files
   # relative to $datadir_root
   datadir_redux = redux

   # locations of ADS data files
   # relative to $datadir_root/$datadir_redux
   datadir_ADS = ADS

   # locations of orcid data files
   # relative to $datadir_root/$datadir_redux
   datadir_orcid = ordic

   # locations of model files
   # relative to $datadir_root
   datadir_models = models

   # locations of report files
   # relative to $datadir_root
   datadir_report = report


   # _____________________________________________________
   [pp] # PIPELINE

   # Select which steps in the data reduction pipeline must be run.

   # steps 01 are mandatory

   # steps 02:

   # use OAC data
   use_OAC_data = yes

   # use IATE data
   use_IATE_data = yes

   # use IALP data
   use_IALP_data = yes

   # use GAE data
   use_GAE_data = yes

   # use IAFE data
   use_IAFE_data = yes

   # use ICATE data
   use_ICATE_data = yes

   # use CIC data
   use_CIC_data = yes

   # generate gender data
   gen_gender = yes

   # generate age data
   gen_age = yes

   # download ADS data
   get_ads_data = yes

   # guess orcid data
   guess_orcid_data = yes

   # build journals indices
   build_journals_indices = yes

   # generate value added publication data
   build_valueadded_pub = yes


   # _____________________________________________________
   [run] # CONFIGURATIONS FOR EXPERIMENT AND COMPUTATIONS

   # performance computing ---

   # number of jobs, to be passed to joblib.  Ignored if not run_parallel:
   n_jobs = 1
   # whether to run serial or parallel:
   run_parallel = no


   # _____________________________________________________
   [out] # OUTPUT SETTINGS



   # _____________________________________________________
   [UX] # USER EXPERIENCE

   # Show progress bars
   # options: Y/N
   show_progress = y

   # Show messages for partial computations
   # options: Y/N
   verbose = y

   # Return objects (N: only write to files)
   # options: Y/N
   interactive = n




The directory tree structure is defined as follows:

.. code-block:: html
    :linenos:

    ├── astrogen
    │   ├── data
    │   ├── dataviz
    │   ├── models
    │   └── sql
    ├── data
    │   ├── external
    │   │   ├── ADS
    │   │   └── ORCID
    │   ├── interim
    │   │   └── ADS
    │   ├── collect
    │   └── redux
    ├── docs
    │   └── source
    │       ├── api
    │       ├── img
    │       └── project
    ├── models
    ├── notebooks
    ├── figures
    └── sets


This structure must be used with the configuration file defaults. If a
different structure is needed, the corresponding names of the
directories must be changed, of the code edited so as to ignore the
parsing of the configuration file and override the default values.




Once the settings have been saved, run the pipeline:

.. code-block:: bash

   cd astrogen/astrogen/data
   python pipeline

This code generates a pickle file containing a pandas dataframe with
the full dataset. An SQL data file similar to the one provided can be
generated adding the following steps:

.. code-block:: bash

   python clean_anonymous
   python database_anonymous
