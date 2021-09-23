import datetime
import time
import pandas as pd
import bonobo
from dateutil.relativedelta import relativedelta
import numpy as np
from scipy.optimize import curve_fit
from astrogen_utils import bcolors, ds, ds1, ds2, get_gender2
import pickle



## base, raw data ##
"""
"""



## steps ##
"""
S01_read_aaa_table

S02_add_gender
S02_add_age
S02_clean_and_sort



add_oac_data
add_unlp_data
add_gae_data
add_icate_data
add_ue_data
add_iafe_data


add_cic_data

anonymize
"""

# EXTRACT

def S01_read_aaa_table():
    D = pd.read_excel('../../data/raw/sociosAAA_historico.xlsx')

    D.rename(columns={"DNI": "dni"}, inplace=True)
    D.rename(columns={"Nac": "nac"}, inplace=True)
    D.rename(columns={"Aff": "aff"}, inplace=True)
    D.rename(columns={"Fnac": "fnac"}, inplace=True)
    D.rename(columns={"Nombre": "nombre"}, inplace=True)
    D.rename(columns={"Apellido": "apellido"}, inplace=True)

    D['dni'] = D['dni'].apply(lambda x: x if np.isreal(x) else np.NaN)
 
    print('\nS01')
    print(D.columns)
    yield D


# TRANSFORM

def S02_add_gender(*args):
    """
    Add gender

    """
    D = args[0]
    N = D.shape[0]
    gender = []
    for i in range(N):
        name = D['nombre'].iloc[i]
        g = get_gender2(name)
        gender.append(g)
    D['genero'] = gender 
    print('\nS02_gender')
    print(D.columns)
    yield D

def S02_add_age(*args):
    """
    Add age

    """
    D = args[0]

    hdr = D.keys()
    D = D.drop(hdr[6:], axis=1)

    today = datetime.date.today()
    today = pd.to_datetime(today)

    D['fnac'] = pd.to_datetime(D['fnac'], errors='coerce')
    edad = []
    for day in D['fnac']:
        if pd.isnull(day):
            edad.append(-1)
        else:
            edad.append(relativedelta(today, day).years)

    D['fnac'] = D['fnac'].dt.strftime("%Y")
    D['edad'] = edad 

     
    # Estimación de la edad a partir del DNI ------------------------

    filt = D['nac'].str.contains('arg').values
    Darg = D[filt & D.edad.notnull()]
    df = Darg[Darg['dni'].between(1.e7, 4.e7) & Darg['edad'].between(20,70)]

    x = df['dni']
    y = df['edad']

    def age(dni, a, b, c):
        return a - b*dni*1.e-7 + c*(dni*1.e-7-2.5)**2

    x0 = [83, 16, 1.5]
    pars_age, cov = curve_fit(age, x, y, x0)

    N = D.shape[0]
    edad_fit = []
    for i in range(N):
        edad = D['edad'].iloc[i]
        dni = D['dni'].iloc[i]

        if edad < 1 and not np.isnan(dni):
            edad = age(dni, *pars_age)
        if edad < 1 and np.isnan(dni):
            edad = np.nan
        edad_fit.append(edad)
    D['edad'] = edad_fit
    print('\nS02_age')
    print(D.columns)
    yield D

def S02_clean_and_sort(*args):
    """
    Clean and sort columns

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

    print('\nS02_clean')
    print(D.columns)
    cols = ['apellido', 'nombre', 'genero', 'aff', 'lugar', 'aaa', 'area',
            'nac', 'dni', 'fnac', 'edad', 'cic', 'docencia', 'status']
    #D = D[cols] 

    yield D


# LOAD

def load(*args):
    D = args[0]
    print('\nLOAD')
    print(D.columns)
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
    """
    This function builds the services dictionary, which is a simple dict of names-to-implementation used by bonobo
    for runtime injection.

    It will be used on top of the defaults provided by bonobo (fs, http, ...). You can override those defaults, or just
    let the framework define them. You can also define your own services and naming is up to you.

    :return: dict
    """
    return {}


# The __main__ block actually execute the graph.
if __name__ == '__main__':
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser) as options:
        bonobo.run(
            get_graph(**options),
            services=get_services(**options)
        )
