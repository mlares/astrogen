import pickle
import pandas as pd
import sqlite3
from pipeline import *


with open('../../data/redux/astrogen_DB_labelled.pk', 'rb') as f:
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


def paper2tuple_anonymized(auth, p, k):
    a1 = int(auth.ID)
    a2 = p.pub
    a3 = int(auth.auth_Q[k])
    a4 = int(p.year)
    a10 = int(p.citation_count)
    a11 = int(p.author_count)
    a12 = int(auth.auth_pos[k])
    a13 = int(auth.auth_inar[k])
    a14 = bool(auth.filter_papers.reshape([-1])[k])
    a14 = 1 if a14 else 0

    t = tuple((a1, a2, a3, a4,
               a10, a11, a12, a13, a14))
    return t


conn = sqlite3.connect('../../data/redux/astrogen_DB_anonymous.db')
c = conn.cursor()

fl = ['ID',
      'journal',
      'journal_Q',
      'year',
      'citation_count', 
      'author_count',
      'author_pos',
      'inar',
      'filter']
fls = ', '.join(fl)    

script = f'CREATE TABLE IF NOT EXISTS papers ({fls})'
c.execute(script)
conn.commit()

recordsToInsert = []

for i in df.index:
    x = df.loc[i]
    p = get_papers_from_df(x)
    for k, ip in enumerate(p):
        tup = paper2tuple_anonymized(x, ip, k)
        recordsToInsert.append(tup)

insertMultipleRecords(recordsToInsert, conn, fls)

conn.commit()

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
