from pipeline import *

#%load_ext autoreload
#%autoreload 2

if __name__ == '__main__' and '__file__' in globals():

    D = S01_read_aaa_table()
    D = S02_add_OAC_data(next(D))
    D = S02_add_IATE_data(next(D))
    D = S02_add_IALP_data(next(D))
    D = S02_add_GAE_data(next(D))
    D = S02_add_IAFE_data(next(D))
    D = S02_add_ICATE_data(next(D))
    D = S03_get_yob_from_DNI(next(D))
    D = S03_add_age(next(D))

    df1 = next(D).copy()

    with open('df1.pk', 'wb') as f:
        pickle.dump(df1, f)
    with open('df1.pk', 'rb') as f:
        df1 = pickle.load(f)

    df = df1.copy()
    for year in range(2007, 2021):
        print(year)
        D = S02_add_CONICET_data(df, year)
        df = next(D)

    df2 = df.copy()

    D = S03_add_gender(df2)

    D = S03_clean_and_sort(df12); df13 = next(D)
    D = S04_pub_get_ads_entries(df13); df14 = next(D)
    D = S04_pub_clean_papers(df14); df15 = next(D)
    D = S04_pub_journal_index(df15); df16 = next(D)
    D = S04_pub_add_metrics(df16); df17 = next(D)

    with open('df15.pk', 'wb') as f:
        pickle.dump(df17, f)
    with open('df15.pk', 'rb') as f:
        df17 = pickle.load(f)

    # la idea es correr dos veces el S04_load_check_filters
    # la primera vez crea los archivos si no existen (sino, ignora)
    D = S04_load_check_filters(df17); df18 = next(D)
    D = S04_make_pages(df18); df19 = next(D)
    D = S04_load_check_filters(df19); df20 = next(D)
    D = S04_count_papers_ss(df20); df21 = next(D)

    load_final(df21)
#    load_anonymized(df18)


"""
Then, run:
PYTHON:
    clean_anonymous.py
    curation_pages.py
    database_anonymous.py

    clean_labelled.py
    database_labelled.py

SQL:

"""
