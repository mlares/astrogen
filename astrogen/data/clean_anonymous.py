import pickle
import pandas as pd
import sqlite3
from pipeline import *


with open('../../data/redux/astrogen_DB_labelled.pk', 'rb') as f:
    df = pickle.load(f)  

df.drop(['filter_papers'], axis=1, inplace=True)

for i in range(7,21):
    cname = 'cc' + str(i).zfill(2)
    df[cname] = df[cname].convert_dtypes().replace({np.nan: None})

lst= ['auth_Q', 'cita_Q', 'pub_años', 'auth_pos', 'auth_num',
          'auth_inar', 'auth_citas',
          'apellido', 'nombre', 'aff', 'ynac', 'orcid', 'use_orcid',
          'conicet', 'LT_sigla']

df = df.drop(lst, axis=1)

#cols = df.columns.tolist()
#cc = [cols[16]] + cols[14:16] + cols[17:] + cols[:14]
#df = df[cc]   

cc = [18, 17, 1, 20, 21, 19, 3,4,5,6,7,8,9,10,11,12,13,14,15,16]
df = df.iloc[:, cc]

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
