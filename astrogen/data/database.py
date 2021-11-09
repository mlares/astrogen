import pickle
import pandas as pd
import sqlite3


with open('df14.pk', 'rb') as f:
    df = pickle.load(f)

df.drop(['auth_Q', 'cita_Q',
    'pub_años', 'auth_pos', 'auth_num', 'auth_inar',
    'auth_citas', 'filter_authors', 'filter_papers'], axis=1,
    inplace=True)


conn = sqlite3.connect('astrogen.db')
c = conn.cursor()

script = 'CREATE TABLE IF NOT EXISTS astronomers (' + \
         ', '.join(df.columns) + ')'


c.execute(script)
conn.commit()

df.to_sql('astronomers', conn, if_exists='replace', index = False)





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

recordsToInsert = [
        (22, 90909, 'SD df sdf asdfasdf asdaf as', 'fasdfasf', 33,
        '00001010', 'asdfsadfsdf', 'asdfsdf', 'jtyjdjh', 'yrtyrt',
        'qweqweqwe'),
        (22, 90909, 'SD df sdf asdfasdf asdaf as', 'fasdfasf', 33,
        '00001010', 'asdfsadfsdf', 'asdfsdf', 'jtyjdjh', 'yrtyrt',
        'qweqweqwe'),
        (22, 90909, 'SD df sdf asdfasdf asdaf as', 'fasdfasf', 33,
        '00001010', 'asdfsadfsdf', 'asdfsdf', 'jtyjdjh', 'yrtyrt',
        'qweqweqwe'),
        (22, 90909, 'SD df sdf asdfasdf asdaf as', 'fasdfasf', 33,
        '00001010', 'asdfsadfsdf', 'asdfsdf', 'jtyjdjh', 'yrtyrt',
        'qweqweqwe')]




p = get_papers_from_df(auth)
pasar los papaers a tupla y escribir




        (4, 'Jos', 'jos@gmail.com'),
                   (5, 'Chris', 'chris@gmail.com'),
                   (6, 'Jonny', 'jonny@gmail.com')]

insertMultipleRecords(recordsToInsert, conn, fls)
