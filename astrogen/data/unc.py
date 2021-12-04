import pandas as pd
import numpy as np
import sqlite3

cnames = ['year_in', 'mi', 'fi', 'me', 'fe']
opts = {'skiprows': 1,
        'names': cnames, 
        'usecols': [0,2,3,6,7]}

D = []
for y in range(2006,2021):
    df = pd.read_excel('../../data/collect/famaf-astronomia.xlsx',
                       sheet_name=str(y), **opts)
    df['year'] = [y]*df.shape[0]
    D.append(df)
dd = pd.concat(D)

dd['duracion'] = dd.year - dd.year_in
dd = dd.dropna(axis=0, thresh=4)
dd.duracion = dd.duracion.astype(int)
dd.mi = dd.mi.astype(int)
dd.fi = dd.fi.astype(int)
dd.me = dd.me.astype(int)
dd.fe = dd.fe.astype(int)
dd.year_in = dd.year_in.astype(int)



# Incorporar a la base de datos

# -> DB
conn = sqlite3.connect('../../data/redux/astrogen_DB_anonymized.db')
c = conn.cursor()

script = 'CREATE TABLE IF NOT EXISTS famaf ('+', '.join(df.columns)+')'
c.execute(script)
conn.commit()
dd.to_sql('famaf', conn, if_exists='replace', index = False)

conn.close() 
