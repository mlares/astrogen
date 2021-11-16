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
import joblib
from io import StringIO
import jinja2
import sqlite3
import unicodedata
 
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import csv
#from difflib import SequenceMatcher
      
from astrogen_utils import bcolors, ds, ds1, ds2, get_gender2
from astrogen_utils import initials, getinitials, pickone, similar
 
# avoid SettingWithCopyWarning
# (see https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy)
pd.options.mode.chained_assignment = None
pd.options.display.html.border = 1
#pd.options.display.max_rows = None


def clean_accented(s):
     s1 = unicodedata.normalize("NFKD", s)
     s2 = s1.encode("ascii","ignore")
     s3 = s2.decode("ascii")
     return s3

def get_filters_by_names(D, UE):
    """
    Given two dataframes with "nombre" and "apellido" keys, 
    find the entries in the second dataframe (UE) that match 
    any entry in the first dataframe.

    Args:
    D: DataFrame, base data

    UE: DataFrame, data to be added

    Returns:
    filt: boolean array
    An ndarray of dimension len(D)

    inds: int ndarray

    """
    filt = []
    inds = []
    for i, (n1, a1) in enumerate(zip(UE['nombre'], UE['apellido'])):
        closest = 99
        for j, (n2, a2) in enumerate(zip(D['nombre'], D['apellido'])):

            aa1 = clean_accented(a1)
            aa2 = clean_accented(a2)
            nn1 = clean_accented(n1)
            nn2 = clean_accented(n2)

            d = ds2(aa1, aa2, nn1, nn2)
            if d < closest:
                closest = d
                ind = j
                nc2 = nn2
                ac2 = aa2
        cond = closest < 0.26
        cond = closest < 0.02
        filt.append(cond)
        inds.append(ind)

    filt = np.array(filt)
    inds = np.array(inds)
    return filt, inds

def get_filters_by_dnis(D, UE):
    """
    Given two dataframes with "dni" keys, 
    find the entries in the second dataframe (UE) that match 
    any entry in the first dataframe.

    Args:
    D: DataFrame, base data

    UE: DataFrame, data to be added

    Returns:
    filt: boolean array
    An ndarray of dimension len(D)

    inds: int ndarray

    """
    filt = [False]*UE.shape[0]
    inds = []
    for i, n1 in enumerate(UE['dni']):
        if n1 is np.nan: continue
        for j, n2 in enumerate(D['dni']):
            if n2 is np.nan: continue
            d = abs(n1-n2)
            if d < 1:
                break
        filt[i] = True
        inds.append(j)

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

    if len(aind)<1: # no hay papers que cumplan con los criterios
        df = pd.DataFrame({'Título': lst_title,
                           'Autores': lst_auths,
                           'Afiliaciones': lst_affs,
                           'Año': lst_año,
                           'Journal': lst_journal,
                           'adsurl': lst_bibcode
                          })
        return df

    for i in aind:
        p = papers[i]

        aux = p.aff.copy()
        aux[auth.auth_pos[i]] = '<b>' + \
                                aux[auth.auth_pos[i]] + \
                                '</b>'
        lst_affs.append(aux)

        aux = p.author.copy()
        aux[auth.auth_pos[i]] = '<b>' + \
                                aux[auth.auth_pos[i]] + \
                                '</b>'
        lst_auths.append(aux)

        if p.title is not None:
            lst_title.append(p.title[0])
        else:
            lst_title.append('')
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

def get_papers_from_df(x, clean=False):
    ap = x.apellido.title()
    fname_ap = '_'.join(ap.split())
    nm = x.nombre
    fname_nm = ''.join([a[0].upper() for a in nm.split()])
    fname = '_'.join([fname_ap, fname_nm])
    if clean:
        file_papers = '../../data/interim/ADS/' + fname + '_C1.pk' 
    else:
        file_papers = '../../data/interim/ADS/' + fname + '.pk' 
    with open(file_papers, 'rb') as f:
        papers = pickle.load(f)
    return papers

def ccats(c):
    """
    c is assumed a string
    sUPErior, pRINcipal, indepeNDIente, aDJUnto, asISTente, 
    POSdoctoral, doCTOral 
    """
    c = c.lower()
    if 'upe' in c:
        return '5'
    elif 'rin' in c:
        return '4'
    elif 'ndi' in c:
        return '3'
    elif 'dju' in c:
        return '2'
    elif 'ist' in c:
        return '1'
    elif 'pos' in c:
        return '0'
    elif 'cto' in c:
        return '-1'

def cic_category(c):
    """
    Categorize the stage in CONICET

    Paramerers
    ----------
    c: str

    Returns
    -------
    int: A number from the set {-1, 0, 1, 2, 3, 4, 5, 999}

    Notes
    -----
    -1: beca doctoral
    0: beca postdoctoral
    1: inv. asistente
    2: inv. adjunto
    3: inv. independiente
    4: inv. principal
    5: inv. superior
    999: inconsistent data
    None: missing data
    """
    if c is None:
        return
    L = c.split(',')
    if len(L)==1:
        return ccats(L[0])
    else:
        a = L[0].strip()
        b = L[1].strip()
        if ccats(a)==ccats(b):
            return ccats(a)
        elif len(a)==0:
            return ccats(b)
        elif len(b)==0:
            return ccats(a)
        elif (a.lower()=='beca') and (b.lower()=='doctorado'):
            return -1                     
        elif (b.lower()=='beca') and (a.lower()=='doctorado'):
            return -1
        else:
            return 999


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
    D = pd.read_excel('../../data/collect/collect_AAA.xlsx')

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
    UE = pd.read_excel('../../data/collect/collect_OAC.xlsx')
    UE.drop(UE.filter(regex="Unname"),axis=1, inplace=True)

    filt, inds = get_filters_by_names(D, UE)
    D = fill_empty_columns(D, UE)

    # TEST: coincidencias
    #for i, j in enumerate(inds):
    #   print(D.iloc[j].apellido, UE.iloc[i].apellido)

    # TEST: diferencias
    #for i, emb in enumerate(filt):
    #    if not emb:
    #        print(UE.iloc[i].apellido)


    N = len(filt)
    for i in range(N):
        if filt[i]:
            D.at[inds[i], 'cic'] = UE.iloc[i].cic
            D.at[inds[i], 'orcid'] = UE.iloc[i].orcid
            D.at[inds[i], 'area'] = UE.iloc[i].area
            D.at[inds[i], 'dni'] = UE.iloc[i].dni 
            D.at[inds[i], 'aff'] = D.at[inds[i], 'aff'] + ' OAC'
            D.at[inds[i], 'use_orcid'] = UE.iloc[i].use_orcid

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

    UE = pd.read_excel('../../data/collect/collect_IATE.xlsx')
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
            D.at[inds[i], 'use_orcid'] = UE.iloc[i].use_orcid

    # TEST \\\
    if 0>1:
        # TEST: coincidencias
        for i, j in enumerate(inds):
           print(i, filt[i], D.iloc[j].apellido, UE.iloc[i].apellido)

        # TEST: diferencias
        for i, emb in enumerate(filt):
            if not emb:
                print(i, emb, UE.iloc[i].apellido)  
    # TEST ///


    ADD = UE[~np.array(filt)]
    ADD = fill_empty_columns(ADD, D)
    ADD = ADD[list(D.columns)]  
    D = pd.concat([D, ADD], ignore_index=True)
    yield D

def f(*args):
    D = args[0] 
    UE = pd.read_excel('../../data/collect/collect_IATE.xlsx')
    UE.drop(UE.filter(regex="Unname"),axis=1, inplace=True)
    #filt, inds = get_filters_by_names(D, UE)
    #D = fill_empty_columns(D, UE)
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
    UE = pd.read_excel('../../data/collect/collect_ICATE.xlsx')
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
            D.at[inds[i], 'use_orcid'] = UE.iloc[i].use_orcid


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
    UE = pd.read_excel('../../data/collect/collect_IALP.xlsx')
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
            D.at[inds[i], 'aff'] = D.at[inds[i], 'aff'] + ' IALP' 
            D.at[inds[i], 'use_orcid'] = UE.iloc[i].use_orcid

    ADD = UE[~np.array(filt)]
    ADD = fill_empty_columns(ADD, D)
    ADD = ADD[list(D.columns)]  
    D = pd.concat([D, ADD], ignore_index=True)
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
    UE = pd.read_excel('../../data/collect/collect_IAFE.xlsx')
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
            D.at[inds[i], 'use_orcid'] = UE.iloc[i].use_orcid

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
    UE = pd.read_excel('../../data/collect/collect_GAE.xlsx')
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
            D.at[inds[i], 'use_orcid'] = UE.iloc[i].use_orcid

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
    STEP: S03_add_CIC_data

    In this step, the database is combined with data from the GAE

    | Columns:
    | 1) apellido
    | 2) nombre
    | 3) conicet (+)
    | 4) area (+)
    | 5) subarea (+)
    | 6) ue (+)
    | 7) l (+)
    | 8) tema (+)
    | 9) sn (+)

    Returns:
    D: DataFrame containing the data

    Notes:
    La columna "cic" puede tener dos entradas, ya que a la categoría
    indicada en las planillas de institutos se le suma la categoría
    de la planilla de conicet.

    """     
    D = args[0] 
    CIC = pd.read_excel('../../data/collect/collect_CIC.xlsx')
    CIC.drop(CIC.filter(regex="Unname"),axis=1, inplace=True)

    filt, inds = get_filters_by_names(D, CIC)
    D = fill_empty_columns(D, CIC)
 
    N = len(filt)
    for i in range(N):
        if filt[i]:
            a = D.at[inds[i], 'cic']
            b = CIC.iloc[i].conicet
            if isinstance(a, str) and isinstance(b, str):
                addc = ', '.join([a, b])
            elif isinstance(b, str):
                addc = b
            else:
                addc = a
            D.at[inds[i], 'cic'] = addc
            s = ' / '.join([str(CIC.iloc[i].subarea), str(CIC.iloc[i].tema)])
            D.at[inds[i], 'area'] = s

    ADD = CIC[~np.array(filt)]
    ADD = fill_empty_columns(ADD, D)
    ADD = ADD[list(D.columns)]  
    D = pd.concat([D, ADD], ignore_index=True)
    yield D     

def S02_add_CONICET_data(*args):
    """
    STEP: S03_add_OAC_data

    In this step, the database is combined with data from the GAE

    | Columns:
    | 1) apellido
    | 2) nombre
    | 3) conicet (+)
    | 4) area (+)
    | 5) subarea (+)
    | 6) ue (+)
    | 7) l (+)
    | 8) tema (+)
    | 9) sn (+)

    Returns:
    D: DataFrame containing the data

    Notes:
    La columna "cic" puede tener dos entradas, ya que a la categoría
    indicada en las planillas de institutos se le suma la categoría
    de la planilla de conicet.

    """     
    D = args[0] 
    CIC = pd.read_excel('../../data/collect/collect_conicet2020.xlsx')
    CIC.drop(CIC.filter(regex="Unname"),axis=1, inplace=True)

    filt, inds = get_filters_by_names(D, CIC)
    D = fill_empty_columns(D, CIC)
 
    N = len(filt)
    for i in range(N):
        if filt[i]:
            b = CIC.iloc[i].conicet
            D.at[inds[i], 'cic'] = b
            D.at[inds[i], 'conicet'] = b

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

    ages = pd.read_excel('../../data/collect/collect_age.xlsx')

    df['fnac'] = pd.to_datetime(df['fnac'], errors='coerce')
    edad = []
    for day in df['fnac']:
        if pd.isnull(day):
            edad.append(-1)
        else:
            edad.append(relativedelta(today, day).years)

    df['fnac'] = df['fnac'].dt.strftime("%Y")
    df['edad'] = edad

    # Search for existing age or DNI ---------------
    nms = [[[]]*4, [[]]*4]
    for i in tqdm(df.index):
        x = df.iloc[i]
        if x.fnac is not np.nan:
            continue
        nms[0][0:2] = re_names(x.apellido)
        nms[0][2:4] = re_names(x.nombre)        
        for j in ages.index:
            y = ages.iloc[j]
            nms[1][0:2] = re_names(y.apellido)
            nms[1][2:4] = re_names(y.nombre)
            ll = aut_compare(*nms)
            m = ll[0]>0.9 and ll[1]>0.9 and ll[2]<0.1
            if m:
                # 1) tiene la fecha de nacimietnto?
                if y.ynac is not np.nan:
                    df.iloc[i].ynac = y.ynac
                # 2) tiene la edad?
                elif y.dni is not np.nan:
                    df.iloc[i].dni = y.dni

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


    # Ahora revisar la lista de edades de conicet
    CIC = pd.read_excel('../../data/collect/collect_conicet2020.xlsx')
    CIC.drop(CIC.filter(regex="Unname"),axis=1, inplace=True)
    filt, inds = get_filters_by_names(df, CIC)
    df = fill_empty_columns(df, CIC)
    N = len(filt)
    for i in range(N):
        if filt[i]:
            b = CIC.iloc[i].ynac
            df.at[inds[i], 'ynac'] = b

    yield df

def S03_clean_and_sort(*args):
    """
    STEP: S02_clean_and_sort

    In this step, columns of the database are cleaned and sorted
    - columns changed to lower case
    - age to type integer
    - deceased astronomers are eliminated
    - year of birth to integer
    - index created to assign a unique ID to each author
    - columns are arranged for easier analysis

    Returns:
    D: DataFrame containing the data

    """     
    D = args[0] 

    # Fill missing data with None -> Null in SQL
    aux = D.replace({'': None})
    aux = aux.replace({np.nan: None})
    D = aux

    D['apellido'] = D.apellido.apply(str.lower)
    D['nombre'] = D.nombre.apply(str.lower)
    D['aff'] = D.aff.apply(ft_low)
    D['cic'] = D.cic.apply(ft_low)
    D['docencia'] = D.docencia.apply(ft_low)

    if 'area' in D:
        D['area'] = D.area.apply(ft_low)
    if 'conicet' in D:
        D['conicet'] = D.conicet.apply(ft_low)
    if 'subarea' in D:
        D['subarea'] = D.subarea.apply(ft_low)

    D['edad'] = D['edad'].fillna('999').astype(int).replace({999: None})

    D['cic'] = D.cic.apply(cic_category)
    D['conicet'] = D.conicet.apply(cic_category)

    # filter deceased (data from AAA)
    # aaa_soc = F, FP or B1
    cond1 = D.aaa_soc.str.strip()=='F'
    cond2 = D.aaa_soc.str.strip()=='FP'
    cond3 = D.aaa_soc.str.strip()=='B1'
    cond = ~(cond1 | cond2 | cond3)
    D = D[cond]

    # use_orcid -> bool
    D = D.replace({np.nan: 0})
    D.use_orcid = D.use_orcid.astype(bool)

    # ynac -> int
    D.ynac = D.ynac.astype(int)

    # Add INDEX
    D.reset_index(drop=True, inplace=True)
    D['ID'] = D.index


    colsout = ['ads_str', 'dni', 'fnac', 'nac',  'aaa_soc', 
               'docencia', 'area', 'cic', 'cic_code', 'sexo']

    D.drop(colsout, axis=1, inplace=True)  

    yield D


# TRANSFORM: add publication data
"""
S04_pub_get_orcids
S04_pub_get_ads_entries
S04_pub_clean_papers
S04_pub_journal_index
S04_make_pages
S04_pub_value_added
"""

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

        OPTS = {'rows': rows_max, 'fl': fl}
        if orcid_cck and x.use_orcid:
            s = x.orcid
            orcid_number = s[s.find('0'):]
            OPTS['orcid'] = orcid_number
        else:
            OPTS['author'] = auth

        filen = '../../data/interim/ADS/' + fname + '.pk'
        # download only if file does not exist:
        if not path.isfile(filen):
            print(f'writing... {filen}')
            apapers = list(ads.SearchQuery(**OPTS))
            print(f'# papers: {len(apapers)}')
            with open(filen, 'wb') as f:
                pickle.dump(apapers, f)

    # ##########################################################

    yield D

def S04_pub_clean_papers(*args):
    D = args[0]
    
    # CARGAR MODELO :::::::::::::::::::::::::::::::::::::::::
    clf, scaler = joblib.load('../../models/SVM_model_pars.joblib')
                            
    # FILTRAR: calcular el filtro :::::::::::::::::::::::::
    lst = D.index
    apin = []
    for i in tqdm(lst): # LISTA DE AUTORES
        x = D.loc[i]

        ap = x.apellido.title()
        fname_ap = '_'.join(ap.split())
        nm = x.nombre
        fname_nm = ''.join([a[0].upper() for a in nm.split()])
        fname = '_'.join([fname_ap, fname_nm])
        file_papers = '../../data/interim/ADS/' + fname + '.pk' 

        with open(file_papers, 'rb') as f:
            apapers = pickle.load(f)

        ipin = [] # index paper in
        for ip in apapers:  # LISTA DE PAPERS
            ll = authmatch(x, ip)
            tst = np.array(ll[:6]).reshape(1, -1)
            tst = scaler.transform(tst)
            pred = clf.predict(tst)[0]

            # BAAA appears as:
            # Boletin de la Asociacion Argentina de Astronomia La Plata Argentina
            notbaaa = not 'rgentina' in ip.pub

            includepaper = pred and notbaaa
            ipin.append(includepaper)

        papers = [apapers[k] for k in range(len(ipin)) if ipin[k]]

        file_papers_out = '../../data/interim/ADS/' + fname + '_C1.pk' 
        with open(file_papers_out, 'wb') as f:
           pickle.dump(papers, f)     

    yield D

def S04_pub_filter_criteria(*args):
    """
    CRITERIA:

    --- AUTORES
    1 / Al menos un paper publicado en Argentina en los últimos 3 años
    2 / Edad entre 25 y 75 años
    3 / Fracción de papers Q1 publicados en Argentina mayor al 75%

    --- PAPERS
    4 / Menos de 50 autores
    5 / Revistas Q1
    """
    D = args[0]

    # -----  -----  -----  -----  -----  -----  -----  -----  FILTER AUTHORS
    # rango de edad
    D.edad.fillna(0, inplace=True)
    f_edad = D.edad.between(25, 80)

    # fraccion de papers con afiliación en Argentina
    f_ar = D.apply(lambda x: x.auth_inar.count(1)/max(x.Npapers, 1), axis=1)

    # fraccion de papers Q1 con afiliación en Argentina
    def q1frac(series):
         n = sum(np.logical_and(np.array(series.auth_inar)==1, 
                                np.array(series.auth_Q)==1))
         d = max(sum(np.array(series.auth_Q)==1),1)
         z = n/d
         return z
    f_arq1 = D.apply(q1frac, axis=1)
    f_arq1 = f_arq1 > 0.75
    # arreglar a mano algunos autores:
    f_arq1[372] = True  # merchan, hay otro merchan afuera


    # año de la ultima publicación (activo en los ultimos 5 años)
    f_last = D.pub_años.apply(lambda x: max(x)>2016 if len(x)>0 else 0)

    # elegir f_ar o f_arq1 para tomar papers Q1
    #filter_authors = f_edad | f_last
    filter_authors = f_edad & f_last & f_arq1

    # TEST / / / / / / / / / / / / / /   (borrar)
    #filter_authors = np.logical_or(filter_authors, True)
    # TEST / / / / / / / / / / / / / / 

    D['filter_authors'] = filter_authors
    D['ID'] = range(D.shape[0])
    D_selected = D[D.filter_authors].copy()

    # -----  -----  -----  -----  -----  -----  -----  -----  FILTER PAPERS

    # limitar el numero de autores
    Nmax = 50
    f_lessauth = D_selected.auth_num.apply(lambda x: np.array(x)<=Nmax)

    # papers que son Q1
    f_Q1 = D_selected.auth_Q.apply(lambda x: np.array(x)==1)

    # papers con menos de 50 autores en revistas Q1
    filter_papers =  D_selected.apply(lambda x: 
                             np.logical_and(np.array(x['auth_num'])<50, 
                                            np.array(x['auth_Q'])==1), axis=1)

    # TEST / / / / / / / / / / / / / /  (borrar)
    #filter_papers = D_selected.apply(lambda x: [True for i in
    #    range(x.Npapers)], axis=1)
    # TEST / / / / / / / / / / / / / / 

    if len(filter_papers)==0:
        filter_papers = D_selected.apply(lambda x: [True for i in
            range(x.Npapers)], axis=1)
    D_selected['filter_papers'] = filter_papers

    yield D_selected

# -> auth_Q
def S04_gen_journal_index(*args):
    """
    STEP: S04_gen_journal_index

    Create a table with:
    1) journal name
    2) journal Q

    for all the journals in the papers list.
    This function must be run one time only, to generate the 
    """
    D = args[0]

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

    jnames = []
    jqs = []
    lst = D.index
    apin = []
    for i in tqdm(lst): # LISTA DE AUTORES
        x = D.loc[i]
        papers = get_papers_from_df(x)

        # PUBLICATIONS DATA ································
        # la lista de todos los journals para este autor
        pubs = []
        for ip in papers:
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
        for p in ppubs:
            qs = []
            for Journal in journals:
                journal = Journal[2]
                s1 = similar(p, journal)
                s2 = jellyfish.jaro_winkler(p, journal)
                if s1 > 0.92 and s2 > 0.92:
                    #print(f'{s1:.2f} {s2:.2f} -- {p} -- {journal}')
                    qs.append(Journal[6])
            if len(qs)>0:
                Q = min(qs)
                jname.append(p)
                Qnum = int(Q[1]) if len(Q)>1 else 0
                jq.append(Qnum)

        # la lista unica de journals y sus Qs
        jnames.append(jname)
        jqs.append(jq)

    fileD = '../../data/interim/SJR/Qs_saved_individual.pk'
    with open(fileD, 'wb') as f:
        pickle.dump([jnames, jqs], f)


    ujnames = []
    ujqs = []

    inn = ''

    for n, q in zip(jnames, jqs):
        for i_n, i_q in zip(n, q):

           if i_n in inn:
               continue
           else:
               inn += i_n
               ujnames.append(i_n)
               ujqs.append(i_q)   
    
    fileD = '../../data/interim/SJR/Qs_saved.pk'
    with open(fileD, 'wb') as f:
        pickle.dump([ujnames, ujqs], f)

    return None

def S04_sort_journal_index(*args):
    """
    This is a utility function that can be used 
    to improve the performance of step S04_pub_journal_index
    """
    fileD = '../../data/interim/SJR/Qs_saved.pk'
    with open(fileD, 'rb') as f:
       jname, jq = pickle.load(f) 


    f=open('j.txt', 'r')
    for a, b in zip(jname, jq):
        f.write(jname + ', ' + str(jq))

    # ordenar a mano las revistas más usadas !!!

    f=open('j.txt', 'r')
    jname = []
    jq = []

    for l in f.readlines():
        a, b = l.split(',')[:2]
        jname.append(a)
        jq.append(int(b))
    f.close()

    fileD = '../../data/interim/SJR/Qs_saved_ordered.pk'
    with open(fileD, 'wb') as f:
        pickle.dump([jname, jq], f)
                                  
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

    stop_words = set(stopwords.words('english'))
    fileD = '../../data/interim/SJR/Qs_saved_ordered.pk'
    with open(fileD, 'rb') as f:
       jname, jq = pickle.load(f)

    N = D.shape[0]
    add_auth_Q = []
    add_cita_N = []

    for i in tqdm(range(N)):
        x = D.iloc[i]
        p = get_papers_from_df(x)
        auth_Q = []
        cita_N = []

        for ip in p:

            jn = ip.pub.lower()
            word_tokens = word_tokenize(jn)
            fname = [w for w in word_tokens if w not in stop_words]
            sent1 = ' '.join(fname)
            journalname = sent1.replace('/', '')
            s1m = 0
            s2m = 0

            for j, q in zip(jname, jq):
                s1 = similar(j, journalname)
                s2 = jellyfish.jaro_winkler(j, journalname)
                if s1 > s1m and s2 > s2m:
                    s1m, s2m = s1, s2
                    Q = q
                if s1>0.99 and s2>0.99:
                    break

            if s1m<0.92 or s2m<0.92:
                Q = 0
            auth_Q.append(Q)
            cita_N.append(ip.citation_count)

        add_auth_Q.append(auth_Q)
        add_cita_N.append(cita_N)

    D['auth_Q'] = add_auth_Q
    D['cita_Q'] = add_cita_N

    H = []
    for i in tqdm(range(N)):
        x = D.iloc[i]
        c = np.array(x.cita_Q)
        c = c[c != np.array(None)]
        c.sort()
        c = np.flip(c)

        Hindex = 0
        for i, cc in enumerate(c):
            if cc is None:
                pass
            else:
                if cc<i:
                    Hindex = i
                    break
        H.append(Hindex)

    D['Hindex'] = H

    A_add = []
    for i in tqdm(range(N)):
        x = D.iloc[i]

        p = get_papers_from_df(x)

        A = []
        for ip in p:
            A.append(int(ip.year))
        A_add.append(A)

    D['pub_años'] = A_add

    yield D

# -> auth_inar
def S04_pub_add_metrics(*args):
    D = args[0]

    N = D.shape[0]

    add_auth_pos = []
    add_auth_num = []
    add_auth_citas = []
    add_auth_años = []
    add_auth_inar = []
    add_auth_Npprs = []
    add_coauth_inar = []

    for i in tqdm(range(N)):
        x = D.iloc[i]

        ap = x.apellido.title()
        nm = x.nombre
        auth = ', '.join([ap, getinitials(nm)]) 

        p = get_papers_from_df(x)

        add_auth_Npprs.append(len(p))
        Npapers = 0
        k = 0
        auth_pos = []
        auth_num = []
        auth_año = []
        auth_citas = []
        auth_inar = []
        coauth_inar = []
        for ip in p:

            k = k+1
            t = ip.title
            a = ip.author
            j = ip.aff
            p = ip.pub
            dmin = 99
            ak = 0
            for au, af in zip(a, j):
                nl = au.split(',')
                if len(nl)==2:
                    au_surname, au_name = nl
                elif len(nl)>2:
                    au_surname = nl[0]
                    au_name = ''.join(nl[1:])
                else:
                    au_surname = nl[0]
                    au_name = ''
                aut1 = ', '.join([ap, getinitials(nm)])
                aut2 = ', '.join([au_surname, getinitials(au_name)])
                d = 1 - difflib.SequenceMatcher(None, aut1, aut2,).ratio()
                if d<dmin:
                    dmin = d
                    kmin = ak
                ak +=1
                #if 'entina' in af.lower():

            if 'entina' in j[kmin].lower():
                auth_inar.append(1)
            elif (af=='-') or (af==''):
                auth_inar.append(2)
            else:
                auth_inar.append(0)

            auth_pos.append(kmin)
            auth_num.append(ip.author_count)
            auth_citas.append(ip.citation_count)
            auth_año.append(int(ip.year))

        # columnas del DF para agregar
        add_auth_pos.append(auth_pos)
        add_auth_num.append(auth_num)
        add_auth_inar.append(auth_inar)
        add_auth_citas.append(auth_citas)

    D['Npapers'] = add_auth_Npprs
    D['auth_pos'] = add_auth_pos
    D['auth_num'] = add_auth_num
    D['auth_inar'] = add_auth_inar
    D['auth_citas'] = add_auth_citas
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

    # Prepare template
    #---------------------------------------------------------
    source_dir = '../../models/'
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

    # checkboxes
    s1 = '<input type="checkbox" name="check'
    s2 = '" value="" /><br>'
    # urls
    s3 = '<a href="'
    s4 = '">'
    s5 = '</a>'

    source_dir = '../../data/interim/htmls/'
    for kounter, i in tqdm(enumerate(D.index)):

        auth = D.loc[i]
        p = get_papers_from_df(auth)
        df = gen_spreadsheet(auth, p)

        df.sort_values(by=['Año'], axis='index', inplace=True)
        S = [f'{s1}{str(i+1).zfill(3)}{s2}' for i in range(df.shape[0])]
        df['exclude'] = S

        url = [f'{s3}{r}{s4}{t}{s5}' for r, t in zip(df.adsurl, df.Título)]
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

        fname = (f'{str(kounter).zfill(3)}_{str(i).zfill(3)}_'
                 f'{auth.apellido.replace(" ", "_")}_{auth.nombre[0]}.html')
        fout = f'{str(kounter).zfill(3)}_{str(i).zfill(3)}_{auth.apellido.replace(" ", "_")}_{auth.nombre[0]}.txt'

        filename = pathjoin(source_dir, fname)
        target = open(filename, 'w')
        target.write(template_page.render(N=N,
                                          html_str=html_str,
                                          auth=auth,
                                          filedata=fout))
        target.close()

    yield D


# LOAD
"""
Load data to data warehouse
"""

def load_final(*args):
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
    fileD = '../../data/redux/astrogen_DB.pk'
    with open(fileD, 'wb') as f:
       pickle.dump(D, f)

    #
    fileD = '../../data/redux/astrogen_DB.csv'
    with open(fileD, 'w') as f:
       D.to_csv(f)
    #
    fileD = '../../data/redux/astrogen_DB.xlsx'
    D.to_excel(fileD)

# PIPELINE
"""
Set data reduction pipeline using ETL data integration process.

TST_filter_subset
data_pipeline
"""

def TST_filter_subset(*args):
    D = args[0]
    D = D.iloc[377:387]
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
                    S02_add_IALP_data,
                    S02_add_GAE_data,
                    S02_add_IAFE_data,
                    S02_add_ICATE_data,
                    ##
                    S02_add_CONICET_data,
                    #S02_add_CIC_data,
                    ##
                    S03_add_gender,
                    S03_add_age,
                    S03_clean_and_sort,
                    #TST_filter_subset,
                    ##
                    S04_pub_get_ads_entries,
                    S04_pub_clean_papers,
                    S04_pub_journal_index,
                    S04_pub_add_metrics,
                    S04_pub_filter_criteria,
                    S04_make_pages,
                    load_final)

    return graph


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

if __name__ == '__main__' and '__file__' in globals():

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

"""
Desired outputs:

the final database, in:
    csv
    xlsx
    db

the anonymized database, in:
    csv
    xlsx
    db

"""
