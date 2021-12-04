import jellyfish
import difflib
import pandas as pd
import numpy as np
from openpyxl import load_workbook
from matplotlib import pyplot as plt

from astrogen_utils import bcolors, ds, ds1, ds2, get_gender2
from astrogen_utils import append_df_to_excel

pd.options.mode.chained_assignment = None
pd.set_option('display.max_rows', None)

df = pd.read_excel('../../data/redux/astro_all.xlsx', sheet_name="todos")

df.area.fillna('', inplace=True)
df.area.replace('nan', '', inplace=True)
df.cic.fillna('', inplace=True)
df.cic.replace('nan', '', inplace=True)
df.docencia.fillna('', inplace=True)
df.docencia.replace('nan', '', inplace=True)
df.orcid.fillna('', inplace=True)
df.orcid.replace('nan', '', inplace=True)
 
doc = df.cic.str.contains('oc')
posdoc = df.cic.str.contains('osdoc')

df.loc[posdoc, 'cic'] = 'posdoc'
df.loc[-posdoc & doc, 'cic'] = 'becario'






def age(dni, a, b, c):
    return a - b*dni*1.e-7 + c*(dni*1.e-7-2.5)**2 

a, b, c = 80.87333471, 14.38981263, 0.62055574









# ________________________________________________________________________
# distribucion de edades por categoria

tit = ['SUPERIOR', 'PRINCIPAL', 'INDEPENDIENTE', 'ADJUNTO', 'ASISTENTE']
cat = ['super', 'rincip', 'indep', 'djunto', 'sistente']

for title, categoria in zip(tit, cat):

    s = df[df.cic.str.contains(categoria)]

    Nm = s[s.genero=='m'].count().max()
    Nf = s[s.genero=='f'].count().max()

    age_f = s[s.genero=='f']['edad'].values
    age_m = s[s.genero=='m']['edad'].values
    age_f.sort()
    age_m.sort()

    y_f = np.linspace(0,1,len(age_f))
    y_m = np.linspace(0,1,len(age_m))

    fig = plt.figure(figsize=(8,6))

    ax1 = fig.add_subplot(1,1,1)
    ax1.step(age_f, y_f, where='pre', color='deeppink',
            label=f'investigadoras mujeres ({Nf})')
    ax1.step(age_m, y_m, where='pre', color='teal',
            label=f'investigadores varones ({Nm})')
    ax1.set_xlabel('edad (años)')
    ax1.set_xticks(np.arange(35, 95, 5))
    ax1.set_xlim(25, 90)
    ax1.legend()

    ax1.plot(age_f, [0.55]*len(age_f), marker='o', linestyle='None', color='deeppink')
    ax1.plot(age_m, [0.45]*len(age_m), marker='o', linestyle='None', color='teal')

    ax1.set_ylabel('N(< edad) / N')
    ax1.set_title(f'EDADES DE INVESTIGADORES {title}')
    ax1.grid()

    plt.tight_layout()
    fig.savefig(f'age_{title}.png')


# ________________________________________________________________________
# distribucion de edades por categoria

cat = ['super', 'rincip', 'indep', 'djunto', 'sistente']

fig = plt.figure(figsize=(7,7))
ax1 = fig.add_subplot(1,1,1)

clr = ['maroon', 'brown', 'chocolate', 'peru', 'burlywood']

clrf = ['deeppink', 'darkorchid', 'deeppink', 'darkorchid', 'deeppink']
clrm = ['teal', 'dodgerblue', 'teal', 'dodgerblue', 'teal', 'dodgerblue' ]
clrf = ['deeppink']*6
clrm = ['teal']*6

lsy = ['-', ':', '--', ':', '-']
lwd = [2,2,2,2,2]
add = [0, 0, 0, 0, 0]

for k, categoria in enumerate(cat):

    s = df[df.cic.str.contains(categoria)]

    Nm = s[s.genero=='m'].count().max()
    Nf = s[s.genero=='f'].count().max()
    age_f = s[s.genero=='f']['edad'].values
    age_m = s[s.genero=='m']['edad'].values
    age_f.sort()
    age_m.sort()

    y_f = np.linspace(0,1,len(age_f))
    y_m = np.linspace(0,1,len(age_m))
    y_f = range(add[k], add[k]+len(age_f))
    y_m = range(add[k], add[k]+len(age_m)) 

    ax1.step(age_f, y_f, where='pre', color=clrf[k],
            label=f'investigadoras mujeres ({Nf})', linewidth=lwd[k],
            linestyle=lsy[k])
    ax1.step(age_m, y_m, where='pre', color=clrm[k],
            label=f'investigadores varones ({Nm})', linewidth=lwd[k],
            linestyle=lsy[k])

ax1.set_xlabel('edad (años)')
ax1.set_xticks(np.arange(35, 95, 5))
ax1.set_xlim(30, 80)
#ax1.legend()
ax1.set_ylabel('N(< edad)')
#ax1.grid()
plt.tight_layout()
fig.savefig(f'age_CICs.png')


fig.savefig(f'age_CICs.pdf')
fig.savefig(f'age_CICs.svg')





 










# ________________________________________________________________________
# distribucion de categorias por rango de edades

age_bins = [35, 45, 55, 65, 75, 95]

s = df[df.cic.str.contains('super|princ|independiente|adjunto|asistente')]
cats = np.array(s.cic.value_counts().index)[[2, 1, 0, 3, 4]]

x=np.array(range(1, 6))

for i in range(len(age_bins)-1):
    ss = s[s.edad.between(age_bins[i], age_bins[i+1])]

    bm, bf = [], []
    for c in cats:
        jm=ss[(ss.genero=='m') & (ss.cic==c)].count().max()
        jf=ss[(ss.genero=='f') & (ss.cic==c)].count().max()
        bm.append(jm)
        bf.append(jf)


    fig = plt.figure(figsize=(8,6))
    ax1 = fig.add_subplot(111)
    ax1.bar(x-0.15, bm, width=0.3, color='powderblue',
            label='varones')
    ax1.bar(x+0.15, bf, width=0.3, color='thistle',
            label='mujeres')
    ax1.set_xticks(x)
    ax1.set_xticklabels(cats)
    ax1.set_ylabel('cantidad')
    ax1.set_title(f'rango de edad: {age_bins[i]} - {age_bins[i+1]}')
    ax1.legend()

    plt.tight_layout()
    fig.savefig(f'cats_by_age_{str(i)}.png')
    plt.close('all')
                                           






age_bins = [0, 40, 49.9, 59.9, 100]

s = df[df.cic.str.contains('becario|posdoc|super|princ|independiente|adjunto|asistente')]
cats = np.array(s.cic.value_counts().index)[[2, 5, 3, 1, 0, 4, 6]]

x=np.array(range(1, 8))

for i in range(len(age_bins)-1):
    ss = s[s.edad.between(age_bins[i], age_bins[i+1])]

    bm, bf = [], []
    for c in cats:
        jm=ss[(ss.genero=='m') & (ss.cic==c)].count().max()
        jf=ss[(ss.genero=='f') & (ss.cic==c)].count().max()
        bm.append(jm)
        bf.append(jf)


    fig = plt.figure(figsize=(8,6))
    ax1 = fig.add_subplot(111)
    ax1.bar(x-0.15, bm, width=0.3, color='powderblue',
            label='varones')
    ax1.bar(x+0.15, bf, width=0.3, color='thistle',
            label='mujeres')
    ax1.set_xticks(x)
    ax1.set_xticklabels(cats)
    ax1.set_ylabel('cantidad')
    ax1.set_title(f'rango de edad: {age_bins[i]} - {age_bins[i+1]}')
    ax1.legend()

    plt.tight_layout()
    fig.savefig(f'cats_by_age_{str(i)}.png')
    fig.savefig(f'cats_by_age_{str(i)}.pdf')
    plt.close('all')
                                           
 





M = np.zeros([2,7,4])  # generos, cats, edades

for i in range(len(age_bins)-1):
    ss = s[s.edad.between(age_bins[i], age_bins[i+1])]
    bm, bf = [], []
    for c in cats:
        jm=ss[(ss.genero=='m') & (ss.cic==c)].count().max()
        jf=ss[(ss.genero=='f') & (ss.cic==c)].count().max()
        bm.append(jm)
        bf.append(jf)
    M[0,:,i] = bm
    M[1,:,i] = bf


"""
Guardar estos datos en un archivo
M=M.astype(int)
columns=['0-39', '40-49', '50-59', '60-']
index = ['scholars', 'posdocs', 'I', 'II', 'III', 'IV', 'V']
dfm = pd.DataFrame(M[0], columns=columns, index=index)
dff = pd.DataFrame(M[1], columns=columns, index=index)
dfm['gender'] = ['male']*7
dff['gender'] = ['female']*7
df = dfm.append(dff)
df.to_csv('conicet_astro.csv')
"""




xx = np.array(range(1, 8))

fig, ax = plt.subplots() 
labels = ['scholars', 'posdocs', 'I', 'II', 'III', 'IV', 'V']

c = ['red', 'blue', 'green', 'grey']
bm = np.array([0]*7)
bf = np.array([0]*7)
for i in range(4):
    y = M[0, :, i]
    ax.bar(xx+0.2, y, width=0.4, bottom=bm, color=c[i])
    bm = bm + y

    y = M[1, :, i]
    ax.bar(xx-0.2, y, width=0.4, bottom=bf, color=c[i])
    bf = bf + y

plt.xticks(xx, ('S', 'P', 'I', 'II', 'III', 'IV', 'V'))

fig.savefig(f'cats_stacked.png')
fig.savefig(f'cats_stacked.pdf')
fig.savefig(f'cats_stacked.svg')
plt.close('all')






    fig = plt.figure(figsize=(8,6))
    ax1 = fig.add_subplot(111)
    ax1.bar(x-0.15, bm, width=0.3, color='powderblue',
            label='varones')
    ax1.bar(x+0.15, bf, width=0.3, color='thistle',
            label='mujeres')
    ax1.set_xticks(x)
    ax1.set_xticklabels(cats)
    ax1.set_ylabel('cantidad')
    ax1.set_title(f'rango de edad: {age_bins[i]} - {age_bins[i+1]}')
    ax1.legend()

    plt.tight_layout()
    fig.savefig(f'cats_by_age_{str(i)}.png')
    fig.savefig(f'cats_by_age_{str(i)}.pdf')
                                           
                            
