ORGANIZE
========

(these links are temporarily restricted to authors)

   + `Shared Drive <https://drive.google.com/drive/u/1/folders/0AN-YzcZ1W14wUk9PVA>`_
   + `Github repository <git@github.com:mlares/astrogen.git>`_
   + `Overleaf document <https://www.overleaf.com/project/60d0fe7480df9741fb8eb662>`_


download & get data
--------------------

   * datos del ADS

   * planillas del CONICET

         + completar con lo que haga falta


   * planillas de socios de la AAA

         + planillas actualizadas, históricas?
         + no anda el link en la página a la planilla de socios

   * listas de integrantes de instituciones:

      + IATE, IAFE, ICATE, CASLEO, UNLP, PierreAuger, ...
      + preguntar en los CCT?


clean & curation
--------------------

   Asignar géneros por nombre



analysis
---------

Tomar la tabla de datos de socios de la AAA y limpiarla a mano en XLSX

--> data/redux/astro_arg.xlsx

Usar los archivos cross... para agregar las tabs a la tabla XLSX


NOTAS: El orcid es por autor, asi que se puede hacer al principio
La indexación es lenta, asi que conviene hacerla despues de limpiar
los papers.

D_value_added.pk, papers_cleaned.pk, scimagojr.csv → **pub_journals.py**
**pub_journals.py** → pickles/Qs_saved.pk


Proceso sobre los papers:

clean: pasar el modelo SVM
select: criterios de autores y papers







estadisticas de publicaciones
-----------------------------

Parte de la planilla del Google Drive: astro_all.xlsx

que contiene las columnas:


1) descargar todos los papers del ADS
.........................................

+ code: pub_get_ads_entries.py 
  + lee: astro_all.xlsx
  + escribe: data/ADS/papers_*.pk


2) agregar ORCIDs
.......................

El script genera un script de descarga, que hay que correr aparte, y
luego los lee con python y los agrega en el campo 'orcid_tent'

+ code: pub_get_orcids.py
  + lee: astro_all.xlsx (nombre y apellido)
  + escribe: data/pickles/D_orcids.pk



3) Entrenar modelo de ML para limpiar papers
.............................................


+ code: ads_names.py
  + lee: astro_all.xlsx, papers_saved.pk
  + escribe: ...data/ADS/papers_learn.csv



4) Generar modelo de ML para limpiar papers
............................................

+ code: ML_model.ipynb
  + lee: papers_learn.csv
  + escribe: SVM_model.joblib


5) limpiar papers por nombres de autores
.........................................

+ code:
  + lee: SVM_model.joblib
  + escribe:


6) Agregar métricas y listas de publicaciones
.............................................

+ code: pub_value_added.py
  + lee:
  + escribe:

Agrega las columnas:
  » D['Npapers'] = add_auth_Npprs
  » D['auth_pos'] = add_auth_pos
  » D['auth_num'] = add_auth_num
  » D['auth_inar'] = add_auth_inar
  » D['auth_citas'] = add_auth_citas


7) preparar indexación de los journals
.........................................


8) agregar indexación de los journals
.........................................

--- pub_journal_index.py


herramientas
..............

Mirar papers:

+ code: pub_check.py


python implementation
------------------------

We implemented a pdpipe data reduction pipeline, with an ETL
(Extract-Transform-Load) data integration process.