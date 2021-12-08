# %%
import pandas as pd
import numpy as np
import sqlite3
import seaborn as sns
from os import path
from matplotlib import pyplot as plt
from matplotlib import colors
import plotly.express as px
import plotly.graph_objects as go

# %%
plotdir = '../../figures/'
colora = 'mediumpurple'
coloro = 'lightseagreen'
dcolora = (0.5764705882, 0.43921569, 0.85882353, 0.1)
dcoloro = (0.1254901961, 0.69803922, 0.66666667, 0.1)

# %%
conn = sqlite3.connect('../../data/redux/astrogen_DB_anonymous.db')
c = conn.cursor()
query = ('''  
         SELECT genero, edad, cc20
         FROM people
         WHERE cc20 is not NULL
         ''')
c.execute(query)
cnames = ['ID', 'genero', 'edad', 'Hindex', 'Npapers', 
          'cc07', 'cc08', 'cc09', 'cc10', 'cc11', 'cc12', 'cc13',
          'cc14', 'cc15', 'cc16', 'cc17', 'cc18', 'cc19', 'cc20']
cnames = ['genero', 'edad', 'cc20']
df = pd.DataFrame(c.fetchall(), columns=cnames)
conn.close()
# %%

fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot()
my_pal = {"m": dcoloro, "f": dcolora}
vs = sns.violinplot(ax=ax, x="cc20", y="edad", data=df,
               hue='genero', palette=my_pal, split=True)
ax.set_xticklabels(['doc','postdoc','I', 'II', 'III', 'IV', 'V'])
ax.set_xlabel('Category')
ax.set_ylabel('Age distribution')

for v in vs.collections:
    v.set_alpha(0.5)

fig.savefig(path.join(plotdir, 'violins_conicet.png'))

# %%
plt.style.use('seaborn-whitegrid')

# %%
gen    = df.genero
age    = df.edad
cic    = df.cc20
tipo= [1, 2, 3, 4, 5]
# %%
pointpos_male  = [-0.6,-0.4,-0.6,-0.3,-0.2]
pointpos_female  = [0.40,0.4,0.5,0.3,0.2]
show_legend = [True,False,False,False,False]

fig = go.Figure()

for i in range(len(tipo)):
    fig.add_trace(go.Violin(x = cic[(gen == 'm') & (age >0) & (cic==tipo[i])],
                            y = age[(gen == 'm') & (age >0) & (cic==tipo[i])],
                            legendgroup='M', scalegroup='M', name='M',
                            side='negative',
                            pointpos=pointpos_male[i], # where to position points
                            line_color='lightseagreen',
                            showlegend=show_legend[i])
             )
    fig.add_trace(go.Violin(x = cic[(gen == 'f') & (age >0) & (cic==tipo[i])],
                            y = age[(gen == 'f') & (age >0) & (cic==tipo[i])],
                            legendgroup='F', scalegroup='F', name='F',
                            side='positive',
                            pointpos=pointpos_female[i],
                            line_color='mediumpurple',
                            showlegend=show_legend[i])
             )
             
# update characteristics shared by all traces
fig.update_traces(meanline_visible=True,
                  points='all', # show all points
                  jitter=0.05,  # add some jitter on points for better visibility
                  scalemode='count') #scale violin plot area with total count
fig.update_layout(
    margin=dict(l=20, r=20, t=25, b=20), 
    template="simple_white", 
    title_text="Age distribution",
    violingap=0, violingroupgap=0, violinmode='overlay')

fig.update_yaxes( # the y-axis is in dollars
     showgrid=True)

fig.write_image(path.join(plotdir, 'vio.png'))
# %%
