import pprint
import yaml

from ._loader import Loader


class ConfigParser(object):
    """Class for parsing config files for FMU."""

    def __init__(self):

        self._config = {}

    @property
    def config(self):
        return self._config

    def parse(self, yfile):
        """Parsing the YAML file (reading it)."""

        with open(yfile, 'r') as stream:
            self._config = yaml.load(stream, Loader=Loader)

    def show(self):
        """Show the current configuration using prettyprinter"""

        pp = pprint.PrettyPrinter(indent=4)

        pp.pprint(self.config)

    def to_ipl(self, iplfile):
        """Export the config as a global variables IPL."""

        cfg = self.config

        with open(iplfile, 'w') as stream:

            # declarations
            stream.write('// Declare horizons\n')
            for ipltype in cfg['horizons']:
                stream.write('String {}[]\n'.format(ipltype))

            # print the actual arrays
            for ipltype in cfg['horizons']:
                arr = cfg['horizons'][ipltype]
                stream.write('\n')
                for i, element in enumerate(arr):
                    stream.write('{}[{}] = "{}"\n'
                                 .format(ipltype, i + 1, element))
