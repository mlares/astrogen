# %%
import pandas as pd
import numpy as np
import sqlite3
from os import path
from matplotlib import pyplot as plt


from matplotlib import rc
rc('font',**{'family':'serif','serif':['DejaVu Serif']})
rc('text', usetex=False)

# %%
conn = sqlite3.connect('../../data/redux/astrogen_DB_anonymous.db')
c = conn.cursor()

c.execute('''  
                SELECT * FROM famaf
          ''')

cnames = ['year_in', 'mi', 'fi', 'me', 'fe', 'year', 'duration']
df = pd.DataFrame(c.fetchall(), columns=cnames)
conn.close()

# %%
plotdir = '../../figures/'
colora = 'mediumpurple'
coloro = 'lightseagreen'
dcolora = (0.5764705882, 0.43921569, 0.85882353, 0.5)
dcoloro = (0.1254901961, 0.69803922, 0.66666667, 0.5)


# %%
# Cantidad de alumnos y cantidad de egresados por año

byear = df.groupby(['year']).sum()

fig = plt.figure(figsize=(8,8))

ax1 = fig.add_subplot(2,1,1)
ax1.plot(byear.index, byear['fi'], 
         color=colora, label='female students')
ax1.plot(byear.index, byear['mi'], 
         color=coloro, label='male students')
ax1.legend(title='STUDENTS', fontsize=20)
ax1.set_xlabel('year', fontsize=20)
ax1.set_ylabel('dN/d(year)', fontsize=20)
ax1.set_xticks([2008, 2012, 2016, 2020])
ax1.tick_params(axis='both', which='major', labelsize=20)

ax2 = fig.add_subplot(2,1,2)
ax2.plot(byear.index, byear['fe'].cumsum(), color=colora,
        label='females graduates')
ax2.plot(byear.index, byear['me'].cumsum(), color=coloro,
        label='male graduates')
ax2.legend(title='GRADUATES', fontsize=20)
ax2.set_xlabel('year', fontsize=20)
ax2.set_ylabel('N(<year)', fontsize=20)
ax2.set_xticks([2008, 2012, 2016, 2020])
ax2.tick_params(axis='both', which='major', labelsize=20)

plt.tight_layout()
fig.savefig(plotdir + 'graduates_by_year.png')



# %%
# tiempo que tardan en terminar la carrera

dur_m = []
for r in df[df.me>0].itertuples():
    dur_m = dur_m + int(r.me) * [r.duration]
dur_m = np.array(dur_m)

dur_f = []
for r in df[df.fe>0].itertuples():
    dur_f = dur_f + int(r.fe) * [r.duration]
dur_f = np.array(dur_f)

bins = np.arange(4.5, 14.5)

fig = plt.figure(figsize=(8,8))
# #7aeae3
ax1 = fig.add_subplot()
ax1.tick_params(axis='both', which='major', labelsize=20)
ax1.hist(dur_f, bins=bins, histtype='stepfilled', linewidth=0,
         color='#a084e1', alpha=0.5, label='female')
ax1.hist(dur_f, bins=bins, histtype='step', linewidth=1,
         color=colora)

ax1.hist(dur_m, bins=bins, histtype='step', linewidth=6,
         color='white')
ax1.hist(dur_m, bins=bins, histtype='step', linewidth=3,
         color=coloro, label='male')

mn_m = dur_m.mean()
mn_f = dur_f.mean()
er_m = np.sqrt(dur_m.var()/len(dur_m))
er_f = np.sqrt(dur_f.var()/len(dur_f))

ax1.axvline(mn_m, color=coloro)
ax1.axvline(mn_f, color=colora)

ax1.plot([np.percentile(dur_m, 25), np.percentile(dur_m, 75)], [1,1],
        linestyle='--', color=coloro)
ax1.plot([np.percentile(dur_f, 25), np.percentile(dur_f, 75)], [0.8,0.8],
        linestyle='--', color=colora)

ax1.plot([mn_m-er_m, mn_m+er_m], [1,1], lw=3, color=coloro)
ax1.plot([mn_f-er_f, mn_f+er_f], [.8,.8], lw=3, color=colora)

ax1.legend(fontsize=20)
ax1.set_xlabel('years to complete graduation, y', fontsize=20)
ax1.set_ylabel('frequency of graduates, dN/dy', fontsize=20)

plt.tight_layout()
fig.savefig(path.join(plotdir, 'time_to_graduation.png'))


# %%
# fraccion que termina la carrera

fig = plt.figure(figsize=(6,6))
ax1 = fig.add_subplot()

#for a in range(2000, 2015):
for a in range(2000, 2003):
    dfss = df[df.year_in==a]

    y = dfss.year
    m_fade = dfss.mi
    f_fade = dfss.fi
    m_rec = dfss.me
    f_rec = dfss.fe
    m_recs = m_rec > 0
    f_recs = f_rec > 0

    ax1.plot(y, m_fade, color=coloro)
    ax1.plot(y, f_fade, color=colora)
    ax1.plot(y[m_recs], m_rec[m_recs], color=coloro)
    ax1.plot(y[m_recs], f_rec[m_recs], color=colora)

plt.tight_layout()
fig.savefig(path.join(plotdir, 'dropout_rates.png'))


# %%

for a in range(2006, 2015):

    fig = plt.figure(figsize=(6,6))
    ax1 = fig.add_subplot()

    dfss = df[df.year_in==a]

    y = dfss.year - a + 1
    m_fade = dfss.mi
    f_fade = dfss.fi
    m_rec = dfss.me
    f_rec = dfss.fe
    m_recs = m_rec > 0
    f_recs = f_rec > 0

    ymn = min(y[m_recs].min(), y[f_recs].min())
    txttop = max(m_fade.max(), f_fade.max())

    ax1.axhline(0, linestyle='--', color='silver', linewidth=1)
    ax1.axvline(ymn, linestyle='--', color='silver', linewidth=1)
    ax1.plot(y, m_fade, color=coloro, label='estudiantes varones')
    ax1.plot(y, f_fade, color=colora, label='estudiantes mujeres')

    ax1.plot(y[f_recs], f_rec[f_recs], markersize=6,
            marker='o', mfc='white', mec=colora)
    ax1.plot(y[m_recs], m_rec[m_recs], 'o', color=coloro, markersize=3)

    ax1.set_xlabel(f'años desde el inicio de la carrera ({a})')
    ax1.set_ylabel('cantidad de alumnos')
    ax1.text(ymn+1, txttop, f'Cohorte de ingresantes {a}')
    ax1.set_xlim(0, 8)

    plt.tight_layout()
    fig.savefig(path.join(plotdir, f'dropout_rates_{a}.png'))

# %%

fig = plt.figure(figsize=(6,6))
ax1 = fig.add_subplot()
        
for a in range(2006, 2015):

    dfss = df[df.year_in==a]

    y = dfss.year - a + 1
    m_fade = dfss.mi
    f_fade = dfss.fi
    m_rec = dfss.me
    f_rec = dfss.fe
    m_recs = m_rec > 0
    f_recs = f_rec > 0

    rnmx = np.random.normal(scale=0.1, size=sum(m_recs))
    rnmy = np.random.normal(scale=0.1, size=sum(m_recs))
    rnfx = np.random.normal(scale=0.1, size=sum(f_recs))
    rnfy = np.random.normal(scale=0.1, size=sum(f_recs))

    ymn = min(y[m_recs].min(), y[f_recs].min())
    txttop = max(m_fade.max(), f_fade.max())

    ax1.axhline(0, linestyle='--', color='silver', linewidth=1)
    #ax1.plot(y, m_fade, color=coloro, label='estudiantes varones')
    ax1.plot(y, f_fade, color=colora, label='estudiantes mujeres')

    #ax1.plot(y[f_recs]+rnfx, f_rec[f_recs]+rnfy, markersize=6,
    #        marker='o', mfc='None', mec=colora)
    for xx, yy in zip(y[f_recs], f_rec[f_recs]):
        ax1.plot(xx, yy)


    #ax1.plot(y[m_recs]+rnmx, m_rec[m_recs]+rnmy, 'o', color=coloro, markersize=3)

ax1.set_xlabel(f'años desde el inicio de la carrera ({a})')
ax1.set_ylabel('cantidad de alumnos')
ax1.set_xlim(0.5, 8.5)

plt.tight_layout()
fig.savefig(path.join(plotdir, 'dropout_rates_f.png'))

# %%
# FIGURA

fig = plt.figure(figsize=(10,5))
ax1 = fig.add_subplot()
mn = np.zeros(30)
cn = np.zeros(30)
k=0
for a in range(2006, 2015):
    dfss = df[df.year_in==a]
    y = dfss.year - a + 1
    m_fade = dfss.mi
    f_fade = dfss.fi
    f_fade = f_fade / f_fade.max()
    m_fade = m_fade / m_fade.max()
    ax1.axhline(0, linestyle='--', color='silver', linewidth=1)
    ax1.plot(y, m_fade, color=coloro, label='estudiantes varones')
    ax1.plot(y, f_fade, color=colora, label='estudiantes mujeres')
    mn[:len(f_fade)] = mn[:len(f_fade)] + f_fade
    mn[:len(m_fade)] = mn[:len(m_fade)] + m_fade
    cn[:len(f_fade)] +=1
    cn[:len(m_fade)] +=1
    k+=1
flt = cn>0
mn[flt] = mn[flt] / cn[flt]
err = np.sqrt(20*mn*(1-mn))/20
ax1.set_xlabel(f'años desde el inicio de la carrera ({a})')
ax1.set_ylabel('cantidad de alumnos')
k = list(cn).index(0)
ax1.plot(range(1,k+1), mn[:k], linestyle='--', linewidth=3, color='green')
ax1.plot(range(1,k+1), mn[:k]+err[:k], linestyle='--', linewidth=1, color='green')
ax1.plot(range(1,k+1), mn[:k]-err[:k], linestyle='--', linewidth=1, color='green')
#Px = list(range(1,k+1)) + list(range(k+1, 1, -1))
#Py = list(mn[:k]+err[:k]) + list(mn[:k]-err[:k])
#ax1.fill(Px, Py)
ax1.set_xlim(0.5, 12.5)
plt.tight_layout()
fig.savefig(path.join(plotdir, 'dropout_rates_normalized.png'))

# %% NORMALIZED MODEL                                                     %%

def model(t, alfa, beta):
    return np.exp(-((t-1)**(1/beta))/alfa)

from scipy.optimize import curve_fit

xdata = np.arange(2, 13)
ydata = mn[1:12]
p0 = [2, 1.5]
pars, cm = curve_fit(model, xdata, ydata, [2, 1.5])


# %% NORMALIZED PLOT                                                      %%

fig = plt.figure(figsize=(10,8))
ax1 = fig.add_subplot()
ax1.set_xlim(0.5, 12.5)
ax1.tick_params(axis='both', which='major', labelsize=20)
mn = np.zeros(30)
cn = np.zeros(30)
mnf = np.zeros(30)
cnf = np.zeros(30)
mnm = np.zeros(30)
cnm = np.zeros(30)
k=0
for a in range(2006, 2015):
    dfss = df[df.year_in==a]
    y = dfss.year - a + 1
    m_fade = dfss.mi
    f_fade = dfss.fi
    f_fade = f_fade / f_fade.max()
    m_fade = m_fade / m_fade.max()
    ax1.axhline(0, linestyle='--', color='silver', linewidth=1)
    ax1.plot(y[1:], m_fade[1:], color=coloro, lw=0.5)
    ax1.plot(y[1:], f_fade[1:], color=colora, lw=1.0,
    linestyle=':')
    mn[:len(f_fade)] = mn[:len(f_fade)] + f_fade
    mn[:len(m_fade)] = mn[:len(m_fade)] + m_fade
    cn[:len(f_fade)] +=1
    cn[:len(m_fade)] +=1

    mnf[:len(f_fade)] = mnf[:len(f_fade)] + f_fade
    cnf[:len(f_fade)] +=1
    mnm[:len(f_fade)] = mnm[:len(f_fade)] + m_fade
    cnm[:len(f_fade)] +=1
    k+=1
ax1.scatter(1, 1, color='k')
flt = cn>0
mn[flt] = mn[flt] / cn[flt]
mnf[flt] = mnf[flt] / cnf[flt]
mnm[flt] = mnm[flt] / cnm[flt]
err = np.sqrt(20*mn*(1-mn))/20
ax1.set_xlabel(f'years from enrollment', fontsize=20)
ax1.set_ylabel('retention fraction', fontsize=20)
k = list(cn).index(0)
#ax1.plot(range(2,k+1), mn[1:k], linestyle='--', linewidth=3, color='green')
#ax1.plot(range(2,k+1), mn[1:k]+err[:k], linestyle='--', linewidth=1, color='green')
#ax1.plot(range(2,k+1), mn[1:k]-err[:k], linestyle='--', linewidth=1, color='green')

t = np.linspace(2, 12, 100)
#ax1.plot(t, model(t, *pars), color='red')
p = model(t, *pars)
e = np.sqrt(25*p*(1-p))/25
#ax1.plot(t, model(t, *pars)+e, color='red')
#ax1.plot(t, model(t, *pars)-e, color='red')

op = {'linewidth': 2, 'linestyle': '--'}
ax1.plot(range(2,13), mnm[1:12], color=coloro, **op, label='avg. male')
ax1.plot(range(2,13), mnf[1:12], color=colora, **op, label='avg. female')

Px = np.concatenate([t, t[::-1]])
Py = np.concatenate([model(t, *pars)+e, (model(t, *pars)-e)[::-1]])
ax1.fill(Px, Py, color='blanchedalmond', label='theoretical uncertainty')
ax1.legend(fontsize=20)

plt.tight_layout()
fig.savefig(path.join(plotdir, 'dropout_rates_normalized_model.png'))

# %% END                                                                  %%

"""
Para ver las fuentes disponibles, en un jupyter notebook:

import matplotlib.font_manager
from IPython.core.display import HTML

def make_html(fontname):
    return "<p>{font}: <span style='font-family:{font}; font-size: 24px;'>{font}</p>".format(font=fontname)

code = "\n".join([make_html(font) for font in sorted(set([f.name for f in matplotlib.font_manager.fontManager.ttflist]))])

HTML("<div style='column-count: 2;'>{}</div>".format(code))

"""
