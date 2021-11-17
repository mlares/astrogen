import pickle
import pandas as pd
import sqlite3
from pipeline import *


with open('../../data/redux/astrogen_DB.pk', 'rb') as f:
    df = pickle.load(f)


def insertMultipleRecords(recordList, sqliteConnection, fls):
    try:
        #sqliteConnection = sqlite3.connect('SQLite_Python.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        qm = ', '.join(['?']*len(fls.split(',')))
        sqlite_insert_query = f"""INSERT INTO papers({fls}) 
                          VALUES ({qm});"""

        cursor.executemany(sqlite_insert_query, recordList)
        sqliteConnection.commit()
        print("Total", cursor.rowcount, "Records inserted successfully into SqliteDb_developers table")
        sqliteConnection.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert multiple records into sqlite table", error)
    #finally:
    #    if sqliteConnection:
    #        sqliteConnection.close()
    #        print("The SQLite connection is closed")


def paper2tuple(auth, p, k):
    a1 = int(auth.ID)
    a2 = auth.apellido
    if isinstance(p.title, list):
        a3 = p.title[0]
    else:
        a3 = ''
    a4 = p.abstract
    a5 = ', '.join(p.author)
    a6 = ', '.join(p.aff)
    a7 = p.author_count
    a8 = p.bibcode
    a9 = p.citation_count
    a10 = p.year
    a11 = p.pubdate
    a12 = auth.auth_Q[k]
    a13 = auth.cita_Q[k]
    a14 = auth.auth_pos[k]
    a15 = auth.auth_num[k]
    a16 = auth.auth_inar[k]
    a17 = auth.filter_papers[k]
    a17 = 1 if a17 else 0

    t = tuple((a1, a2, a3, a4, a5, a6, a7, a8, a9,
               a10, a11, a12, a13, a14, a15, a16, a17))
    return t
 

conn = sqlite3.connect('../../data/redux/astrogen_DB_papers.db')
c = conn.cursor()

fl = ['ID', 'apellido', 'title', 'abstract', 'authors',
      'affilliations', 'author_count', 'bibcode', 'citation_count', 'year',
      'pubdate', 'Q', 'citations', 'position', 'Nauth',
      'inar', 'filter']
fls = ', '.join(fl)    

script = f'CREATE TABLE IF NOT EXISTS papers ({fls})'
c.execute(script)
conn.commit()

recordsToInsert = []

for i in df.index:
    x = df.loc[i]
    p = get_papers_from_df(x)
    for k, ip in enumerate(p):
        tup = paper2tuple(x, ip, k)
        recordsToInsert.append(tup)

insertMultipleRecords(recordsToInsert, conn, fls)

conn.close()

"""
PARA EXTRAER DATOS:

c.execute('''  
		SELECT * FROM products
		WHERE price = (SELECT max(price) FROM products)
          ''')

df = pd.DataFrame(c.fetchall(), columns=['product_name','price'])    
print (df)


"""
 
