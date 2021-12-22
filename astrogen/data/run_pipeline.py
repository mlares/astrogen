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
    with open('df3.pk', 'wb') as f:
        pickle.dump(df3, f)
    with open('df3.pk', 'rb') as f:
        df3 = pickle.load(f)

    D = S03_add_gender(df2)
    D = S03_clean_and_sort(next(D))
    D = S04_pub_get_ads_entries(next(D))
    D = S04_pub_clean_papers(next(D))
    D = S04_pub_journal_index(next(D))
    D = S04_pub_add_metrics(next(D))

    df3 = next(D).copy()
    with open('df3.pk', 'wb') as f:
        pickle.dump(df3, f)
    with open('df3.pk', 'rb') as f:
        df3 = pickle.load(f)

    # la idea es correr dos veces el S04_load_check_filters
    # la primera vez crea los archivos si no existen (sino, ignora)
    D = S04_load_check_filters(df3)
    D = S04_make_pages(next(D))
    D = S04_load_check_filters(next(D))
    D = S04_count_papers_ss(next(D))

    df4 = next(D).copy()
    with open('df4.pk', 'wb') as f:
        pickle.dump(df4, f)
    with open('df4.pk', 'rb') as f:
        df4 = pickle.load(f)

    load_final(df4)
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
