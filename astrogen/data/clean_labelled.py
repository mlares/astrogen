import pickle
import pandas as pd
import sqlite3
from pipeline import *


with open('../../data/redux/astrogen_DB_labelled.pk', 'rb') as f:
    df = pickle.load(f)  

df.drop(['filter_papers'], axis=1, inplace=True)
df.drop(['conicet','ynac','use_orcid'], axis=1, inplace=True)

df.aff[df.aff==0] = None
df.LT_sigla[df.LT_sigla==0] = None

for i in df.index:
    cond1 = df.loc[i]['aff'] is not None
    cond2 = df.loc[i]['LT_sigla'] is not None
    if cond1 and cond2:
        df.loc[i]['aff'] = df.loc[i]['aff'] + df.loc[i]['LT_sigla']
    elif cond2:
        df.loc[i]['aff'] = df.loc[i]['LT_sigla']

df.drop(['LT_sigla'], axis=1, inplace=True)

for i in range(7,20):
    cname = 'cc' + str(i).zfill(2)
    df[cname] = df[cname].convert_dtypes().replace({np.nan: None})

for i in df.index:
    if df.loc[i].aff is not None:
        s = set(df.loc[i].aff.split(' '))
        l = ', '.join(list(s)).strip()
        df.at[i, 'aff'] = l

lst= ['auth_Q', 'cita_Q', 'pub_años', 'auth_pos', 'auth_num',
          'auth_inar', 'auth_citas']

df = df.drop(lst, axis=1)

#cols = df.columns.tolist()
#cc = [cols[19]] + cols[:4] + cols[17:19] + cols[20:] + cols[4:17]
cc = [22, 0, 1, 5, 6, 21, 2, 3, 24, 25, 23, 7, 8, 9, 10, 11, 12, 13,
        14, 15, 16, 17, 18, 19, 20]
df = df.iloc[:, cc]

# -> DB
fileD = '../../data/redux/astrogen_DB_labelled.xlsx'
df.to_excel(fileD)

fileD = '../../data/redux/astrogen_DB_labelled.csv'
df.to_csv(fileD)

conn = sqlite3.connect('../../data/redux/astrogen_DB_labelled.db')
c = conn.cursor()

script = 'CREATE TABLE IF NOT EXISTS people ('+', '.join(df.columns)+')'
c.execute(script)
conn.commit()
df.to_sql('people', conn, if_exists='replace', index = False)

conn.close()
