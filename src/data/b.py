import datetime
import time
import pandas as pd
import bonobo
from dateutil.relativedelta import relativedelta
import numpy as np
from scipy.optimize import curve_fit
from astrogen_utils import bcolors, ds, ds1, ds2, get_gender2
import pickle


# avoid SettingWithCopyWarning
# (see https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy)
pd.options.mode.chained_assignment = None

## base, raw data ##
"""
"""



## steps ##
"""
S01_read_aaa_table
S02_add_gender
S02_add_age
S02_clean_and_sort

S03_add_OAC_data
S03_add_IATE_data
S03_add_UNLP_data
S03_add_ICATE_data
S03_add_GAE_data

S04_add_CIC_data


SX_anonymize

"""

# EXTRACT

def S01_read_aaa_table():
    """
    STEP: S01_read_aaa_table

    This is the first step, that reads data from the AAA list.

    Columns:
    1)
    2)
    3)
    4)

    Returns:
    --------
    D: DataFrame containing the data

    """
    D = pd.read_excel('../../data/raw/sociosAAA_historico.xlsx')

    D.rename(columns={"DNI": "dni"}, inplace=True)
    D.rename(columns={"Nac": "nac"}, inplace=True)
    D.rename(columns={"Aff": "aff"}, inplace=True)
    D.rename(columns={"Fnac": "fnac"}, inplace=True)
    D.rename(columns={"Nombre": "nombre"}, inplace=True)
    D.rename(columns={"Apellido": "apellido"}, inplace=True)

    D['dni'] = D['dni'].apply(lambda x: x if np.isreal(x) else np.NaN)
 
    yield D


# TRANSFORM

def S02_add_gender(*args):
    """
    STEP: S02_add_gender

    In this step, genders are assigned according to data from XXX

    Columns:
    1)
    2)
    3)
    4)

    Returns:
    --------
    D: DataFrame containing the data

    """   
    D = args[0]
    N = D.shape[0]
    gender = []
    for i in range(N):
        name = D['nombre'].iloc[i]
        g = get_gender2(name)
        gender.append(g)
    D['genero'] = gender 
    yield D

def S02_add_age(*args):
    """
    STEP: S02_add_age

    In this step, age is computed and added.

    Columns:
    1)
    2)
    3)
    4)

    Notes:
    ------
    When the year of birthday is not available, a relacion between the
    DNI and the age is fitted aud used to complete the data.
    DNI (Documento nacional de identidad) number is assigned
    correlatively after inscription of newborns, which is mandatory in
    Argentina.

    Returns:
    --------
    D: DataFrame containing the data

    """    
    df = args[0]

    today = datetime.date.today()
    today = pd.to_datetime(today)

    df['fnac'] = pd.to_datetime(df['fnac'], errors='coerce')
    edad = []
    for day in df['fnac']:
        if pd.isnull(day):
            edad.append(-1)
        else:
            edad.append(relativedelta(today, day).years)

    df['fnac'] = df['fnac'].dt.strftime("%Y")
    df['edad'] = edad 
     
    # Estimate age from DNI ------------------------

    filt = df['nac'].str.contains('arg').values
    Darg = df[filt & df.edad.notnull()]
    df = Darg[Darg['dni'].between(1.e7, 4.e7) & Darg['edad'].between(20,70)]

    x = df['dni']
    y = df['edad']

    def age(dni, a, b, c):
        return a - b*dni*1.e-7 + c*(dni*1.e-7-2.5)**2

    x0 = [83, 16, 1.5]
    pars_age, cov = curve_fit(age, x, y, x0)

    N = df.shape[0]
    edad_fit = []
    for i in range(N):
        edad = df['edad'].iloc[i]
        dni = df['dni'].iloc[i]

        if edad < 1 and not np.isnan(dni):
            edad = age(dni, *pars_age)
        if edad < 1 and np.isnan(dni):
            edad = np.nan
        edad_fit.append(edad)
    df.drop(columns=['edad'], inplace=True)
    df['edad'] = edad_fit
    yield df

def S02_clean_and_sort(*args):
    """
    STEP: S02_clean_and_sort

    In this step, columns of the database are cleaned and sorted

    Columns:
    1)
    2)
    3)
    4)

    Returns:
    --------
    D: DataFrame containing the data

    """     

    D = args[0] 

    D['cic'] = ''
    D['docencia'] = ''
    D['lugar'] = ''
    D['area'] = ''
    D['status'] = ''
    D['aaa'] = ''

    D.dni = D.dni.apply(lambda x: int(x) if pd.notna(x) else '')
    D.edad = D.edad.apply(lambda x: int(x) if pd.notna(x) else '')
    cols = ['apellido', 'nombre', 'genero', 'aff', 'lugar', 'aaa', 'area',
            'nac', 'dni', 'fnac', 'edad', 'cic', 'docencia', 'status']
    D = D[cols] 
    yield D



def S03_add_OAC_data(*args):
    """
    STEP: S03_add_OAC_data

    In this step, the database is combined with data from the OAC

    Columns:
    1)
    2)
    3)
    4)

    Returns:
    --------
    D: DataFrame containing the data

    """     

    D = args[0] 




 
    yield D



def S03_add_IATE_data(*args):
    """
    STEP: S03_add_OAC_data

    In this step, the database is combined with data from the IATE

    Columns:
    1)
    2)
    3)
    4)

    Returns:
    --------
    D: DataFrame containing the data

    """     

    D = args[0] 



AAA = pd.read_excel('../../../data/redux/astro_arg.xlsx')
AAA['orcid'] = ''

UE = pd.read_excel('../../../data/UEs/IATE_julio_2021.xlsx')
UE.drop(UE.filter(regex="Unname"),axis=1, inplace=True)

filt = []
inds = []
for i, (n1, a1) in enumerate(zip(UE['nombre'], UE['apellido'])):
    closest = 99
    for j, (n2, a2) in enumerate(zip(AAA['nombre'], AAA['apellido'])):
        d = ds2(a1, a2, n1, n2)
        if d < closest:
            closest = d
            ind = j
            nc2 = n2
            ac2 = a2
    cond = closest < 0.26
    inds.append(ind)
    filt.append(cond)

filt = np.array(filt)
inds = np.array(inds)

AAA.cic = AAA.cic.astype(str)
AAA.area = AAA.area.astype(str)
AAA.docencia = AAA.docencia.astype(str)
N = len(filt)
for i in range(N):
    if filt[i]:
        AAA.at[inds[i], 'cic'] = UE.iloc[i].cic
        AAA.at[inds[i], 'orcid'] = UE.iloc[i].orcid
        AAA.at[inds[i], 'area'] = UE.iloc[i].area
        AAA.at[inds[i], 'docencia'] = UE.iloc[i].docencia
        AAA.at[inds[i], 'aff'] = 'IATE'
 
ADD = UE[~np.array(filt)]

# Agregar columna de género
N = ADD.shape[0]
gender = []

for i in range(N):
    name = ADD['nombre'].iloc[i]
    g = get_gender2(name)
    gender.append(g)

ADD['genero'] = gender  
                
ADD['aff'] = 'IATE'
ADD['lugar'] = 'IATE'
ADD['aaa'] = 0
ADD['area'] = ''
ADD['nac'] = ''
ADD['dni'] = ''
ADD['fnac'] = ''
ADD['edad'] = ''
ADD['cic'] = ''
ADD['orcid'] = ''
ADD['status'] = ''
ADD['docencia'] = ''
                       
ADD = ADD[list(AAA.columns)]  

df = pd.concat([AAA, ADD])

# Escribir en una tabla de excell

path = '../../../data/redux/astro_arg.xlsx'
append_df_to_excel(path, ADD, sheet_name="NoSoc_IATE", 
                   startcol=0, startrow=0, index=False)

path = '../../../data/redux/astro_all.xlsx'
append_df_to_excel(path, df, sheet_name="con IATE",  
                   startcol=0, startrow=0, index=False) 


 
    yield D

def S03_add_ICATE_data(*args):
    """
    STEP: S03_add_OAC_data

    In this step, the database is combined with data from the ICATE

    Columns:
    1)
    2)
    3)
    4)

    Returns:
    --------
    D: DataFrame containing the data

    """     

    D = args[0] 
 
    yield D

def S03_add_UNLP_data(*args):
    """
    STEP: S03_add_OAC_data

    In this step, the database is combined with data from the UNLP

    Columns:
    1)
    2)
    3)
    4)

    Returns:
    --------
    D: DataFrame containing the data

    """     

    D = args[0] 
 
    yield D

def S03_add_IAFE_data(*args):
    """
    STEP: S03_add_OAC_data

    In this step, the database is combined with data from the IAFE

    Columns:
    1)
    2)
    3)
    4)

    Returns:
    --------
    D: DataFrame containing the data

    """     

    D = args[0] 
 
    yield D

def S03_add_GAE_data(*args):
    """
    STEP: S03_add_OAC_data

    In this step, the database is combined with data from the GAE

    Columns:
    1)
    2)
    3)
    4)

    Returns:
    --------
    D: DataFrame containing the data

    """     

    D = args[0] 
 
    yield D






# LOAD

def load(*args):
    """
    STEP: S02_clean_and_sort

    In this step, columns of the database are cleaned and sorted

    Columns:
    1)
    2)
    3)
    4)

    Returns:
    --------
    D: DataFrame containing the data

    """   

    D = args[0]
    fileD = '../../data/redux/D.pk'
    with open(fileD, 'wb') as f:
       pickle.dump(D, f)
    #
    fileD = '../../data/redux/D.csv'
    with open(fileD, 'wb') as f:
       D.to_csv(f)




def get_graph(**options):
    """
    This function builds the graph that needs to be executed.

    :return: bonobo.Graph

    """
    graph = bonobo.Graph()
    graph.add_chain(S01_read_aaa_table,
                    S02_add_gender,
                    S02_add_age,
                    S02_clean_and_sort,
                    load)
    return graph


def get_services(**options):
    """ This function builds the services dictionary, which is a
    simple dict of names-to-implementation used by bonobo for runtime
    injection.
    It will be used on top of the defaults provided by bonobo (fs,
    http, ...). You can override those defaults, or just let the
    framework define them. You can also define your own services and
    naming is up to you.
    :return: dict
    """
    return {}

if __name__ == '__main__':
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser) as options:
        bonobo.run(
            get_graph(**options),
            services=get_services(**options)
        )
