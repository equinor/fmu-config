import yaml

from ._loader import Loader


class ConfigParser(object):
    """Class for parsing config files for FMU."""

    def __init__(self):

        self._config = {}

    def parse(self, yfile):
        """Parsing the YAML file (reading it)."""

        with open(yfile, 'r') as stream:
            self._config = yaml.load(stream, Loader=Loader)
