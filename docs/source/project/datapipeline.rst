Data pipeline
================

(these links are temporarily restricted to authors)

   + `Shared Drive with data warehouse <https://drive.google.com/drive/u/1/folders/0AN-YzcZ1W14wUk9PVA>`_ (requires access rights)
   + `Github repository for codes <https://github.com/mlares/astrogen>`_
   + `Overleaf document for paper <https://www.overleaf.com/project/612e7975fb24d63d9eef8aeb>`_ (requires access rights)
   + `Data repository <https://datadryad.org/stash>`_ (comming soon)


Get data
--------------------

The data used in this work has been collected from several sources,
namely:

* `Astronomical Data System <https://ui.adsabs.harvard.edu>`_

* `CONICET <https://www.conicet.gov.ar/gobierno-abierto/>`_

 - CONICET, "gobierno abierto > conicet en cifras"
   https://cifras.conicet.gov.ar/publica/
 - CONICET, "conicet digital" Repositorio institucional
   https://ri.conicet.gov.ar
 

* `Asociación Argentina de Astronomía <http://www.astronomiaargentina.org.ar>`_

* Astronomy Institutions in Argentina:

  + `IATE <http://iate.oac.uncor.edu>`_
  + `IAFE <http://www.iafe.uba.ar>`_
  + `ICATE <https://icate.conicet.gov.ar>`_
  + `IALP <http://ialp.fcaglp.unlp.edu.ar>`_
  + `OAC <https://oac.unc.edu.ar>`_

* Universities in Argentina

  + `UNC <https://www.unc.edu.ar>`_
     + `Lic. en Astronomía <https://www.famaf.unc.edu.ar/academica/grado/licenciatura-en-astronom%C3%ADa/>`_
     + `Statistical data <https://www.unc.edu.ar/programa-de-estad%C3%ADsticas-universitarias/anuarios-estad%C3%ADsticos>`_
  + `UNLP <https://unlp.edu.ar>`_
  + `UNSJ <http://www.unsj.edu.ar>`_


Feature construction
---------------------


* Age: We performed a non-linear least squares regression for the
  variables "DNI" and age, using as the training dataset that of the
  AAA original table.

* Gender: We use the `table
  <https://gist.github.com/muatik/10500344>`_ compiled by `Mustafa
  Atik <https://gist.github.com/muatik>`_ to assign gender on the
  basis of the names. We have also tried other tools, e.g.
  `genderize.io <https://genderize.io>`_, throught the client
  `https://github.com/SteelPangolin/genderize <genderize>`_, `GenderAPI <https://gender-api.com/en/api-docs>`_ web tool, with the same results.



Publications
-----------------------------

We have performed a detailed analysis of publication data for each
author. The process involves the following steps:


* Download ADS publication data for each author using the name as the
  search key. At this stage we use the python packages `ADS <https://ads.readthedocs.io/en/latest/>`_ and
  `PINNACLE <https://pinnacle.readthedocs.io/en/latest/?badge=latest>`_.

* Search and add ORCID keys

* Train, evaluate and apply a machine learning model to clean the sample of papers. This is required since the search by name often return the entries for
  several authors with similar names.

* Add metrics for journals, taking data from `SCImago Journal & Country Rank public portal <https://www.scimagojr.com>`_

* Add publication metrics


The curated dataset allows to construct sevarl indices:

+ number of authors per article
+ number of articles per author
+ number of articles per author, as leading author
+ distribution in time of articles
+ H-index
+ relative position of a given author in the authors list

