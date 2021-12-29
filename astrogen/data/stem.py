# %%

from pipeline import *
import pandas as pd
import matplotlib.pyplot as plt

# %%

D = pd.read_excel('../../data/collect/CIC_p_año_edad.xlsx')

FALT GENERO ??

# %%

D.drop('ID DATASET', axis=1, inplace=True)

# %%
"""
Seleccionar solo las  areas STEM:
    KE - Ciencias Exactas y Naturales
    KT - Tecnología
"""

fltr = D['Area del Conocimiento'].str.contains('KE|KT')
D = D[fltr]

D.drop(['Area del Conocimiento'], axis=1, inplace=True)

# %%

df2017 = D[D.Año==2007].groupby(['Categoría', 'Rango de Edad']).count()
df2020 = D[D.Año==2020].groupby(['Categoría', 'Rango de Edad']).count()

# %%


PLOT BARRAS Y HATCH

fig = plt.figure()
patterns = [ "|" , "\\" , "/" , "+" , "-", ".", "*","x", "o", "O" ]
ax = fig.add_subplot(111)
for i in range(len(patterns)):
    ax.bar(i, 3, color='white', edgecolor='black', hatch=patterns[i])
plt.show()




