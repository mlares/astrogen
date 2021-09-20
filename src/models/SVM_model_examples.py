import pickle
import ads
import difflib
import pandas as pd
from os import path, system
from matplotlib import pyplot as plt
import numpy as np
from tqdm import tqdm
import re
import jellyfish
import pickle
from joblib import dump, load

from astrogen_utils import bcolors, ds2
from astrogen_utils import initials, getinitials, pickone


D = pd.read_excel('../../data/redux/astro_all.xlsx', sheet_name="todos") 
D['apellido'] = D.apellido.apply(lambda x: x.lower())
D['nombre'] = D.nombre.apply(lambda x: x.lower())
N = D.shape[0]


"""
Load papers from origianl files downloaded from ADS

Se puede corregir un autor reemplazando el archivo individual
"""
papers = []
for i in tqdm(range(N)):
    x = D.iloc[i]

    ap = x.apellido.title()
    nm = x.nombre
    auth = ', '.join([ap, getinitials(nm)])

    ymax = 0
    filen = '../../../data/ADS/papers_'+ ap +'.pk'
    if path.isfile(filen):
        with open(filen, 'rb') as f:
            ppr = pickle.load(f)

        for p in ppr:
            ymax = max(ymax, int(p.year))
        papers.append(ppr)
    else:
        papers.append([])

fileD = '../../data/pickles/papers_list.pk'
with open(fileD, 'wb') as f:
   pickle.dump(papers, f)



def re_names(string):
    """
    Dado un nombre, devuelve los nombres completos o iniciales
    """
    string = string.title()
    regex1 = r"[A-Z][^A-Z\s]\w+"
    fullnames = re.findall(regex1, string)
    if len(fullnames)>0:
        if '.' in fullnames[0]:
            fullnames = ''
    regex2 = "[A-Z][A-Z][A-Z]\s|[A-Z][A-Z]\s|[A-Z]\.|[A-Z]$"
    regaux = r"[A-Z][A-Z][A-Z]|[A-Z][A-Z]"
    laux = re.findall(regaux, string)
    if len(laux)>0:
        iniciales = ('. '.join(list(laux[0])) + '.').split()
    else:
        iniciales = re.findall(regex2, string)
    if len(fullnames)>0 and len(iniciales)==0:
        for s in fullnames:
            iniciales.append(getinitials(s))
    return ' '.join(fullnames), ' '.join(iniciales)


def aut_compare(aut1, aut2):
    """
    each author: ap_full, ap_inic, nom_full, nom_inic
    e.g.:
    aut_compare([['Lares'], [], [], ['M.']], [['Lares'], [], [], ['M. E.']])
    """
    # comparar apellidos:
    a1 = aut1[0]
    a2 = aut2[0]

    d_ap = difflib.SequenceMatcher(None, a1, a2).ratio()
    d1_ap = jellyfish.damerau_levenshtein_distance(a1, a2)
    d2_ap = jellyfish.jaro_distance(a1, a2)     
    d3_ap = jellyfish.levenshtein_distance(a1, a2)                          

    # comparar nombres:
    if len(aut2[2])>0: # tiene nombre completo
        a1 = aut1[2]
        a2 = aut2[2]
        d_n = difflib.SequenceMatcher(None, a1, a2).ratio()
        d1_n = jellyfish.damerau_levenshtein_distance(a1, a2)
        d2_n = jellyfish.jaro_distance(a1, a2)     
        d3_n = jellyfish.levenshtein_distance(a1, a2)                          

    else: # tiene solo iniciales
        a1 = aut1[3]
        a2 = aut2[3]
        d_n = difflib.SequenceMatcher(None, a1, a2).ratio()
        d1_n = jellyfish.damerau_levenshtein_distance(a1, a2)
        d2_n = jellyfish.jaro_distance(a1, a2)     
        d3_n = jellyfish.levenshtein_distance(a1, a2)                          

    return [d_ap, d_n, d1_ap, d1_n, d2_ap, d2_n, d3_ap, d3_n,
           len(aut1[0]), len(aut2[0]), 
           len(aut1[1]), len(aut2[1])]



def authmatch(x, ip, show=False):
    """
    Dado un autor y un paper, determinar si ese paper
    es de ese autor.
    0)ap_full, 1)ap_inic, 2)nom_full, 3)nom_inic,  <--- autor buscado
    4)etal_ap_full, 5)etal_ap_inic, 6)etal_nom_full, 7)etal_nom_inic

    """
    nms = [[[]]*4, [[]]*4]
    nms[0][0:2] = re_names(x.apellido)
    nms[0][2:4] = re_names(x.nombre)

    mx = -99

    for au, af in zip(ip.author, ip.aff):
        nl = au.split(',')
        if len(nl)==2:
            au_surname, au_name = nl
        elif len(nl)>2:
            au_surname = nl[0]
            au_name = ''.join(nl[1:])
        else:
            au_surname = nl[0]
            au_name = ''

        nms[1][0:2] = re_names(au_surname)
        nms[1][2:4] = re_names(au_name)
        ll = aut_compare(*nms)

        m = ll[0]+ll[1]-ll[2]-ll[3]-ll[4]-ll[5]
        if m > mx:
            lmx = ll
            mx = m
        ar = 1 if 'entina' in af else 0
        if not ar: ar = 0.5 if (af==' ' or af=='-') else 0
        ll.append(ar)
        if show:
            if ll[0]>0.8:
                print(f'\u001b[46;1m   {au} \u001b[0m{af[:80]}')
            else:
                print(f'   \u001b[46;1m{au} \u001b[0m{af[:80]}')

    return lmx



# CREAR MUESTRA DE ENTRENAMIENTO :::::::::::::::::::::::::::::::::::::::::
ss = 'y'
while ss=='y':
    lst = np.random.choice(D.index, 10)
    fd = open('papers_learn.csv', 'a')
    lista_auts = []
    for i in lst: # LISTA DE AUTORES
        lista_auts.append(i)
        x = D.loc[i]
        saut = f'{x.apellido} {x.nombre}'

        if len(papers[i])>0:
            ip = np.random.choice(papers[i])

            system('clear')
            print(f'{ip.year}\n{bcolors.BOLD}\u001b[41;1m{ip.title}\u001b[42;1m{bcolors.ENDC}')
            print(f'\nBúsqueda de autor: [{i}]{saut.upper()}\n')
            ll = authmatch(x, ip, True)
            print('\n', ll)
            s = input('\ninclude this paper?  ')
            vals = [f'{float(v):6.3f}' for v in ll]
            vals.append(s)
            vals = ', '.join(vals) + '\n'
            if s=='0' or s=='1':
                fd.write(vals)
    fd.close()
    ss = input('\n Seguir? (y/n)')

