import pickle
from os import path, system
from os.path import join as pathjoin
import jinja2
from pipeline import *
from astrogen_utils import fnames


# READ DATA

file_D = '../../data/redux/astrogen_DB.pk'
with open(file_D, 'rb') as f:
    D = pickle.load(f)

# APPLY TEMPLATE

N = D.shape[0]
source_dir = '../../data/interim/htmls/'
source_dir = './'  # relative to index.html
finames = []
anames = []
auths = []
for kounter, i in enumerate(D.index):

    auth = D.loc[i]
    auths.append(auth)
    #fout = (f'{str(i).zfill(3)}_'
    #        f'{auth.apellido.replace(" ", "_")}_{auth.nombre[0]}.txt')

    filename = fnames(auth, source_dir, '.html')
    finames.append(filename)

    n1 = auth.apellido.title()
    n2 = auth.nombre.title()
    link_name = f'{n1}, {n2}'
    anames.append(link_name)
    print(filename, link_name)


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

output_dir = '../../data/interim/htmls/'
fname = 'index.html'
filename = pathjoin(output_dir, fname)
target = open(filename, 'w')
target.write(template_page.render(lst = zip(finames, anames, auths)
                                  ))
target.close()
