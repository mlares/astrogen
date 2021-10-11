import bonobo
import datetime
 
# def test_step():
#     print('a')
#     yield True
# 
# def test_step2():
#     print('b')
# 
# graph = bonobo.Graph(
#         test_step(),
#         test_step2()
#         )
# bonobo.run(graph) 




def S01_read_aaa_data():
    D = pd.read_excel('../../data/raw/sociosAAA_historico.xlsx')
    yield D
   
    """
    hdr = D.keys()
    D = D.drop(hdr[6:], axis=1)

    today = datetime.date.today()
    today = pd.to_datetime(today)

    D['Fnac'] = pd.to_datetime(D['Fnac'], errors='coerce')
    #D["Fnac"].replace({pd.NaT: today}, inplace=True)

    edad = []
    for day in D['Fnac']:
        if pd.isnull(day):
            edad.append(-1)
        else:
            edad.append(relativedelta(today, day).years)

    D['Fnac'] = D['Fnac'].dt.strftime("%Y")

    D['edad'] = edad

    D['DNI'] = D['DNI'].apply(lambda x: x if np.isreal(x) else np.NaN)


    D.rename(columns={"DNI": "dni"}, inplace=True)
    D.rename(columns={"Nac": "nac"}, inplace=True)
    D.rename(columns={"Aff": "aff"}, inplace=True)
    D.rename(columns={"Fnac": "fnac"}, inplace=True)
    D.rename(columns={"Nombre": "nombre"}, inplace=True)
    D.rename(columns={"Apellido": "apellido"}, inplace=True)

     
    # Estimación de la edad a partir del DNI ------------------------

    filt = D['nac'].str.contains('arg').values
    Darg = D[filt & D.edad.notnull()]
    df = Darg[Darg['dni'].between(1.e7, 4.e7) & Darg['edad'].between(20,70)]

    x = df['dni']
    y = df['edad']

    def age(dni, a, b, c):
        return a - b*dni*1.e-7 + c*(dni*1.e-7-2.5)**2

    x0 = [83, 16, 1.5]
    pars_age, cov = curve_fit(age, x, y, x0)

    xx= np.linspace(1.e7, 4.e7, 50)

    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot()

    ax.plot(x, y, marker='o', linestyle='None', mec='cornflowerblue',
            mfc='paleturquoise')

    ax.plot(xx, age(xx, *pars_age), linestyle='-', color='orchid')
    ax.set_xlabel('dni')
    ax.set_ylabel('edad')
    plt.tight_layout()

    fig.savefig('dni_age.pdf')
    # -----------------------------------------

    N = D.shape[0]
    gender = []
    edad_fit = []
    for i in range(N):
        name = D['nombre'].iloc[i]
        g = get_gender2(name)
        gender.append(g)

        edad = D['edad'].iloc[i]
        dni = D['dni'].iloc[i]

        if edad < 1 and not np.isnan(dni):
            edad = age(dni, *pars_age)
        if edad < 1 and np.isnan(dni):
            edad = np.nan
        edad_fit.append(edad)

    D['genero'] = gender
    D['edad'] = edad_fit

    D['cic'] = ''
    D['docencia'] = ''
    D['lugar'] = ''
    D['area'] = ''
    D['status'] = ''
    D['aaa'] = ''

    D.dni = D.dni.apply(lambda x: int(x) if pd.notna(x) else '')
    D.edad = D.edad.apply(lambda x: int(x) if pd.notna(x) else '')

    cols = ['apellido', 'nombre', 'genero', 'aff', 'lugar', 'aaa', 'area',
            'nac', 'dni', 'fnac', 'edad', 'cic', 'docencia', 'status']
    D = D[cols]

    yield D
    """


def SXX_read_astro_all():
    df = pd.read_excel('astro_all.xlsx', sheet_name="todos")
    yield df


def S02_clean_columns():
    df['senior'] = df.edad > 50
    yield df


pipeline = bonobo.Graph(
    test_step,
    test_step2
)


def extract():
    """Placeholder, change, rename, remove... """
    D = pd.read_excel('../../data/raw/sociosAAA_historico.xlsx')
    yield D


def transform(*args):
    """Placeholder, change, rename, remove... """
    yield D.shape

def load(*args):
    """Placeholder, change, rename, remove... """
    print(*args)
 

def get_graph(**options):
    """
    This function builds the graph that needs to be executed.

    :return: bonobo.Graph

    """
    graph = bonobo.Graph()
    #graph.add_chain(extract, transform, load)
    graph.add_chain(test_step, test_step2, S01_read_aaa_data)

    return graph


def get_services(**options):
    """
    This function builds the services dictionary, which is a simple dict of names-to-implementation used by bonobo
    for runtime injection.

    It will be used on top of the defaults provided by bonobo (fs, http, ...). You can override those defaults, or just
    let the framework define them. You can also define your own services and naming is up to you.

    :return: dict
    """
    return {}

 

if __name__ == '__main__':
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser) as options:
        bonobo.run(
            get_graph(**options),
            services=get_services(**options)
        )








def test_step():
    yield True

def test_step2():
    yield True   

graph = bonobo.Graph(
        test_step,
        test_step2
        )
bonobo.run(graph)






pipeline = bonobo.Graph(
    S01_read_aaa_data()
)

bonobo.run(pipeline)  
