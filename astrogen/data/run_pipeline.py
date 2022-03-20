from pipeline import *

#%load_ext autoreload
#%autoreload 2

if __name__ == '__main__' and '__file__' in globals():

    D = S01_read_aaa_table()
    D = S02_add_OAC_data(next(D))
    D = S02_add_IATE_data(next(D))
    D = S02_add_IALP_data(next(D))
    D = S02_add_IAR_data(next(D))
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
    with open('df2.pk', 'wb') as f:
        pickle.dump(df2, f)
    with open('df2.pk', 'rb') as f:
        df2 = pickle.load(f)

    D = S03_add_gender(df2)
    D = S03_clean_and_sort(next(D))
    D = S04_pub_get_ads_entries(next(D))

    df3 = next(D).copy()
    with open('df3.pk', 'wb') as f:
        pickle.dump(df3, f)
    with open('df3.pk', 'rb') as f:
        df3 = pickle.load(f)

    D = S04_pub_clean_papers(df3); df = next(D)

    df4 = df.copy()
    with open('df4.pk', 'wb') as f:
        pickle.dump(df4, f)
    with open('df4.pk', 'rb') as f:
        df4 = pickle.load(f)

    D = S04_pub_journal_index(df4); df = next(D)

    D = S04_pub_add_metrics(df); df = next(D)

    df5 = df.copy()
    with open('df5.pk', 'wb') as f:
        pickle.dump(df5, f)
    with open('df5.pk', 'rb') as f:
        df5 = pickle.load(f)

    # la idea es correr dos veces el S04_load_check_filters
    # la primera vez crea los archivos si no existen (sino, ignora)
    D = S04_load_check_filters(df5); df = next(D)
    D = S04_make_pages(df); df = next(D)
    D = S04_load_check_filters(df); df = next(D)
    D = S04_count_papers_ss(df); df6 = next(D).copy()

    with open('df6.pk', 'wb') as f:
        pickle.dump(df6, f)
    with open('df6.pk', 'rb') as f:
        df6 = pickle.load(f)

    load_final(df6)
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
