import pickle
from os import path, system
from os.path import join as pathjoin
import jinja2


file_D = '../../data/redux/astrogen_DB.pk'
with open(file_D, 'rb') as f:
    D = pickle.load(f)

df = S04_pub_filter_criteria(D)


N = D.shape[0]


source_dir = '../../data/interim/ADS/htmls/'
source_dir = './'
fnames = []
anames = []
for kounter, i in enumerate(D.index):

    auth = D.iloc[i]

    fname = (f'{str(kounter).zfill(3)}_{str(i).zfill(3)}_'
             f'{auth.apellido.replace(" ", "_")}_{auth.nombre[0]}.html')
    fout = f'{str(kounter).zfill(3)}_{str(i).zfill(3)}_{auth.apellido.replace(" ", "_")}_{auth.nombre[0]}.txt'

    filename = pathjoin(source_dir, fname)
    fnames.append(filename)

    n1 = auth.apellido.title()
    n2 = auth.nombre.title()
    link_name = f'{n1}, {n2}'

    anames.append(link_name)
    print(link_name)


source_dir = '../../models/'
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

output_dir = '../../data/interim/ADS/htmls/'
fname = 'index.html'
filename = pathjoin(output_dir, fname)
target = open(filename, 'w')
target.write(template_page.render(lst = zip(fnames,anames)
                                  ))
target.close()

