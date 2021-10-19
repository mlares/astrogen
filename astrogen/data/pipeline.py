import datetime
import time
import pandas as pd
import bonobo
import numpy as np
from dateutil.relativedelta import relativedelta
import numpy as np
from scipy.optimize import curve_fit
import pickle
import ads
from sys import argv
from Parser import Parser
import difflib
from os import path, system
from os.path import join as pathjoin
import numpy as np
from tqdm import tqdm
import re
import jellyfish
from joblib import dump, load
from io import StringIO
import jinja2
 
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import csv
from difflib import SequenceMatcher
      
from astrogen_utils import bcolors, ds, ds1, ds2, get_gender2
from astrogen_utils import initials, getinitials, pickone, similar
 
# avoid SettingWithCopyWarning
# (see https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy)
# pd.options.mode.chained_assignment = None


def get_filters_by_names(D, UE):
    """
    Given two dataframes with "nombre" key, find the entries in the 
    second dataframe (UE) that match any entry in the first dataframe.

    Args:
    D: DataFrame, base data

    UE: DataFrame, data to be added

    Returns:
    filt: ndarray

    inds: ndarray

    """
    filt = []
    inds = []
    for i, (n1, a1) in enumerate(zip(UE['nombre'], UE['apellido'])):
        closest = 99
        for j, (n2, a2) in enumerate(zip(D['nombre'], D['apellido'])):
            d = ds2(a1, a2, n1, n2)
            if d < closest:
                closest = d
                ind = j
                nc2 = n2
                ac2 = a2
        cond = closest < 0.26
        filt.append(cond)
        inds.append(ind)

    filt = np.array(filt)
    inds = np.array(inds)
    return filt, inds

def set_empty_with_type(tipo):
    """
    Returns an empty object of a given type.

    Args:
    tipo: type

    Returns:
    An empty object of the same type.
    """
    if tipo == type(''):
        return ''
    elif tipo == type(1):
        return np.nan
    elif tipo == type(1.):
        return np.nan
    elif tipo == type([]):
        return []
    else:
        return np.nan

def fill_empty_columns(df1, df2):
    """
    add empty columns to df1 that are in df2 but not in df1

    Args:

       df1 (DataFrame): A Pandas dataframe with data
       df2 (DataFrame): A Pandas dataframe with data

    """
    for c, t in zip(df2.columns, df2.iloc[0]):
        if c not in df1.columns:
            df1[c] = set_empty_with_type(type(t))

    return df1

def ft_year(s):
    """
    Returns the year from a datetime object

    Notes:
       If it is not possible to return the year, then returns -1

    """
    try:
        y=s.year
    except AttributeError:
        y=-1
    return y
 
def ft_low(s):
    """
    Returns the affiliation in lower case format

    """
    if isinstance(s, str):
        y = s.lower()
    else:
        y = s
    return y

def re_names(string):
    """
    Dado un nombre, devuelve los nombres completos o iniciales

    """
    string = string.title()
    regex1 = r"[A-Z][^A-Z\s]\w+"
    fullnames = re.findall(regex1, string)
    if len(fullnames)>0:
        if '.' in fullnames[0]:
            fullnames = ''
    regex2 = "[A-Z][A-Z][A-Z]\s|[A-Z][A-Z]\s|[A-Z]\.|[A-Z]$"
    regaux = r"[A-Z][A-Z][A-Z]|[A-Z][A-Z]"
    laux = re.findall(regaux, string)
    if len(laux)>0:
        iniciales = ('. '.join(list(laux[0])) + '.').split()
    else:
        iniciales = re.findall(regex2, string)
    if len(fullnames)>0 and len(iniciales)==0:
        for s in fullnames:
            iniciales.append(getinitials(s))
    return ' '.join(fullnames), ' '.join(iniciales)

def aut_compare(aut1, aut2):
    """
    each author: ap_full, ap_inic, nom_full, nom_inic

    e.g.:
    aut_compare([['Lares'], [], [], ['M.']], [['Lares'], [], [], ['M. E.']])

    """
    # comparar apellidos:
    a1 = aut1[0]
    a2 = aut2[0]

    d_ap = difflib.SequenceMatcher(None, a1, a2).ratio()
    d1_ap = jellyfish.damerau_levenshtein_distance(a1, a2)
    d2_ap = jellyfish.jaro_distance(a1, a2)     
    d3_ap = jellyfish.levenshtein_distance(a1, a2)                          

    # comparar nombres:
    if len(aut2[2])>0: # tiene nombre completo
        a1 = aut1[2]
        a2 = aut2[2]
        d_n = difflib.SequenceMatcher(None, a1, a2).ratio()
        d1_n = jellyfish.damerau_levenshtein_distance(a1, a2)
        d2_n = jellyfish.jaro_distance(a1, a2)     
        d3_n = jellyfish.levenshtein_distance(a1, a2)                          

    else: # tiene solo iniciales
        a1 = aut1[3]
        a2 = aut2[3]
        d_n = difflib.SequenceMatcher(None, a1, a2).ratio()
        d1_n = jellyfish.damerau_levenshtein_distance(a1, a2)
        d2_n = jellyfish.jaro_distance(a1, a2)     
        d3_n = jellyfish.levenshtein_distance(a1, a2)                          

    return [d_ap, d_n, d1_ap, d1_n, d2_ap, d2_n, d3_ap, d3_n,
           len(aut1[0]), len(aut2[0]), 
           len(aut1[1]), len(aut2[1])]

def authmatch(x, ip, show=False):
    """
    Dado un autor y un paper, determinar si ese paper
    es de ese autor.

    0)ap_full, 1)ap_inic, 2)nom_full, 3)nom_inic,  <--- autor buscado

    4)etal_ap_full, 5)etal_ap_inic, 6)etal_nom_full, 7)etal_nom_inic

    """
    nms = [[[]]*4, [[]]*4]
    nms[0][0:2] = re_names(x.apellido)
    nms[0][2:4] = re_names(x.nombre)

    mx = -99

    for au, af in zip(ip.author, ip.aff):
        nl = au.split(',')
        if len(nl)==2:
            au_surname, au_name = nl
        elif len(nl)>2:
            au_surname = nl[0]
            au_name = ''.join(nl[1:])
        else:
            au_surname = nl[0]
            au_name = ''

        nms[1][0:2] = re_names(au_surname)
        nms[1][2:4] = re_names(au_name)
        ll = aut_compare(*nms)

        m = ll[0]+ll[1]-ll[2]-ll[3]-ll[4]-ll[5]
        if m > mx:
            lmx = ll
            mx = m
        ar = 1 if 'entina' in af else 0
        if not ar: ar = 0.5 if (af==' ' or af=='-') else 0
        ll.append(ar)
        if show:
            if ll[0]>0.8:
                print(f'\u001b[46;1m   {au} \u001b[0m{af[:80]}')
            else:
                print(f'   \u001b[46;1m{au} \u001b[0m{af[:80]}')

    return lmx
         



## steps ##
"""
S01: read base table (AAA)
S02: add institutes and cic data
S03: add metadata for authors
S04: add publications data

SX_anonymize
"""


# EXTRACT

def S01_read_aaa_table():
    """
    STEP: S01_read_aaa_table

    This is the first step, that reads data from the AAA list.
    This is the more complete list, so it used as the base list to add
    information from other data sources.

    | Columns:
    | 1) apellido 
    | 2) nombre   
    | 3) ads_str: string to look for in ADS
    | 4) dni: documento nacional de identidad
    | 5) fnac: day of birth
    | 6) ynac: year of birth
    | 7) aff: affiliation
    | 8) nac: nacionality
    | 9) aaa_soc: aaa situation

    Returns:
    D: DataFrame containing the data

    Notes:

    | aa_soc codes:
    | B1   baja por fallecimiento
    | B2   baja por renuncia no vinculada al alejamiento de la Astronomía
    | B3   baja por desvinculación de la Astronomía (incluyendo renuncia)
    | B4   baja por no haberse reempadronado al 01/01/2005
    | B5   baja por morosidad en el pago
    | B6   baja por expulsión, falta profesional grave
    | L    licencia
    | A1   activo
    | Pf   profesional
    | Ad   adherente
    | Af   aficionado
    | F    fallecido
    | FP   fallecido a posteriori de su baja

    """
    D = pd.read_excel('../../data/raw/collect_AAA.xlsx')

    D['ynac'] = D.ynac.apply(ft_year)
    D['dni'] = D['dni'].apply(lambda x: x if np.isreal(x) else np.NaN)
 
    yield D


# TRANSFORM: add data from institutes
""" 
| In these steps the following columns are added:
|     - cic
|     - docencia
|     - area
|     - orcid
|     - use_orcid
| 
| The steps are contained in the following functions:
|     - S02_add_OAC_data
|     - S02_add_IATE_data
|     - S02_add_UNLP_data
|     - S02_add_ICATE_data
|     - S02_add_GAE_data
|     - S02_add_CIC_data
""" 

def S02_add_OAC_data(*args):
    """
    STEP: S02_add_OAC_data

    In this step, the database is combined with data from the OAC

    | Columns:
    | 1) apellido  
    | 2) nombre    
    | 3) ads_str   
    | 4) dni
    | 5) ynac      
    | 6) cic (+)
    | 7) docencia (+)
    | 8) area (+)
    | 9) orcid (+)
    | 10) use_orcid (+)

    Returns:
    D: DataFrame containing the data

    """     

    D = args[0] 
    UE = pd.read_excel('../../data/raw/collect_OAC.xlsx')
    UE.drop(UE.filter(regex="Unname"),axis=1, inplace=True)

    filt, inds = get_filters_by_names(D, UE)
    D = fill_empty_columns(D, UE)

    N = len(filt)
    for i in range(N):
        if filt[i]:
            D.at[inds[i], 'cic'] = UE.iloc[i].cic
            D.at[inds[i], 'orcid'] = UE.iloc[i].orcid
            D.at[inds[i], 'area'] = UE.iloc[i].area
            D.at[inds[i], 'dni'] = UE.iloc[i].dni 
            D.at[inds[i], 'aff'] = D.at[inds[i], 'aff'] + ' OAC'

    ADD = UE[~np.array(filt)]
    ADD = fill_empty_columns(ADD, D)
    ADD = ADD[list(D.columns)]  
    D = pd.concat([D, ADD], ignore_index=True)
    yield D

def S02_add_IATE_data(*args):
    """
    STEP: S02_add_IATE_data

    In this step, the database is combined with data from the IATE

    | Columns:
    | 1) apellido  
    | 2) nombre    
    | 3) ads_str   
    | 4) ynac      
    | 5) cic (+)
    | 6) docencia (+)
    | 7) area (+)
    | 8) orcid (+)
    | 9) use_orcid (+)

    Returns:
    D: DataFrame containing the data

    """     

    D = args[0] 

    UE = pd.read_excel('../../data/raw/collect_IATE.xlsx')
    UE.drop(UE.filter(regex="Unname"),axis=1, inplace=True)

    filt, inds = get_filters_by_names(D, UE)
    D = fill_empty_columns(D, UE)

    N = len(filt)
    for i in range(N):
        if filt[i]:
            D.at[inds[i], 'cic'] = UE.iloc[i].cic
            D.at[inds[i], 'orcid'] = UE.iloc[i].orcid
            D.at[inds[i], 'area'] = UE.iloc[i].area
            D.at[inds[i], 'dni'] = UE.iloc[i].dni 
            D.at[inds[i], 'aff'] = D.at[inds[i], 'aff'] + ' IATE'

    ADD = UE[~np.array(filt)]
    ADD = fill_empty_columns(ADD, D)
    ADD = ADD[list(D.columns)]  
    D = pd.concat([D, ADD], ignore_index=True)
    yield D

def S02_add_ICATE_data(*args):
    """
    STEP: S02_add_ICATE_data

    In this step, the database is combined with data from the ICATE

    | Columns: 
    | 1) apellido  
    | 2) nombre    
    | 3) ads_str   
    | 4) dni
    | 5) ynac      
    | 6) cic (+)
    | 7) docencia (+)
    | 8) area (+)
    | 9) orcid (+)
    | 10) use_orcid (+) 

    Returns:
    D: DataFrame containing the data

    """     
    D = args[0] 
    UE = pd.read_excel('../../data/raw/collect_ICATE.xlsx')
    UE.drop(UE.filter(regex="Unname"),axis=1, inplace=True)

    filt, inds = get_filters_by_names(D, UE)
    D = fill_empty_columns(D, UE)

    N = len(filt)
    for i in range(N):
        if filt[i]:
            D.at[inds[i], 'cic'] = UE.iloc[i].cic
            D.at[inds[i], 'orcid'] = UE.iloc[i].orcid
            D.at[inds[i], 'area'] = UE.iloc[i].area
            D.at[inds[i], 'dni'] = UE.iloc[i].dni 
            D.at[inds[i], 'aff'] = D.at[inds[i], 'aff'] + ' ICATE' 
    ADD = UE[~np.array(filt)]
    ADD = fill_empty_columns(ADD, D)
    ADD = ADD[list(D.columns)]  
    D = pd.concat([D, ADD], ignore_index=True)
    yield D

def S02_add_IALP_data(*args):
    """
    STEP: S02_add_IALP_data

    In this step, the database is combined with data from the IALP

    | Columns:
    | 1) apellido  
    | 2) nombre    
    | 3) ads_str   
    | 4) dni
    | 5) ynac      
    | 6) cic (+)
    | 7) docencia (+)
    | 8) area (+)
    | 9) orcid (+)
    | 10) use_orcid (+) 

    Returns:
    D: DataFrame containing the data

    """     
    D = args[0] 
    UE = pd.read_excel('../../data/raw/collect_IALP.xlsx')
    UE.drop(UE.filter(regex="Unname"),axis=1, inplace=True)

    filt, inds = get_filters_by_names(D, UE)
    D = fill_empty_columns(D, UE)

    N = len(filt)
    for i in range(N):
        if filt[i]:
            D.at[inds[i], 'cic'] = UE.iloc[i].cic
            D.at[inds[i], 'orcid'] = UE.iloc[i].orcid
            D.at[inds[i], 'area'] = UE.iloc[i].area
            D.at[inds[i], 'dni'] = UE.iloc[i].dni 
    #        D.at[inds[i], 'aff'] = D.at[inds[i], 'aff'] + ' IALP' 

    #ADD = UE[~np.array(filt)]
    #ADD = fill_empty_columns(ADD, D)
    #ADD = ADD[list(D.columns)]  
    #D = pd.concat([D, ADD], ignore_index=True)
    yield D

def S02_add_IAFE_data(*args):
    """
    STEP: S02_add_IAFE_data

    In this step, the database is combined with data from the IAFE

    | Columns:
    | 1) apellido  
    | 2) nombre    
    | 3) ads_str   
    | 4) dni
    | 5) ynac      
    | 6) cic (+)
    | 7) docencia (+)
    | 8) area (+)
    | 9) orcid (+)
    | 10) use_orcid (+) 

    Returns:
    D: DataFrame containing the data

    """     
    D = args[0] 
    UE = pd.read_excel('../../data/raw/collect_IAFE.xlsx')
    UE.drop(UE.filter(regex="Unname"),axis=1, inplace=True)

    filt, inds = get_filters_by_names(D, UE)
    D = fill_empty_columns(D, UE)

    N = len(filt)
    for i in range(N):
        if filt[i]:
            D.at[inds[i], 'cic'] = UE.iloc[i].cic
            D.at[inds[i], 'orcid'] = UE.iloc[i].orcid
            D.at[inds[i], 'area'] = UE.iloc[i].area
            D.at[inds[i], 'dni'] = UE.iloc[i].dni 
            D.at[inds[i], 'aff'] = D.at[inds[i], 'aff'] + ' IAFE' 
    ADD = UE[~np.array(filt)]
    ADD = fill_empty_columns(ADD, D)
    ADD = ADD[list(D.columns)]  
    D = pd.concat([D, ADD], ignore_index=True)
    yield D

def S02_add_GAE_data(*args):
    """
    STEP: S02_add_GAE_data

    In this step, the database is combined with data from the GAE

    | Columns:
    | 1) apellido  
    | 2) nombre    
    | 3) ads_str   
    | 4) dni
    | 5) ynac      
    | 6) cic (+)
    | 7) docencia (+)
    | 8) area (+)
    | 9) orcid (+)
    | 10) use_orcid (+) 

    Returns:
    D: DataFrame containing the data

    """     
    D = args[0] 
    UE = pd.read_excel('../../data/raw/collect_GAE.xlsx')
    UE.drop(UE.filter(regex="Unname"),axis=1, inplace=True)

    filt, inds = get_filters_by_names(D, UE)
    D = fill_empty_columns(D, UE)

    N = len(filt)
    for i in range(N):
        if filt[i]:
            D.at[inds[i], 'cic'] = UE.iloc[i].cic
            D.at[inds[i], 'orcid'] = UE.iloc[i].orcid
            D.at[inds[i], 'area'] = UE.iloc[i].area
            D.at[inds[i], 'dni'] = UE.iloc[i].dni 
            D.at[inds[i], 'aff'] = D.at[inds[i], 'aff'] + ' GAE' 
    ADD = UE[~np.array(filt)]
    ADD = fill_empty_columns(ADD, D)
    ADD = ADD[list(D.columns)]  
    D = pd.concat([D, ADD], ignore_index=True)
    yield D



# TRANSFORM: add data from CONICET
"""
Add data for the scientific research career at CONICET
"""

def S02_add_CIC_data(*args):
    """
    STEP: S03_add_OAC_data

    In this step, the database is combined with data from the GAE

    | Columns:
    | 1) apellido
    | 2) nombre
    | 3) categoria (+)
    | 4) area (+)
    | 5) subarea (+)
    | 6) ue (+)
    | 7) l (+)
    | 8) tema (+)
    | 9) sn (+)

    Returns:
    D: DataFrame containing the data

    """     
    D = args[0] 
    CIC = pd.read_excel('../../data/raw/collect_CIC.xlsx')
    CIC.drop(CIC.filter(regex="Unname"),axis=1, inplace=True)

    filt, inds = get_filters_by_names(D, CIC)
    D = fill_empty_columns(D, CIC)
 
    N = len(filt)
    for i in range(N):
        if filt[i]:
            D.at[inds[i], 'cic'] = CIC.iloc[i].categoria
            s = ' / '.join([str(CIC.iloc[i].subarea), str(CIC.iloc[i].tema)])
            D.at[inds[i], 'area'] = s

    ADD = CIC[~np.array(filt)]

    ADD = fill_empty_columns(ADD, D)
    ADD = ADD[list(D.columns)]  
    D = pd.concat([D, ADD], ignore_index=True)
    yield D     
 


# TRANSFORM: add common data
"""
S03_add_gender
S03_add_age
S03_clean_and_sort
"""

def S03_add_gender(*args):
    """
    STEP: S03_add_gender

    In this step, genders are assigned according to data from XXX

    | Columns:
    | 1)
    | 2)
    | 3)
    | 4)

    Returns:
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

def S03_add_age(*args):
    """
    STEP: S02_add_age

    In this step, age is computed and added.

    Columns:
    1) edad

    Notes:
    When the year of birth is not available, a relacion between the
    DNI and the age is fitted aud used to complete the data.
    DNI (Documento nacional de identidad) number is assigned
    correlatively after inscription of newborns, which is mandatory in
    Argentina.

    Returns:
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
    # 1.- select data
    filt_df = df['nac'].str.contains('arg')
    filt_df[filt_df.isna()] = False
    filt = filt_df.values

    Darg = df[filt & df.edad.notnull()]
    dft = Darg[Darg['dni'].between(1.e7, 4.e7) & Darg['edad'].between(20,70)]
    x = dft['dni']
    y = dft['edad']

    # 2.- fit model
    def age(dni, a, b, c):
        return a - b*dni*1.e-7 + c*(dni*1.e-7-2.5)**2
    x0 = [83, 16, 1.5]
    pars_age, cov = curve_fit(age, x, y, x0)

    # 3.- add regression of age for missing values
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

def S03_clean_and_sort(*args):
    """
    STEP: S02_clean_and_sort

    In this step, columns of the database are cleaned and sorted

    Returns:
    D: DataFrame containing the data

    """     
    D = args[0] 

    D['apellido'] = D.apellido.apply(str.lower)
    D['nombre'] = D.nombre.apply(str.lower)
    D['aff'] = D.aff.apply(ft_low)
    D['cic'] = D.cic.apply(ft_low)
    D['docencia'] = D.docencia.apply(ft_low)
    D['area'] = D.area.apply(ft_low)
    D['categoria'] = D.categoria.apply(ft_low)
    D['subarea'] = D.subarea.apply(ft_low)

    # apellido,nombre,ads_str,dni,fnac,ynac,aff,nac,aaa_soc,
    # cic,docencia,area,orcid,use_orcid,categoria,subarea,ue,l,
    # tema,sn,genero,edad

    #D.dni = D.dni.apply(lambda x: int(x) if pd.notna(x) else '')
    #D.edad = D.edad.apply(lambda x: int(x) if pd.notna(x) else '')
    #cols = ['apellido', 'nombre', 'genero', 'aff', 'lugar', 'aaa', 'area',
    #        'nac', 'dni', 'fnac', 'edad', 'cic', 'docencia', 'status']
    #D = D[cols] 
    yield D



# TRANSFORM: add publication data
"""
S04_pub_get_ads_entries
S04_pub_get_orcids
S04_pub_journal_index
S04_pub_clean_papers
S04_make_pages
S04_pub_value_added
"""

def S04_pub_get_ads_entries(*args):
    """
    STEP: S04_pub_get_ads_entries

    In this step, the lists of names and orcids are used to retrieve
    data from the Astronomical Data Service (ADS) using the ads
    package (https://ads.readthedocs.io/en/latest/)

    Returns:
    D: DataFrame containing the data
    This is the same object that enters the function. In addition, a file is
    saved for each author.

    """   
    D = args[0]

    # ADS: DOWNLOAD DATA (correr esto una sola vez)  / / / / / / / / warning
    fl = ['id', 'bibcode', 'abstract', 'title', 'citation_count',
          'orcid_pub', 'aff', 'author', 'citation', 'pub', 'reference',
          'first_author', 'author_count', 'orcid_user', 'metrics',
          'year', 'read_count', 'pubdate']
    rows_max = 300
    OPTS = {'rows': rows_max, 
            'fl': fl}
    orcid_cck = 'use_orcid' in D.columns
    if orcid_cck:
        D.use_orcid[D.use_orcid.isna()] = 0
    N = D.shape[0]

    print('GET ADS DATA')

    # ############################################## DOWNLOAD DATA      
    for i in range(N):
        print(i, N)
        x = D.iloc[i]
        ap = x.apellido.title()
        fname_ap = '_'.join(ap.split())
        nm = x.nombre
        fname_nm = ''.join([a[0].upper() for a in nm.split()])
        fname = '_'.join([fname_ap, fname_nm])
        auth = ', '.join([ap, getinitials(nm)])
        #print(F'{auth} --- {ap}, {nm}')

        if orcid_cck:
            if x.use_orcid:
                OPTS['orcid'] = orcid
            else:
                OPTS['author'] = auth
        else:
            OPTS['author'] = auth

        papers = list(ads.SearchQuery(**OPTS))
        filen = '../../data/interim/ADS/' + fname + '.pk'
        with open(filen, 'wb') as f:
            pickle.dump(papers, f)
    # ##########################################################

    yield D

def S04_pub_get_orcids(*args):
    """
    STEP: S04_pub_get_orcids

    In this step, orcids are guessed by downloading from orcid
    service.
    
    The following steps are in order:
    
    | 1) generate query
    | 2) download data
    | 3) check on ads
    | 4) clean
    | 5) get orcid best guess
    | 6) add guessed_orcid to dataframe.

    Returns:
    D: DataFrame containing the data

    """
    D = args[0]
    # PLACEHOLDER
    yield D

def S04_pub_journal_index(*args):
    """
    STEP: S04_pub_journal_index

    In this step, journals are assigned an index taken from the
    Scimago Journal Index (Guerrero-Botea & Moya-Anegón, 2021,
    Journal of infometrics, 6, 674)

    Returns:
    D: DataFrame containing the data (including journal index)

    """
    D = args[0]
    # PLACEHOLDER


    ###############################
    ###############################
    ###############################
        
    fileD = '../../data/pickles/papers_cleaned.pk'
    with open(fileD, 'rb') as f:
       papers = pickle.load(f)

    # JOURNALS DATA ····································
    stop_words = set(stopwords.words('english'))
    journals = []
    with open('../../data/external/scimagojr.csv', newline='') as csvfile:
        s = csv.reader(csvfile, delimiter=';')

        for row in s:
            jname = row[2].lower()
            word_tokens = word_tokenize(jname)
            fname = [w for w in word_tokens if w not in stop_words]
            sent1 = ' '.join(fname)
            sent1 = sent1.replace('/', '')
            row[2] = sent1
            journals.append(row)  


    # PUBLICATIONS DATA ································
    pubs = []
    for p in tqdm(papers):
        for ip in p:
            jname = ip.pub.lower()
            word_tokens = word_tokenize(jname)
            fname = [w for w in word_tokens if w not in stop_words]
            sent1 = ' '.join(fname)
            sent1 = sent1.replace('/', '')
            name = sent1 
            pubs.append(name)
    myset = set(pubs)
    ppubs = list(myset)  # lista de nombres de journals sin repeticion


    # MATCH ···············································
    match = 0
    jname = []
    jq = []
    for p in tqdm(ppubs):
        qs = []
        for Journal in journals:
            journal = Journal[2]
            s1 = similar(p, journal)
            s2 = jellyfish.jaro_winkler(p, journal)
            if s1 > 0.92 and s2 > 0.92:
                print(f'{s1:.2f} {s2:.2f} -- {p} -- {journal}')
                qs.append(Journal[6])
        if len(qs)>0:
            Q = min(qs)
            jname.append(p)
            jq.append(Q)


    fileD = '../../data/interim/Qs_saved.pk'
    with open(fileD, 'wb') as f:
       pickle.dump([jname, jq], f)
     
    ###############################
    ###############################
    ###############################

    yield D

def S04_pub_clean_papers(*args):
    D = args[0]

    # CARGAR MODELO :::::::::::::::::::::::::::::::::::::::::
    clf, scaler = load('../../models/SVM_model_pars.joblib')
                            

    # FILTRAR: calcular el filtro :::::::::::::::::::::::::
    lst = D.index
    apin = []
    for i in tqdm(lst): # LISTA DE AUTORES
        x = D.loc[i]
        saut = f'{x.apellido} {x.nombre}'
        ipin = []
        for ip in papers[i]:  # LISTA DE PAPERS
            ll = authmatch(x, ip)
            tst = np.array(ll[:6]).reshape(1, -1)
            tst = scaler.transform(tst)
            ipin.append(clf.predict(tst)[0])
        apin.append(ipin)

    fileD = '../../data/pickles/filter_saved.pk'
    with open(fileD, 'wb') as f:
       pickle.dump(apin, f)

    with open(fileD, 'rb') as f:
       apin = pickle.load(f)



    # FILTRAR: eliminar papers :::::::::::::::::::::::::
    for i in range(N):
        aux = [papers[i][k] for k in range(len(apin[i])) if apin[i][k]]
        papers[i] = aux.copy()

    fileD = '../../data/pickles/papers_cleaned.pk'
    with open(fileD, 'wb') as f:
       pickle.dump(papers, f)     

    yield D

def S04_make_pages(*args):
    """
    STEP: S04_make pages

    Generate web pages with the list of candidate publication entries. Each entry has a checkbox
    that, when marked, selects the entry for elimination of the list.
    The webpage allows check "by eye" the list of entries and to save a filter to further clean the 
    list of publications. Additionally, the page contains links to the ADSABS pages of each author,
    preselected with the following criteria:
    - less than 50 authors
    - refereed papers
    - Q1 journals

    When used, this function generates and writes 

    Returns:
    D: DataFrame containing the data (including journal index)
    """
    D = args[0]
    # PLACEHOLDER

#################################
#################################
#################################




    #---------------------------------------------------------

    def gen_spreadsheet(auth, papers):

        lst_title = []
        lst_auths = []
        lst_affs = []
        lst_año = []
        lst_journal = []
        lst_auth_aff = []
        lst_auth_nam = []
        lst_auth_selected = []
        lst_bibcode = []

        lst = range(len(papers))
        apos = auth.auth_pos

        s1 = 'https://ui.adsabs.harvard.edu/abs/'
        s2 = '/abstract'

        aind = np.arange(auth.Npapers)[auth.filter_papers]

        for i in lst:
            p = papers[i]

            aux = p.aff.copy()
            aux[auth.auth_pos[aind[i]]] = '<b>' + \
                                    aux[auth.auth_pos[aind[i]]] + \
                                    '</b>'
            lst_affs.append(aux)

            aux = p.author.copy()
            aux[auth.auth_pos[aind[i]]] = '<b>' + \
                                    aux[auth.auth_pos[aind[i]]] + \
                                    '</b>'
            lst_auths.append(aux)


            lst_title.append(p.title[0])
            lst_año.append(p.year)
            lst_journal.append(p.pub)
            lst_bibcode.append(f'{s1}{p.bibcode}{s2}')

            #lst_auth_selected.append(p.filter_authors)

            #k = apos[i]
            #lst_auth_aff.append(p.aff[k])
            #lst_auth_nam.append(p.author[k])

        df = pd.DataFrame({'Título': lst_title,
                           'Autores': lst_auths,
                           #'auth_name': lst_auth_nam,
                           'Afiliaciones': lst_affs,
                           #'auth_aff': lst_auth_aff,
                           'Año': lst_año,
                           'Journal': lst_journal,
                           'adsurl': lst_bibcode
                           })
                           #'selected': lst_auth_selected})
        return df
     
    #---------------------------------------------------------
     
    fileD = '../../data/pickles/D_selected.pk'
    with open(fileD, 'rb') as f:
       D = pickle.load(f)
    D['cic'].fillna(value='X', inplace=True)

    fileD = '../../data/pickles/papers_selected.pk'
    with open(fileD, 'rb') as f:
       papers = pickle.load(f)

    #---------------------------------------------------------

    source_dir = './'
    template_file = 'template.html'
    templateLoader = jinja2.FileSystemLoader(searchpath=source_dir)
     
    latex_jinja_env = jinja2.Environment(
        block_start_string=r"\BLOCK{",
        block_end_string='}',
        variable_start_string=r'\VAR{',
        variable_end_string='}',
        comment_start_string=r'\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
        loader=templateLoader
    )
    template_page = latex_jinja_env.get_template(template_file)

    #---------------------------------------------------------

    # checkboxes
    s1 = '<input type="checkbox" name="check'
    s2 = '" value="" /><br>'

    # urls
    s3 = '<a href="'
    s4 = '">link</a>'

    pd.options.display.html.border = 1

    for kounter, i in enumerate(D.index):
        auth = D.loc[i]

        print(i, auth.apellido)

        k = D.index.get_loc(i)
        p = papers[k]
        df = gen_spreadsheet(auth, p)

        df.sort_values(by=['Año'], axis='index', inplace=True)
        S = [f'{s1}{str(i+1).zfill(3)}{s2}' for i in range(df.shape[0])]
        df['exclude'] = S

        url = [f'{s3}{r}{s4}' for r in df.adsurl]
        df['linkurl'] = url
        title_links = df.apply(lambda x: x.linkurl.replace('link', x.Título), axis=1)
        if sum(auth.filter_papers)>0:
            df['title_links'] = title_links
        else:
            df['title_links'] = [] 
        df['counter'] = np.arange(1,df.shape[0]+1)

        dfo = df.iloc[:, [9,3,4,8,6,1,2]].copy()

        dfo = dfo.assign(Autores=dfo.Autores.apply(lambda x: '<br>'.join(x)))
        dfo = dfo.assign(Afiliaciones=dfo.Afiliaciones.apply(lambda x: '<br>'.join(x)))

        N = df.shape[0]

        #--- template
        str_io = StringIO()
        dfo.to_html(buf=str_io, index=False, index_names=False, escape=False)
        html_str = str_io.getvalue()

        fname = (f'../../data/ADS/htmls/{str(kounter).zfill(3)}_{str(i).zfill(3)}_'
                 f'{auth.apellido.replace(" ", "_")}_{auth.nombre[0]}.html')
        fout = f'{str(kounter).zfill(3)}_{str(i).zfill(3)}_{auth.apellido.replace(" ", "_")}_{auth.nombre[0]}.txt'

        filename = pathjoin(source_dir, fname)
        target = open(filename, 'w')
        target.write(template_page.render(N=N,
                                          html_str=html_str,
                                          auth=auth,
                                          filedata=fout))
        target.close()


     
#################################
#################################
#################################

    yield D

def S04_pub_value_added(*args):
    """
    STEP: S04_pub_value_added

    Returns:
    D: DataFrame containing the data (including journal index)
    """
    D = args[0]
    # PLACEHOLDER
    yield D




###### a la parte de analizar hacerla separada ##########




# LOAD
"""
Load data to data warehouse
"""

def load(*args):
    """
    STEP: S02_clean_and_sort

    In this step, columns of the database are cleaned and sorted

    | Columns:
    | 1)
    | 2)
    | 3)
    | 4)

    Returns:
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
    #
    fileD = '../../data/redux/D.xlsx'
    D.to_excel(fileD)


# PIPELINE
"""
Set data reduction pipeline using ETL data integration process.

TST_filter_subset
data_pipeline
"""

def TST_filter_subset(*args):
    D = args[0]
    D = D.iloc[400:420]
    yield D


# > > > PIPELINE < < <

def data_pipeline(**options):
    """
    This function builds the graph that needs to be executed.

    :return: bonobo.Graph

    """
    graph = bonobo.Graph()

    graph.add_chain(S01_read_aaa_table,
                    S02_add_OAC_data,
                    S02_add_IATE_data,
                    #S02_add_IALP_data,
                    #S02_add_GAE_data,
                    #S02_add_IAFE_data,
                    #S02_add_ICATE_data,
                    S02_add_CIC_data,
                    #
                    S03_add_gender,
                    S03_add_age,
                    S03_clean_and_sort,
                    TST_filter_subset,
                    ##
                    S04_pub_get_ads_entries,
                    #S04_pub_get_orcids,
                    S04_pub_clean_papers,
                    #S04_pub_journal_index,
                    #S04_pub_value_added,
                    load)

    return graph


"""
Debugging:

D = S01_read_aaa_table()
D = S02_add_OAC_data(next(D))
D = S02_add_IATE_data(next(D))
D = S02_add_IALP_data(next(D))
D = S02_add_GAE_data(next(D))
D = S02_add_IAFE_data(next(D))
D = S02_add_ICATE_data(next(D))
D = S02_add_CIC_data(next(D))
D = S03_add_gender(next(D))
D = S03_add_age(next(D))
D = S03_clean_and_sort(next(D))
D = S04_pub_get_ads_entries(next(D))
D = S04_pub_get_orcids(next(D))
D = S04_pub_journal_index(next(D))
D = S04_pub_value_added(next(D)) 

se puede interrumppir en cualquier lado y hacer D=next(D)

"""


def get_services(**options):
    """ This function builds the services dictionary, which is a
    simple dict of names-to-implementation used by bonobo for runtime
    injection.
    It will be used on top of the defaults provided by bonobo (fs,
    http, ...). You can override those defaults, or just let the
    framework define them. You can also define your own services and
    naming is up to you.

    Returns: 
       dict
    """
    return {}

if __name__ == '__main__':

    # Load parameters from config file
    inifile = '../../sets/set_experiment.ini'
    global config
    config = Parser(inifile)

    # run bonobo pipeline (default options)
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser) as options:
        bonobo.run(
                   data_pipeline(**options),
                   services=get_services(**options)
                  )
