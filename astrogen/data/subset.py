from pipeline import *


def make_index_html(D):# {{{
    source_dir = '../../data/interim/htmls/'
    for i in tqdm(D.index):

        auth = D.loc[i]
        papers = get_papers_from_df(auth)
        df = gen_spreadsheet(auth, papers)
        idx = np.argsort(df.Año.values)
        df = df.loc[idx, :]
        FP = np.array(auth.filter_papers.reshape([-1])[idx])
        if FP.size>0:
            S = []
            for i, x in enumerate(FP.reshape([-1])):
                ck = 'checked' if bool(x) else ''
                S.append(f'{s1}{str(i+1).zfill(3)}" value="" {ck}{s2}')
            df['include'] = S
        else:
            df['include'] = []

        url = [f'{s3}{r}{s4}{t}{s5}' for r, t in zip(df.adsurl, df.Título)]
        df['linkurl'] = url
        title_links = df.apply(lambda x: x.linkurl.replace('link', x.Título), axis=1)
        if FP.size>0:
            df['title_links'] = title_links
        else:
            df['title_links'] = []
        df['counter'] = np.arange(1,df.shape[0]+1)

        dfo = df.iloc[:, [9,3,4,8,6,1,2]].copy()

        for k in dfo.index:
            aut = focus_authors(dfo.Autores[k], auth.auth_pos[k])
            dfo.at[k, 'Autores'] = aut
            aff = focus_authors(dfo.Afiliaciones[k], auth.auth_pos[k])
            dfo.at[k, 'Afiliaciones'] = aff

        dfo = dfo.assign(Autores=dfo.Autores.apply(lambda x: '<br>'.join(x)))
        dfo = dfo.assign(Afiliaciones=dfo.Afiliaciones.apply(lambda x: '<br>'.join(x)))
        N = df.shape[0]
        Ni = sum(FP)

        #--- template
        str_io = StringIO()
        dfo.to_html(buf=str_io, index=False, index_names=False, escape=False)
        html_str = str_io.getvalue()

        #fname = (f'{str(i).zfill(3)}_'
        #         f'{auth.apellido.replace(" ", "_")}_{auth.nombre[0]}.html')
        #fout = (f'{str(i).zfill(3)}_'
        #        f'{auth.apellido.replace(" ", "_")}_{auth.nombre[0]}.txt')
        filename = fnames(auth, source_dir, '.html')
        fout = fnames(auth, source_dir, '.txt', False)

        target = open(filename, 'w')
        target.write(template_page.render(N=N,
                                          Ni=Ni,
                                          html_str=html_str,
                                          auth=auth,
                                          filedata=fout))
        target.close()# }}}

def S04_make_pages(D):# {{{

    source_dir = '../../models/'
    template_file = 'template.html'
    templateLoader = jinja2.FileSystemLoader(searchpath=source_dir)
    latex_jinja_env = jinja2.Environment(
        block_start_string=r"\BLOCK{",
        block_end_string='}',
        variable_start_string=r'\VAR{',
        variable_end_string='}',
        comment_start_string=r'\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
        loader=templateLoader
    )
    template_page = latex_jinja_env.get_template(template_file)

    s1 = '<input type="checkbox" name="check'
    s2 = ' /><br>'
    s3 = '<a href="'
    s4 = '">'
    s5 = '</a>'

    source_dir = '../../data/interim/htmls/'
    for i in tqdm(D.index):

        auth = D.loc[i]
        papers = get_papers_from_df(auth)
        df = gen_spreadsheet(auth, papers)
        idx = np.argsort(df.Año.values)
        df = df.loc[idx, :]
        FP = np.array(auth.filter_papers.reshape([-1])[idx])
        if FP.size>0:
            S = []
            for i, x in enumerate(FP.reshape([-1])):
                ck = 'checked' if bool(x) else ''
                S.append(f'{s1}{str(i+1).zfill(3)}" value="" {ck}{s2}')
            df['include'] = S
        else:
            df['include'] = []

        url = [f'{s3}{r}{s4}{t}{s5}' for r, t in zip(df.adsurl, df.Título)]
        df['linkurl'] = url
        title_links = df.apply(lambda x: x.linkurl.replace('link', x.Título), axis=1)
        if FP.size>0:
            df['title_links'] = title_links
        else:
            df['title_links'] = []
        df['counter'] = np.arange(1,df.shape[0]+1)

        dfo = df.iloc[:, [9,3,4,8,6,1,2]].copy()

        for k in dfo.index:
            aut = focus_authors(dfo.Autores[k], auth.auth_pos[k])
            dfo.at[k, 'Autores'] = aut
            aff = focus_authors(dfo.Afiliaciones[k], auth.auth_pos[k])
            dfo.at[k, 'Afiliaciones'] = aff

        dfo = dfo.assign(Autores=dfo.Autores.apply(lambda x: '<br>'.join(x)))
        dfo = dfo.assign(Afiliaciones=dfo.Afiliaciones.apply(lambda x: '<br>'.join(x)))
        N = df.shape[0]
        Ni = sum(FP)

        #--- template
        str_io = StringIO()
        dfo.to_html(buf=str_io, index=False, index_names=False, escape=False)
        html_str = str_io.getvalue()

        #fname = (f'{str(i).zfill(3)}_'
        #         f'{auth.apellido.replace(" ", "_")}_{auth.nombre[0]}.html')
        #fout = (f'{str(i).zfill(3)}_'
        #        f'{auth.apellido.replace(" ", "_")}_{auth.nombre[0]}.txt')
        filename = fnames(auth, source_dir, '.html')
        fout = fnames(auth, source_dir, '.txt', False)

        target = open(filename, 'w')
        target.write(template_page.render(N=N,
                                          Ni=Ni,
                                          html_str=html_str,
                                          auth=auth,
                                          filedata=fout))
        target.close()# }}}

# read authors
with open('../../data/redux/astrogen_DB_labelled.pk', 'rb') as f:
    D = pickle.load(f)

# select authors
conn = sqlite3.connect('../../data/redux/astrogen_DB_labelled.db')
script = """
select *, COUNT(*) as cc,
           MAX(p.year) as ymx,
           SUM(CASE WHEN p.inar=1 then 1 else 0 END) as N_inar,
           SUM(CASE WHEN p.inar=1 then 1 else 0 END) / (1.*COUNT(*)) as q
    FROM papers as p
        INNER JOIN people as g
    WHERE 
            p.ID==g.ID
                AND
                g.yob BETWEEN 1951 AND 2001
                AND
                p.journal_Q==1
                AND
                p.author_count<51
        GROUP BY p.ID 
        HAVING 
           ymx>2016
           AND
           q>0.75 
""" 
sql_query = pd.read_sql_query (script, conn)
df = pd.DataFrame(sql_query)
conn.close()

ids = df.ID.values[:,0]
ids = np.random.permutation(ids)

ddf = D.iloc[ids, :]

D = S04_load_check_filters(ddf); ddf = next(D)
S04_make_pages(ddf)


# make index page

source_dir = '../../models/'
target_dir = './'
template_file = 'template_list.html'
templateLoader = jinja2.FileSystemLoader(searchpath=source_dir)
latex_jinja_env = jinja2.Environment(
    block_start_string=r"\BLOCK{",
    block_end_string='}',
    variable_start_string=r'\VAR{',
    variable_end_string='}',
    comment_start_string=r'\#{',
    comment_end_string='}',
    line_statement_prefix='%%',
    line_comment_prefix='%#',
    trim_blocks=True,
    autoescape=False,
    loader=templateLoader
)
template_page = latex_jinja_env.get_template(template_file)  

htmlfilename, authname, authobj = [], [], []

for i in ddf.index:

    auth = ddf.loc[i]
    filename = fnames(auth, target_dir, '.html')
    htmlfilename.append(filename)
    authname.append(f'{auth.apellido}, {auth.nombre}')
    authobj.append(auth)

lst = zip(htmlfilename, authname, authobj)
                  
filename = '../../data/interim/htmls/index.html'
target = open(filename, 'w')
target.write(template_page.render(lst=lst))
target.close()

