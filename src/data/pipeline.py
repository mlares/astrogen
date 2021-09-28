import datetime
import time
import pandas as pd
import bonobo
import numpy as np
from dateutil.relativedelta import relativedelta
import numpy as np
from scipy.optimize import curve_fit
from astrogen_utils import bcolors, ds, ds1, ds2, get_gender2
from astrogen_utils import initials, getinitials, pickone
import pickle
import ads


# avoid SettingWithCopyWarning
# (see https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy)
pd.options.mode.chained_assignment = None


def get_filters_by_names(D, UE):
    """
    Parameters:
    -----------
    D: DataFrame, base data
    UE: DataFrame, data to be added

    Returns:
    --------
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

    Parameters:
    -----------
    tipo: type

    Returns:
    --------
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

    """
    for c, t in zip(df2.columns, df2.iloc[0]):
        if c not in df1.columns:
            df1[c] = set_empty_with_type(type(t))

    return df1

def ft_year(s):
    """
    Return the year from a datetime object, is possible,
    if not, returns -1
    """
    try:
        y=s.year
    except AttributeError:
        y=-1
    return y
 
def ft_low(s):
    """
    Return the affiliation in lower case format
    """
    if isinstance(s, str):
        y = s.lower()
    else:
        y = s
    return y



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

    Columns:
    1) apellido 
    2) nombre   
    3) ads_str: string to look for in ADS
    4) dni: documento nacional de identidad
    5) fnac: day of birth
    6) ynac: year of birth
    7) aff: affiliation
    8) nac: nacionality
    9) aaa_soc: aaa situation

    Returns:
    --------
    D: DataFrame containing the data

    Notes:
    ------
    aa_soc codes:
    B1   baja por fallecimiento
    B2   baja por renuncia no vinculada al alejamiento de la Astronomía
    B3   baja por desvinculación de la Astronomía (incluyendo renuncia)
    B4   baja por no haberse reempadronado al 01/01/2005
    B5   baja por morosidad en el pago
    B6   baja por expulsión, falta profesional grave
    L    licencia
    A1   activo
    Pf   profesional
    Ad   adherente
    Af   aficionado
    F    fallecido
    FP   fallecido a posteriori de su baja
    """
    D = pd.read_excel('../../data/raw/collect_AAA.xlsx')

    D['ynac'] = D.ynac.apply(ft_year)
    D['dni'] = D['dni'].apply(lambda x: x if np.isreal(x) else np.NaN)
 
    yield D


# TRANSFORM: add data from institutes
""" 
In these steps the following columns are added:
    - cic
    - docencia
    - area
    - orcid
    - use_orcid

The steps are contained in the following functions:
    - S02_add_OAC_data
    - S02_add_IATE_data
    - S02_add_UNLP_data
    - S02_add_ICATE_data
    - S02_add_GAE_data
    - S02_add_CIC_data
""" 

def S02_add_OAC_data(*args):
    """
    STEP: S02_add_OAC_data

    In this step, the database is combined with data from the OAC

    Columns:
    1) apellido  
    2) nombre    
    3) ads_str   
    4) dni
    5) ynac      
    6) cic (+)
    7) docencia (+)
    8) area (+)
    9) orcid (+)
    10) use_orcid (+)

    Returns:
    --------
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

    Columns:
    1) apellido  
    2) nombre    
    3) ads_str   
    4) ynac      
    5) cic (+)
    6) docencia (+)
    7) area (+)
    8) orcid (+)
    9) use_orcid (+)

    Returns:
    --------
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

    Columns: 
    1) apellido  
    2) nombre    
    3) ads_str   
    4) dni
    5) ynac      
    6) cic (+)
    7) docencia (+)
    8) area (+)
    9) orcid (+)
    10) use_orcid (+) 

    Returns:
    --------
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

    Columns:
    1) apellido  
    2) nombre    
    3) ads_str   
    4) dni
    5) ynac      
    6) cic (+)
    7) docencia (+)
    8) area (+)
    9) orcid (+)
    10) use_orcid (+) 

    Returns:
    --------
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

    Columns:
    1) apellido  
    2) nombre    
    3) ads_str   
    4) dni
    5) ynac      
    6) cic (+)
    7) docencia (+)
    8) area (+)
    9) orcid (+)
    10) use_orcid (+) 

    Returns:
    --------
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

    Columns:
    1) apellido  
    2) nombre    
    3) ads_str   
    4) dni
    5) ynac      
    6) cic (+)
    7) docencia (+)
    8) area (+)
    9) orcid (+)
    10) use_orcid (+) 

    Returns:
    --------
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

    Columns:
    1) apellido
    2) nombre
    3) categoria (+)
    4) area (+)
    5) subarea (+)
    6) ue (+)
    7) l (+)
    8) tema (+)
    9) sn (+)

    Returns:
    --------
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

def S03_add_age(*args):
    """
    STEP: S02_add_age

    In this step, age is computed and added.

    Columns:
    1) edad

    Notes:
    ------
    When the year of birth is not available, a relacion between the
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
    --------
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
S04_pub_value_added
"""

def S04_pub_get_ads_entries(*args):
    """
    STEP: S04_pub_get_ads_entries

    In this step, 

    Returns:
    --------
    D: DataFrame containing the data

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

    # ############################################## DOWNLOAD DATA      
    for i in range(N):
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
    D = args[0]






    yield D

def S04_pub_journal_index(*args):
    D = args[0]



    yield D

def S04_pub_value_added(*args):
    D = args[0]
    yield D



# LOAD
"""
Load data to data warehouse
"""

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
                    #S04_pub_journal_index,
                    #S04_pub_value_added,
                    load)

    return graph


"""
Como se hace esto???

D = S01_read_aaa_table()
D = S02_add_OAC_data(D)
D = S02_add_IATE_data(D)
D = S02_add_IALP_data(D)
D = S02_add_GAE_data(D)
D = S02_add_IAFE_data(D)
D = S02_add_ICATE_data(D)
D = S02_add_CIC_data(D)
D = S03_add_gender(D)
D = S03_add_age(D)
D = S03_clean_and_sort(D)
D = S04_pub_get_ads_entries(D)
D = S04_pub_get_orcids(D)
D = S04_pub_journal_index(D)
D = S04_pub_value_added(D)
load) 
"""


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
            data_pipeline(**options),
            services=get_services(**options)
        )
