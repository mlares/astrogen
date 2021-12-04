Dataset
====================================

GENDER BALANCE IN THE ARGENTINA ASTRONOMY WORKFORCE

This dataset is published in http://dryad/datasets/astrogen,
see that link for full access to the data.

METADATA
--------

Dataset compiled from several oficial and public sources about the career
development for astronomers in Argentina.

- Marcelo Lares [1, 2, 3] ORCID:
- Valeria Coenda [1, 2, 3] ORCID:
- Luciana Gramajo [1, 2, 3] ORCID:
- Héctor Julián Martínez-Atencio [1, 2, 3] ORCID:
- Celeste Parisi [1, 2, 3] ORCID:
- Cinthia Ragone [1, 3] ORCID:

Affiliations:

- 1) Instituto de Astronomía Teórica y Experimental (IATE)
- 2) Observatorio Astronómico de Córdoba (OAC)
- 3) CONICET

Contact: Marcelo Lares

Date of data collection: Nov 29, 2021

GEOGRAPHIC LOCATION: Argentina

KEYWORDS: gender balance, astronomy

LANGUAGE: English

Funding sources: The authors acknowledge founding from CONICET and SECYT,
although to granted for this project especifically.


DATA AND FILE OVERVIEW
----------------------

We provide a single file containing an SQL database with five tables:


==============  ==============  ===============
table           #elements       #columns
==============  ==============  ===============
unc             0               0
people          0               0
papers          0               0
people_subset1  0               0
people_subset2  0               0
papers_subset1  0               0
papers_subset2  0               0
==============  ==============  ===============



* unc

fasdf

+--------+----------------+------------+-----------------------------+
| Column |  Name          | format     | description                 |
+========+================+============+=============================+
| year   |                | INT        |                             |
+--------+----------------+------------+-----------------------------+
| m_in   |                | INT        |                             |
+--------+----------------+------------+-----------------------------+
| m_out  |                | INT        |                             |
+--------+----------------+------------+-----------------------------+
| f_in   |                | INT        |                             |
+--------+----------------+------------+-----------------------------+
| f_out  |                | INT        |                             |
+--------+----------------+------------+-----------------------------+
 


* people

List of astronomers in Argentina

+--------+---------------------------+------------+-----------------------------+
| Column |   Name                    | format     | contents                    |
+========+===========================+============+=============================+
| 1      |  Author ID                | INT        |                             |
+--------+---------------------------+------------+-----------------------------+
| 2      |  age                      | INT        |                             |
+--------+---------------------------+------------+-----------------------------+
| 3      |  gender                   | CHAR       |                             |
+--------+---------------------------+------------+-----------------------------+
| 4      |  category at CONICET      | INT        |                             |
+--------+---------------------------+------------+-----------------------------+
| 5      |  number of papers in      | INT        |                             |
|        |  papers_subset1           |            |                             |
+--------+---------------------------+------------+-----------------------------+

   
* people_subset1

A view from the "people" table, corresponding to authors tha satisfy the
following criteria:

   - Active on 2021 (last published paper in a Q1 journal no before 2016)
   - Age in the rang 25 to 85 years old
   - At least 75% of the Q1 papers published with an affiliation in Argentina

* people_subset2

A view from the "people" table corrresponding to active researchers at CONICET
in 2020.


* papers

List of papers published by the selected authors in the "subset1" table.
The contents is as follows:
[  1 ] Author ID
[  2 ] Author position
[  3 ] Number of authors
[  4 ] Affiliation in Argentina
[  5 ] ...
[  6 ]
[  7 ]

+--------+---------------------------+---------+-----------------------------+
| Column |   Name                    | format  | contents                    |
+========+===========================+=========+=============================+
| 1      |  Author ID                | INT     |                             |
+--------+---------------------------+---------+-----------------------------+
| 2      |  author position          | INT     |                             |
+--------+---------------------------+---------+-----------------------------+
| 3      |  number of authors        | INT     |                             |
+--------+---------------------------+---------+-----------------------------+
| 4      |  journal index (Q)        | INT     |                             |
+--------+---------------------------+---------+-----------------------------+
| 5      |  Affiliation in Argentina | INT     |                             |
+--------+---------------------------+---------+-----------------------------+
| 6      |  number of citations      | INT     |                             |
+--------+---------------------------+---------+-----------------------------+   

These papers have been classified by an automatic agent as belonging to the
author.

* papers_subset1

These papars satisfy:
   - Published in a journal in the first quartile on at leat an area

This sample can be obtained from the "papers" table with the following SQL
query:
   
* papers_subset1

Besides the criteria for papers_subsample1, must satisfy also:
   - Less than 50 authors


This sample can be obtained from the "papers" table with the following SQL
query:




For each filename, a short description of what data it contains
Format of the file if not obvious from the file name
If the data set includes multiple files that relate to one another, the relationship between the files or a description of the file structure that holds them (possible terminology might include "dataset" or "study" or "data package")
Date that the file was created
Date(s) that the file(s) was updated (versioned) and the nature of the update(s), if applicable
Information about related data collected but that is not in the described dataset


Sharing and access information
Licenses or restrictions placed on the data
Links to publications that cite or use the data
Links to other publicly accessible locations of the data (see best practices for sharing data for more information about identifying repositories)
Recommended citation for the data (see best practices for data citation)
Methodological information
Description of methods for data collection or generation (include links or references to publications or other documentation containing experimental design or protocols used)
Description of methods used for data processing (describe how the data were generated from the raw or collected data)
Any software or instrument-specific information needed to understand or interpret the data, including software and hardware version numbers
Standards and calibration information, if appropriate
Describe any quality-assurance procedures performed on the data
Definitions of codes or symbols used to note or characterize low quality/questionable/outliers that people should be aware of
People involved with sample collection, processing, analysis and/or submission
Data-specific information
*Repeat this section as needed for each dataset (or file, as appropriate)*

Count of number of variables, and number of cases or rows
Variable list, including full names and definitions (spell out abbreviated words) of column headings for tabular data
Units of measurement
Definitions for codes or symbols used to record missing data
Specialized formats or other abbreviations used
Want a template? Download one and adapt it for your own data!

REFERENCES
----------





FILE FORMATS. Cornell Research Data Management Service Group. http://data.research.cornell.edu/content/file-formats

FILE MANAGEMENT. Cornell Research Data Management Service Group. http://data.research.cornell.edu/content/file-management 
