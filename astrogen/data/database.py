import pickle
import pandas as pd
import sqlite3


with open('../../data/redux/astrogen_DB.pk', 'rb') as f:
    df = pickle.load(f)

df.drop(['auth_Q', 'cita_Q',
    'pub_años', 'auth_pos', 'auth_num', 'auth_inar',
    'auth_citas', 'filter_authors', 'filter_papers'], axis=1,
    inplace=True)

conn = sqlite3.connect('../../data/redux/astrogen_DB.db')
c = conn.cursor()

script = 'CREATE TABLE IF NOT EXISTS sample (' + \
         ', '.join(df.columns) + ')'

c.execute(script)
conn.commit()
df.to_sql('sample', conn, if_exists='replace', index = False)



###############################################################
with open('../../data/redux/df14.pk', 'rb') as f:
    df = pickle.load(f)  

df.drop(['auth_Q', 'cita_Q',
    'pub_años', 'auth_pos', 'auth_num', 'auth_inar',
    'auth_citas'], axis=1,
    inplace=True)

script = 'CREATE TABLE IF NOT EXISTS full (' + \
         ', '.join(df.columns) + ')'

c.execute(script)
conn.commit()

df.to_sql('full', conn, if_exists='replace', index = False)
###############################################################

                



"""
PARA EXTRAER DATOS:

c.execute('''  
		SELECT * FROM products
		WHERE price = (SELECT max(price) FROM products)
          ''')

df = pd.DataFrame(c.fetchall(), columns=['product_name','price'])    
print (df)


"""


conn = sqlite3.connect('tst.db')
c = conn.cursor()
 
fl = ['id', 'bibcode', 'abstract', 'title', 'citation_count',
          'orcid_pub', 'aff', 'author', 'citation', 'pub', 'reference',
          'first_author', 'author_count', 'orcid_user', 
          'year', 'read_count', 'pubdate']

fls = ', '.join(fl)    


script = f'CREATE TABLE IF NOT EXISTS table1 ({fls})'
c.execute(script)
conn.commit()

#sql = """INSERT INTO table1(a, b, c) VALUES(10, 20, 30)"""
#c.execute(sql)
#conn.commit()
#
#
#q = 0
#s = 'asdd'
#r = 0.1
#
#sql = f'INSERT INTO table1({fls}) VALUES(, , , , , , , , , , ,)'
#c.execute(sql)
#conn.commit()




#%%%%%%%%%%%%%%%%%%%%%%%%

       
def insertMultipleRecords(recordList, sqliteConnection, fls):
    try:
        #sqliteConnection = sqlite3.connect('SQLite_Python.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        sqlite_insert_query = f"""INSERT INTO table1({fls}) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

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


def paper2tuple(i,x,p):
    a0 = i
    a00 = x.apellido
    if isinstance(p.title, list):
        a1 = p.title[0]
    else:
        a1 = ''
    a2 = p.abstract
    a3 = ''.join(p.author)
    a4 = ''.join(p.aff)
    a5 = p.author_count
    a6 = p.bibcode
    a7 = p.citation_count
    a8 = p.year
    a9 = p.pubdate
    t = tuple((a0, a00, a1, a2, a3, a4, a5, a6, a7, a8, a9))
    return t
 

conn = sqlite3.connect('tstp.db')
c = conn.cursor()

fl = ['ID', 'apellido', 'title', 'abstract', 'authors', 'affilliations', 'author_count',
      'bibcode', 'citation_count', 'year', 'pubdate']
fls = ', '.join(fl)    

script = f'CREATE TABLE IF NOT EXISTS table1 ({fls})'
c.execute(script)
conn.commit()

recordsToInsert = []

for i in range(500, 550):
    x = D.iloc[i]
    p = get_papers_from_df(x)
    for ip in p:
        tup = paper2tuple(i, x, ip)
        recordsToInsert.append(tup)

insertMultipleRecords(recordsToInsert, conn, fls)
