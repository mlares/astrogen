import bonobo
import pandas as pd
import datetime


def extract():
    D = pd.read_excel('../../data/raw/sociosAAA_historico.xlsx')
    yield D


def transform1(*args):
    D = args[0]

    hdr = D.keys()
    D = D.drop(hdr[6:], axis=1)

    today = datetime.date.today()
    today = pd.to_datetime(today)

    D['Fnac'] = pd.to_datetime(D['Fnac'], errors='coerce')

    yield D

def transform2(*args):
    print(args[0].shape)
    yield True

def load(*args):
    """Placeholder, change, rename, remove... """
    print(*args)


def get_graph(**options):
    """
    This function builds the graph that needs to be executed.

    :return: bonobo.Graph

    """
    graph = bonobo.Graph()
    graph.add_chain(extract,
                    transform1,
                    transform2,
                    load)

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


# The __main__ block actually execute the graph.
if __name__ == '__main__':
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser) as options:
        bonobo.run(
            get_graph(**options),
            services=get_services(**options)
        )
