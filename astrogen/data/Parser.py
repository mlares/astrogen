import numpy as np
from configparser import ConfigParser

DEFAULT_INI = '../../sets/set_experiment.ini'


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

def choice_yn(string, default_choice=None):
    if string.lower() in 'yesitrue':
        choice = True
    elif string.lower() in 'nofalse':
        choice = False
    else:
        if isinstance(default_choice, bool):
            choice = default_choice
        else:
            raise AttributeError('Check Y/N choice')
    return choice

def is_iterable(obj):
    from collections.abc import Iterable
    return isinstance(obj, Iterable)

# Idea: change named tuple by class:
# class parameters:
# initialize with default parameters.


class Parser(ConfigParser):
    """parser class.

    Manipulation of configuration parameters. This method allows to read a
    configuration file or to set parameters for a Constrained Causally
    Conected Network (C3Net) model.
    """

    def __init__(self, argv=None, *args, **kwargs):
        """Initialize a parser.

        Parameters
        ----------
            None
        Returns
        -------
            None
        Raises
        ------
            Instantiate a Parser object.
        """
        super().__init__()
        self.message = None
        self.check_file(argv)
        self.read_config_file()

        self.load_config(*args, **kwargs)
        self.check_settings()

    def check_file(self, sys_args=""):
        """Parse paramenters for the simulation from a .ini file.

        Parameters
        ----------
            None

        Raises
        ------
            None

        Returns
        -------
            Updates 'filename' variable in Parser class object.
        """
        from os.path import isfile

        mess = ("Configuration file expected:"
                "\n\t filename or CLI input"
                "\n\t example:  python run_experiment.py"
                f"\n\t {DEFAULT_INI}"
                "\n\t Using default configuration file")
        if isinstance(sys_args, str):
            if isfile(sys_args):
                msg = f"Loading configuration parameters from {sys_args}"
                self.message = msg
                filename = sys_args
            else:
                self.message = "Input argument is not a valid file\
                                Using default configuration file instead"
                filename = DEFAULT_INI

        elif isinstance(sys_args, list):

            if len(sys_args) == 2:
                filename = sys_args[1]

                if isfile(filename):
                    msg = f"Loading configuration parameters from {filename}"
                    self.message = msg
                else:
                    self.message = mess
                    filename = DEFAULT_INI
            else:
                self.message = mess
                filename = DEFAULT_INI

        else:
            self.message = mess
            filename = DEFAULT_INI

        self.filename = filename

    def read_config_file(self):
        """Parse paramenters for the simulation from a .ini file.

        Parameters
        ----------
            None

        Raises
        ------
            None

        Returns
        -------
            None
        """
        self.read(self.filename)

    def load_config(self, keys=None, values=None, *args, **kwargs):
        """Load parameters from config file.

        Parameters
        ----------
        keys: list of strings
            parameters to be reset (mandatory) or set (optional)
        values: list of strings
            Values of the parameters to be reset (mandatory) or set (optional)

        Raises
        ------
            None

        Returns
        -------
        self.config: named tuple
            Updates list of parameters as a named tuple
        """
        from collections import namedtuple
 


    def check_settings(self):
        """Check if parameters make sense.

        Parameters
        ----------
            None

        Raises
        ------
            None

        Returns
        -------
            Exception if settings have inconsistencies.
        """
        from os import path, makedirs

