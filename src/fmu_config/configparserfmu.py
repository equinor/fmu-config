import os
import errno
import pprint
import re
import getpass
import socket
from datetime import datetime

import json
import oyaml as yaml  # for ordered dicts!
import xtgeo

from ._loader import Loader

# just borrow a few useful things from xtgeo
xxx = xtgeo.common.XTGeoDialog()
logger = xxx.functionlogger(__name__)


class ConfigParserFMU(object):
    """Class for parsing config files for FMU."""

    def __init__(self):

        self._config = {}
        self._yamlfile = None

    @property
    def config(self):
        return self._config

    @property
    def yamlfile(self):
        return self._yamlfile

    def parse(self, yfile):
        """Parsing the YAML file (reading it)."""

        with open(yfile, 'r') as stream:
            self._config = yaml.load(stream, Loader=Loader)
        self._yamlfile = yfile

    def show(self):
        """Show the current configuration using prettyprinter"""

        pp = pprint.PrettyPrinter(indent=4)

        pp.pprint(self.config)

    def to_yaml(self, rootname='myconfig', destination=None, template=None,
                tool=None, createfolders=False):
        """Export the config as YAML files; one with true values and
        one with templated variables.

        Args:
            rootname: Root file name without extension. An extension
                .yml will be added for destination, and .tmpl
                for template output.
            destination: The directory path for the destination
                file. If None, than no output will be given
            template: The directory path for the templated
                file. If None, than no templated output will be given.
            tool (str): Using one of the specified tool sections in the
                master config, e.g. 'rms'. Default is None
            createfolders: If True then folders will be created if they
                do not exist.

        Raises:
            ValueError: If both destination and template output is None,
                or folder does not exist in advance, if createfolder=False.

        Example:

            >>> config.to_json('global_variables', destination='../')
        """

        if not destination and not template:
            raise ValueError('Both desitionation and template are None.'
                             'At least one of them has to be set!.')

        if createfolders:
            self._force_create_folders([destination, template])
        else:
            self._check_folders([destination, template])

        mystream = yaml.dump(self.config)
        mystream = ''.join(self._get_sysinfo()) + mystream

        cfg1 = self._get_dest_form(mystream)
        cfg2 = self._get_tmpl_form(mystream)

        # if tool is not None:
        #     cfg1 = cfg1[tool]
        #     cfg2 = cfg2[tool]

        if destination:
            out = os.path.join(destination, rootname + '.yml')
            with open(out, 'w') as stream:
                stream.write(cfg1)

        if template:
            out = os.path.join(destination, rootname + '.tmpl')
            with open(out, 'w') as stream:
                stream.write(cfg2)

    def to_json(self, rootname, destination=None, template=None,
                createfolders=False):
        """Export the config as JSON files; one with true values and
        one with templated variables.

        Args:
            rootname: Root file name without extension. An extension
                .json will be added for destination, and .tmpl
                for template output.
            destination: The directory path for the destination
                file. If None, than no output will be given
            template: The directory path for the templated
                file. If None, than no output will be given
            createfolders: If True then folders will be created if they
                do not exist.

        Raises:
            ValueError: If both destination and template output is None,
                or folder does not exist in advance, if createfolder=False.

        Example:

            >>> config.to_json('global_variables', destination='../')
        """

        if not destination and not template:
            raise ValueError('Both desitionation and template are None.'
                             'At least one of them has to be set!.')

        if createfolders:
            self._force_create_folders([destination, template])
        else:
            self._check_folders([destination, template])

        mystream = json.dumps(self.config, indent=4)

        if destination:
            cfg1 = self._get_dest_form(mystream)
            out = os.path.join(destination, rootname + '.json')
            with open(out, 'w') as stream:
                stream.write(cfg1)
        if template:
            cfg2 = self._get_tmpl_form(mystream)
            out = os.path.join(destination, rootname + '.tmpl')
            with open(out, 'w') as stream:
                stream.write(cfg2)

    def to_ipl(self, rootname='global_variables', destination=None,
               template=None, tool='rms'):
        """Export the config as a global variables IPL and template.

        Args:
            rootname (str): Root file name for the IPL config. Default is
                'global_variables'.
            destination (str): If given, the path to the global_variables.ipl.
            template (str): If given, the path to the global_variables.tmpl
                (for ERT to use).
            tool (str): Which section in the master to use (default is 'rms')

        """

        if not destination and not template:
            raise ValueError('Both desitionation and template are None.'
                             'At least one of them has to be set!.')

        cfg = self.config['rms']

        if destination is None:
            destfile = cfg['ipldestfile']
        else:
            destfile = os.path.join(destination, rootname + '.ipl')
        if template is None:
            tmplfile = cfg['ipltmplfile']
        else:
            tmplfile = os.path.join(template, rootname + '.yml')

        declarations = []
        expressions = []

        metadata = self._get_sysinfo(commentmarker='//')
        declarations.extend(metadata)

        hdecl, hlist = self._ipl_stringlist_format('horizons')
        if hdecl is not None:
            declarations.extend(hdecl)
            expressions.extend(hlist)

        hdecl, hlist = self._ipl_stringlist_format('zones')
        if hdecl is not None:
            declarations.extend(hdecl)
            expressions.extend(hlist)

        hdecl, hlist = self._ipl_freeform_format()
        if hdecl is not None:
            declarations.extend(hdecl)
            expressions.extend(hlist)

        expressions_dest = self._get_dest_form(expressions)
        expressions_tmpl = self._get_tmpl_form(expressions)

        with open(destfile, 'w') as stream:
            for line in declarations:
                stream.write(line)

            for line in expressions_dest:
                stream.write(line)

        with open(tmplfile, 'w') as stream:
            for line in declarations:
                stream.write(line)

            for line in expressions_tmpl:
                stream.write(line)

    def _ipl_stringlist_format(self, subtype):
        """Process the rms horizons etc, and return declarations and values."""

        cfg = self.config['rms'].get(subtype)
        if cfg is None:
            return None, None

        decl = []
        expr = []
        for variable in cfg:
            mydecl = 'String {}[]\n'.format(variable)
            decl.append(mydecl)

            array = cfg[variable]
            for i, element in enumerate(array):
                mylist = '{}[{}] = "{}"\n'.format(variable, i + 1, element)
                expr.append(mylist)

        expr.append('\n')

        return decl, expr

    def _ipl_freeform_format(self):
        """Process the RMS IPL YAML config freeform types."""

        decl = ['// Declare free form:\n']
        expr = ['// Free form expressions:\n']

        cfg = self.config['rms'].get('freeform')
        if cfg is None:
            return None, None

        for variable in cfg:
            print(variable)
            mydtype = cfg[variable]['dtype']
            if 'str' in mydtype:
                subtype = 'String'
            elif 'int' in mydtype:
                subtype = 'Int'
            elif 'float' in mydtype:
                subtype = 'Float'
            else:
                raise ValueError('Do not understand dtype: {}'.format(mydtype))

            myvalue = cfg[variable].get('value')
            myvalues = cfg[variable].get('values')

            if myvalue:
                listtype = ''
                fnutt = ''
                if subtype == 'String':
                    fnutt = '"'
                myexpr = '{} = {}{}{}\n'.format(variable, fnutt, myvalue,
                                                fnutt)
                expr.append(myexpr)
            elif myvalues:
                listtype = '[]'
                for i, val in enumerate(myvalues):
                    fnutt = ''
                    if subtype == 'String':
                        fnutt = '"'
                    myexpr = '{}[{}] = {}{}{}\n'.format(variable, i + 1,
                                                        fnutt, val, fnutt)
                    expr.append(myexpr)

            mydecl = '{} {}{}\n'.format(subtype, variable, listtype)
            decl.append(mydecl)

        return decl, expr

    def to_eclipse(self):
        """Export the config templates and actuals under `eclipse`"""

        cfg = self.config

        for deck in cfg['eclipse']:
            logger.info('Deck is {}'.format(deck))
            edeck = cfg['eclipse'][deck]

            content = edeck['content']
            content_dest = self._get_dest_form(content)
            content_tmpl = self._get_tmpl_form(content)
            logger.info(content_dest)
            logger.info(content_tmpl)

            with open(edeck['destfile'], 'w') as dest:
                dest.write(content_dest)

            with open(edeck['tmplfile'], 'w') as tmpl:
                tmpl.write(content_tmpl)

    # =========================================================================
    # Private methods
    # =========================================================================

    @staticmethod
    def _get_sysinfo(commentmarker='#'):
        """Return a text string that serves as info for the outpyt styles
        that support comments."""

        host = socket.gethostname()
        user = getpass.getuser()
        now = str(datetime.now())

        cmt = commentmarker

        meta = ['{} Autogenerated from global configuration.\n'.format(cmt),
                '{} DO NOT EDIT THIS FILE MANUALLY!\n'.format(cmt),
                '{} Machine {} by user {}, at {}\n'
                .format(cmt, host, user, now)]

        return meta

    @staticmethod
    def _force_create_folders(folderlist):

        for folder in folderlist:
            if folder is None:
                continue
            try:
                os.makedirs(folder)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

    @staticmethod
    def _check_folders(folderlist):

        for folder in folderlist:
            if folder is None:
                continue

            if not os.path.exists(folder):
                raise ValueError('Folder {} does not exist. It must either '
                                 'exist in advance, or the createfolders key'
                                 'must be True.'.format(folder))

    @staticmethod
    def _get_tmpl_form(stream):
        """Given variables..."""

        pattern = '[a-zA-Z0-9.]+~'

        if isinstance(stream, list):
            logger.info('STREAM is a list object')
            result = []
            for item in stream:
                moditem = re.sub(pattern, '', item)
                moditem = re.sub('"', '', moditem)
                result.append(moditem)
        elif isinstance(stream, str):
            result = re.sub(pattern, '', stream)
            result = re.sub('"', '', result)
        else:
            raise ValueError('Input for templateconversion neither string '
                             'or list')

        return result

    @staticmethod
    def _get_dest_form(stream):
        """Given variables..."""

        if isinstance(stream, list):
            logger.info('STREAM is a list object')
            result = []
            for item in stream:
                moditem = re.sub('\~.*>', '', item)
                result.append(moditem)
        elif isinstance(stream, str):
            result = re.sub('\~.*>', '', stream)
        else:
            raise ValueError('Input for templateconversion neither string '
                             'or list')

        return result
