import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

cnames = ['año_ing', 'mi', 'fi', 'me', 'fe']
opts = {'skiprows': 1,
        'names': cnames, 
        'usecols': [0,2,3,6,7]}

D = []
for y in range(2006,2020):
    df = pd.read_excel('../../data/collect/famaf-astronomia.xlsx',
                       sheet_name=str(y), **opts)
    df['año'] = [y]*df.shape[0]
    D.append(df)
dd = pd.concat(D)

dd['duracion'] = dd.año - dd.año_ing
dd = dd.dropna(axis=0, thresh=4)


# %%
# Cantidad de alumnos y cantidad de egresados por año

byear = dd.groupby(['año']).sum()

# %%

fig = plt.figure(figsize=(8,8))

ax1 = fig.add_subplot(2,1,1)
ax1.plot(byear.index, byear['fi'], 
         color='deeppink', label='estudiantes mujeres')
ax1.plot(byear.index, byear['mi'], 
         color='teal', label='estudiantes varones')
ax1.legend()
ax1.set_xlabel('año')
ax1.set_ylabel('dN/d(año)')

ax2 = fig.add_subplot(2,1,2)
ax2.plot(byear.index, byear['fe'].cumsum(), color='deeppink', label='egresadas mujeres')
ax2.plot(byear.index, byear['me'].cumsum(), color='teal', label='egresados varones')
ax2.legend()
ax2.set_xlabel('año')

plt.tight_layout()
fig.savefig('plot1.png')

# %%
# tiempo que tardan en terminar la carrera

dur_m = []
for r in dd[dd.me>0].itertuples():
    dur_m = dur_m + int(r.me) * [r.duracion]

dur_f = []
for r in dd[dd.fe>0].itertuples():
    dur_f = dur_f + int(r.fe) * [r.duracion]

bins = np.arange(4.5, 14.5)


fig = plt.figure(figsize=(6,6))

ax1 = fig.add_subplot()
ax1.hist(dur_f, bins=bins, histtype='stepfilled', linewidth=0,
         color='pink', alpha=0.5, label='estudiantes mujeres')
ax1.hist(dur_f, bins=bins, histtype='step', linewidth=1,
         color='deeppink')

ax1.hist(dur_m, bins=bins, histtype='step', linewidth=2,
         color='teal', label='estudiantes varones')

ax1.legend()
ax1.set_xlabel('duración de la carrera en años')
ax1.set_ylabel('número de estudiantes recibidos')

plt.tight_layout()
fig.savefig('plot2.png')
 
# %%
# fraccion que termina la carrera


fig = plt.figure(figsize=(6,6))
ax1 = fig.add_subplot()

#for a in range(2000, 2015):
for a in range(2000, 2003):
    df = dd[dd.año_ing==a]

    y = df.año
    m_fade = df.mi
    f_fade = df.fi
    m_rec = df.me
    f_rec = df.fe
    m_recs = m_rec > 0
    f_recs = f_rec > 0

    ax1.plot(y, m_fade, color='teal')
    ax1.plot(y, f_fade, color='deeppink')
    ax1.plot(y[m_recs], m_rec[m_recs], color='teal')
    ax1.plot(y[m_recs], f_rec[m_recs], color='deeppink')

plt.tight_layout()
fig.savefig('plot3.png')



for a in range(2006, 2015):

    fig = plt.figure(figsize=(6,6))
    ax1 = fig.add_subplot()

    df = dd[dd.año_ing==a]

    y = df.año - a + 1
    m_fade = df.mi
    f_fade = df.fi
    m_rec = df.me
    f_rec = df.fe
    m_recs = m_rec > 0
    f_recs = f_rec > 0

    ymn = min(y[m_recs].min(), y[f_recs].min())
    txttop = max(m_fade.max(), f_fade.max())

    ax1.axhline(0, linestyle='--', color='silver', linewidth=1)
    ax1.axvline(ymn, linestyle='--', color='silver', linewidth=1)
    ax1.plot(y, m_fade, color='teal', label='estudiantes varones')
    ax1.plot(y, f_fade, color='deeppink', label='estudiantes mujeres')

    ax1.plot(y[f_recs], f_rec[f_recs], markersize=6,
            marker='o', mfc='white', mec='deeppink')
    ax1.plot(y[m_recs], m_rec[m_recs], 'o', color='teal', markersize=3)

    ax1.set_xlabel(f'años desde el inicio de la carrera ({a})')
    ax1.set_ylabel('cantidad de alumnos')
    ax1.text(ymn+1, txttop, f'Cohorte de ingresantes {a}')
    ax1.set_xlim(0, 8)

    plt.tight_layout()
    fig.savefig(f'plot_fade_{a}.png')







fig = plt.figure(figsize=(6,6))
ax1 = fig.add_subplot()
        
for a in range(2006, 2015):

    df = dd[dd.año_ing==a]

    y = df.año - a + 1
    m_fade = df.mi
    f_fade = df.fi
    m_rec = df.me
    f_rec = df.fe
    m_recs = m_rec > 0
    f_recs = f_rec > 0

    rnmx = np.random.normal(scale=0.1, size=sum(m_recs))
    rnmy = np.random.normal(scale=0.1, size=sum(m_recs))
    rnfx = np.random.normal(scale=0.1, size=sum(f_recs))
    rnfy = np.random.normal(scale=0.1, size=sum(f_recs))

    ymn = min(y[m_recs].min(), y[f_recs].min())
    txttop = max(m_fade.max(), f_fade.max())

    ax1.axhline(0, linestyle='--', color='silver', linewidth=1)
    #ax1.plot(y, m_fade, color='teal', label='estudiantes varones')
    ax1.plot(y, f_fade, color='deeppink', label='estudiantes mujeres')

    #ax1.plot(y[f_recs]+rnfx, f_rec[f_recs]+rnfy, markersize=6,
    #        marker='o', mfc='None', mec='deeppink')
    for xx, yy in zip(y[f_recs], f_rec[f_recs]):
        ax1.plot(xx, yy)


    #ax1.plot(y[m_recs]+rnmx, m_rec[m_recs]+rnmy, 'o', color='teal', markersize=3)

ax1.set_xlabel(f'años desde el inicio de la carrera ({a})')
ax1.set_ylabel('cantidad de alumnos')
ax1.set_xlim(0.5, 8.5)

plt.tight_layout()
fig.savefig(f'plot_fade_f.png')
                                    








# fraccion total de gente que se recibe:

frac_f = dd.ef.sum() / dd['if'][:-5].sum()
frac_m = dd.em.sum() / dd.im[:-5].sum()
# --> las mujeres son 26% más exitosas para terminar la carrera








