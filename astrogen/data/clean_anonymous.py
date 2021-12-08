import pickle
import pandas as pd
import sqlite3
from pipeline import *


with open('../../data/redux/astrogen_DB_labelled.pk', 'rb') as f:
    df = pickle.load(f)  

df.drop(['filter_papers'], axis=1, inplace=True)
#df.drop(['conicet','ynac','use_orcid'], axis=1, inplace=True)

#df.aff[df.aff==0] = None
#df.LT_sigla[df.LT_sigla==0] = None

#for i in df.index:
#    cond1 = df.loc[i]['aff'] is not None
#    cond2 = df.loc[i]['LT_sigla'] is not None
#    if cond1 and cond2:
#        df.loc[i]['aff'] = df.loc[i]['aff'] + df.loc[i]['LT_sigla']
#    elif cond2:
#        df.loc[i]['aff'] = df.loc[i]['LT_sigla']
#
#df.drop(['LT_sigla'], axis=1, inplace=True)

for i in range(2007,2021):
    cname = 'conicetcode' + str(i)
    #df[cname] = df[cname].apply(int)
    df[cname] = df[cname].convert_dtypes().replace({np.nan: None})


df.rename(columns={'conicetcode2007': 'cc07', 
                   'conicetcode2008': 'cc08',
                   'conicetcode2009': 'cc09',
                   'conicetcode2010': 'cc10',
                   'conicetcode2011': 'cc11',
                   'conicetcode2012': 'cc12',
                   'conicetcode2013': 'cc13',
                   'conicetcode2014': 'cc14',
                   'conicetcode2015': 'cc15',
                   'conicetcode2016': 'cc16',
                   'conicetcode2017': 'cc17',
                   'conicetcode2018': 'cc18',
                   'conicetcode2019': 'cc19',
                   'conicetcode2020': 'cc20'},
                   inplace=True)

#for i in df.index:
#    if df.loc[i].aff is not None:
#        s = set(df.loc[i].aff.split(' '))
#        l = ', '.join(list(s)).strip()
#        df.at[i, 'aff'] = l

lst= ['auth_Q', 'cita_Q', 'pub_años', 'auth_pos', 'auth_num',
          'auth_inar', 'auth_citas',
          #
          'apellido', 'nombre', 'aff', 'ynac', 'orcid', 'use_orcid',
          'conicet', 'LT_sigla']

df = df.drop(lst, axis=1)

cols = df.columns.tolist()
cc = [cols[16]] + cols[14:16] + cols[17:] + cols[:14]
df = df[cc]   



# -> DB
fileD = '../../data/redux/astrogen_DB_anonymous.xlsx'
df.to_excel(fileD)

fileD = '../../data/redux/astrogen_DB_anonymous.csv'
df.to_csv(fileD)

conn = sqlite3.connect('../../data/redux/astrogen_DB_anonymous.db')
c = conn.cursor()

script = 'CREATE TABLE IF NOT EXISTS people ('+', '.join(df.columns)+')'
c.execute(script)
conn.commit()
df.to_sql('people', conn, if_exists='replace', index = False)

conn.close()
