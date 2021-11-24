from pipeline import *
import sqlite3

#%load_ext autoreload
#%autoreload 2

def load_1(*args):
    D = args[0]
    fileD = '../../data/redux/astrogen_DB_1.xlsx'
    D.to_excel(fileD)

    script = 'CREATE TABLE IF NOT EXISTS load1 ('+', '.join(D.columns)+')'
    c.execute(script)
    conn.commit()
    D.to_sql('load1', conn, if_exists='replace', index = False)

def load_2(*args):
    D = args[0]                           
    fileD = '../../data/redux/astrogen_DB_2.xlsx'
    D.to_excel(fileD)

    script = 'CREATE TABLE IF NOT EXISTS load2 ('+', '.join(D.columns)+')'
    c.execute(script)
    conn.commit()
    D.to_sql('load2', conn, if_exists='replace', index = False)

def load_3(*args):
    D = args[0]
    fileD = '../../data/redux/astrogen_DB_3.xlsx'
    D.to_excel(fileD)

    script = 'CREATE TABLE IF NOT EXISTS load3 ('+', '.join(D.columns)+')'
    c.execute(script)
    conn.commit()
    D.to_sql('load3', conn, if_exists='replace', index = False)

def load_4(*args):
    D = args[0]
    fileD = '../../data/redux/astrogen_DB_4.xlsx'
    D.to_excel(fileD)

    script = 'CREATE TABLE IF NOT EXISTS load4 ('+', '.join(D.columns)+')'
    c.execute(script)
    conn.commit()
    D.to_sql('load4', conn, if_exists='replace', index = False)

def load_5(*args):
    D = args[0]
    fileD = '../../data/redux/astrogen_DB_5.xlsx'
    D.to_excel(fileD)

    script = 'CREATE TABLE IF NOT EXISTS load5 ('+', '.join(D.columns)+')'
    c.execute(script)
    conn.commit()
    D.to_sql('load5', conn, if_exists='replace', index = False)

def load_6(*args):
    D = args[0]
    fileD = '../../data/redux/astrogen_DB_6.xlsx'
    D.to_excel(fileD)

    script = 'CREATE TABLE IF NOT EXISTS load6 ('+', '.join(D.columns)+')'
    c.execute(script)
    conn.commit()
    D.to_sql('load6', conn, if_exists='replace', index = False)

def load_7(*args):
    D = args[0]
    fileD = '../../data/redux/astrogen_DB_7.xlsx'
    D.to_excel(fileD)

    script = 'CREATE TABLE IF NOT EXISTS load7 ('+', '.join(D.columns)+')'
    c.execute(script)
    conn.commit()
    D.to_sql('load7', conn, if_exists='replace', index = False)
 
def load_8(*args):
    D = args[0]
    fileD = '../../data/redux/astrogen_DB_8.xlsx'
    D.to_excel(fileD)

    script = 'CREATE TABLE IF NOT EXISTS load8 ('+', '.join(D.columns)+')'
    c.execute(script)
    conn.commit()
    D.to_sql('load8', conn, if_exists='replace', index = False)

def load_9(*args):
    D = args[0]
    fileD = '../../data/redux/astrogen_DB_9.xlsx'
    D.to_excel(fileD)

    script = 'CREATE TABLE IF NOT EXISTS load9 ('+', '.join(D.columns)+')'
    c.execute(script)
    conn.commit()
    D.to_sql('load9', conn, if_exists='replace', index = False)
                            
def load_10(*args):
    D = args[0]
    fileD = '../../data/redux/astrogen_DB_10.xlsx'
    D.to_excel(fileD)

    script = 'CREATE TABLE IF NOT EXISTS load10 ('+', '.join(D.columns)+')'
    c.execute(script)
    conn.commit()
    D.to_sql('load10', conn, if_exists='replace', index = False)



if __name__ == '__main__' and '__file__' in globals():

    conn = sqlite3.connect('../../data/redux/astrogen_DB_rc2.db')
    c = conn.cursor()

    #--------------------------------- LISTA DE PERSONAL

    D = S01_read_aaa_table(); df1 = next(D)
    D = S02_add_OAC_data(df1); df2 = next(D) 
    D = S02_add_IATE_data(df2); df3 = next(D) 
    D = S02_add_IALP_data(df3); df4 = next(D) 
    D = S02_add_GAE_data(df4); df5 = next(D) 
    D = S02_add_IAFE_data(df5); df6 = next(D) 
    D = S02_add_ICATE_data(df6); df7 = next(D) 

    load_1(df7)

    #D = S02_add_CIC_data(df7); df8 = next(D) 
    #D = S02_add_CONICET_data(df7, 2020); df8 = next(D) 

    df = df7
    for year in range(2007, 2020):
        print(year)
        D = S02_add_CONICET_data(df, year)
        df = next(D)

    df8 = df

    load_2(df8)

    D = S03_add_gender(df8); df9 = next(D)  
    load_3(df9)

    D = S03_add_age(df9); df10 = next(D)  
    load_4(df10)

    D = S03_clean_and_sort(df10); df11 = next(D)
    load_5(df11)



    #D = TST_filter_subset(df11); df11 = next(D)



   # PUBs
    D = S04_pub_get_ads_entries(df11); df12 = next(D)  
    D = S04_pub_clean_papers(df12); df13 = next(D)
    load_6(df13)

    D = S04_pub_journal_index(df13); df14 = next(D)  
    #load_7(df14.drop(['auth_Q','cita_Q','pub_años'], axis=1))
 
    D = S04_pub_add_metrics(df14); df15 = next(D)
 
    lst= ['auth_Q', 'cita_Q', 'pub_años', 'auth_pos', 'auth_num',
          'auth_inar', 'auth_citas', 'filter_papers']
    #load_8(df15.drop(lst, axis=1))
 
    D = S04_pub_filter_criteria(df15); df16 = next(D)
    #load_9(df16.drop(lst, axis=1))
 
    D = S04_make_pages(df16); df17 = next(D)

    load_final(df17) 

    # close DB connection
    conn.close()


# 
# 
# 
# #------------------------- TEST
# # limit to 20 entries for debugging
# D = TST_filter_subset(df8c); df9 = next(D)
# 
# 
# #--------------------------------- LISTA DE PUBLICACIONES
# 
# D = S04_pub_get_ads_entries(df11); df12 = next(D)  
# 
# D = S04_pub_clean_papers(df12); df13 = next(D)
# load_6(df13)
# 
# D = S04_pub_journal_index(df13); df14 = next(D)  
# load_7(df14.drop(['auth_Q','cita_Q','pub_años'], axis=1))
# 
# D = S04_pub_add_metrics(df14); df15 = next(D)
# 
# lst= ['auth_Q', 'cita_Q', 'pub_años', 'auth_pos', 'auth_num',
#       'auth_inar', 'auth_citas']
# load_8(df15.drop(lst, axis=1))
# 
# 
# D = S04_pub_filter_criteria(df15); df16 = next(D)
# load_9(df16.drop(lst, axis=1))
# 
# conn.close()
# 
# D = S04_make_pages(df16); df17 = next(D)
# 
# load_final(df17)
# 
# #se puede interrumppir en cualquier lado y hacer D=next(D)
# #para hacer una copia: 
# 
# 
# 
