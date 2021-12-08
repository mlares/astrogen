# %%
import pandas as pd
import numpy as np
import sqlite3
from os import path
from matplotlib import pyplot as plt
 

# %%
conn = sqlite3.connect('../../data/redux/astrogen_DB_anonymous.db')
c = conn.cursor()

c.execute('''  
                SELECT * FROM famaf
          ''')

cnames = ['year_in', 'mi', 'fi', 'me', 'fe', 'year', 'duration']
df = pd.DataFrame(c.fetchall(), columns=cnames)
print (df)

conn.close()


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
         color=colora, label='estudiantes mujeres')
ax1.plot(byear.index, byear['mi'], 
         color=coloro, label='estudiantes varones')
ax1.legend()
ax1.set_xlabel('year')
ax1.set_ylabel('dN/d(year)')

ax2 = fig.add_subplot(2,1,2)
ax2.plot(byear.index, byear['fe'].cumsum(), color=colora, label='egresadas mujeres')
ax2.plot(byear.index, byear['me'].cumsum(), color=coloro, label='egresados varones')
ax2.legend()
ax2.set_xlabel('year')

plt.tight_layout()
fig.savefig(plotdir + 'graduates_by_year.png')



# %%
# tiempo que tardan en terminar la carrera

dur_m = []
for r in df[df.me>0].itertuples():
    dur_m = dur_m + int(r.me) * [r.duration]

dur_f = []
for r in df[df.fe>0].itertuples():
    dur_f = dur_f + int(r.fe) * [r.duration]

bins = np.arange(4.5, 14.5)


fig = plt.figure(figsize=(6,6))
# #7aeae3
ax1 = fig.add_subplot()
ax1.hist(dur_f, bins=bins, histtype='stepfilled', linewidth=0,
         color='#a084e1', alpha=0.5, label='estudiantes mujeres')
ax1.hist(dur_f, bins=bins, histtype='step', linewidth=1,
         color=colora)

ax1.hist(dur_m, bins=bins, histtype='step', linewidth=2,
         color=coloro, label='estudiantes varones')

ax1.legend()
ax1.set_xlabel('duración de la carrera en años')
ax1.set_ylabel('número de estudiantes recibidos')

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



