
import pdpipe as pdp
import pandas as pd
import numpy as np
from openpyxl import load_workbook

from astrogen_utils import bcolors, ds, ds1, ds2, get_gender2
from astrogen_utils import append_df_to_excel
 


"""
Extract

[  1 ]  Get ADS entries                    
[  2 ]  Get ORCID entries                  
[  3 ]  Get journals scores                

Transform

[  4 ]  Add ORCIDS                         
[  5 ]  Add journals scores                
[  6 ]  Generate examples for the ML model 
[  7 ]  Train the model                    
[  8 ]  Clean papers lists                 
[  9 ]  Filter authors
[ 10 ]  Generate html files                
[ 11 ]  Load filters for papers            
[ 12 ]  Check                              
[ 13 ]  Plot papers stats                  

Load


"""


Eliminar una columna:

step = pdp.ColDrop('column name')


Agregar una columna:




pipeline+=pdp.ApplyByCols('Price', price_tag, 'Price_tag', drop=False)


https://pdpipe.github.io/pdpipe/doc/pdpipe/

pipeline = pdp.ColDrop('Avg. Area House Age')
pipeline+= pdp.OneHotEncode('House_size')
pipeline+=pdp.ApplyByCols('Price',price_tag,'Price_tag',drop=False)
pipeline+=pdp.ValDrop(['drop'],'Price_tag')
pipeline+= pdp.ColDrop('Price_tag')
pipeline_scale = pdp.Scale('StandardScaler',exclude_columns=['House_size_Medium','House_size_Small'])

>>> drop_name = pdp.ColDrop("Name")
>>> binar_label = pdp.OneHotEncode("Label")
>>> map_job = pdp.MapColVals("Job", {"Part": True, "Full":True, "No": False})
>>> pipeline = pdp.PdPipeline([drop_name, binar_label, map_job])
>>> print(pipeline)


se pueden hacer slices de un pipeline, e.g. pipeline[2:4]






step_01 = 

step_02 = 

step_03 = 

step_04 = 


extract_steps = step_01 + step_02 + step_03 + step_04
transform_steps = step_01 + step_02 + step_03 + step_04
load_steps = step_01 + step_02 + step_03 + step_04


pipeline = extract_steps + transform_steps + load_steps


# LOAD raw data ::::::::::::::::::::::::::::::

pd.options.mode.chained_assignment = None
pd.set_option('display.max_rows', None)

df = pd.read_excel('../../data/redux/astro_all.xlsx', sheet_name="todos")
 
# Apply pipeline :::::::::::::::::::::::::::::

df_VA = pipeline(df)

# Write final dataset ::::::::::::::::::::::::

fileD = '../../data/pickles/D_selected.pk'
with open(fileD, 'wb') as f:
   pickle.dump(df_VA, f)




COMO HAGO CON LOS PAPERS???

fileD = '../../data/pickles/papers_selected.pk'
with open(fileD, 'wb') as f:
   pickle.dump(papers_selected, f)
 



"""
Resources:

https://algakovic.medium.com/extract-transform-load-etl-with-pandas-d9e52c309e82
"""


