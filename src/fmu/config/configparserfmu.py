"""Module for parsing global configuration for FMU.

This module will be ran from the `fmuconfig` script, which is the
front-end for the user.
"""

from __future__ import division, absolute_import
from __future__ import print_function

import os
import sys
import errno
import re
import getpass
import socket
import datetime

import json
import oyaml as yaml  # for ordered dicts!

from fmu.config._loader import Loader
from fmu.config import etc

xfmu = etc.Interaction()
logger = xfmu.functionlogger(__name__)


class ConfigParserFMU(object):
    """Class for parsing global config files for FMU."""

    def __init__(self):
        self._config = {}
        self._yamlfile = None
        logger.debug('Ran __init__')

    @property
    def config(self):
        """Get the current config as a Python dictionary (read only)."""
        return self._config

    @property
    def yamlfile(self):
        """The name of the input YAML formatted file (read only)."""
        return self._yamlfile

    def parse(self, yfile):
        """Parsing the YAML file (reading it)."""

        with open(yfile, 'r') as stream:
            self._config = yaml.load(stream, Loader=Loader)
        self._yamlfile = yfile

    def show(self, style='yaml'):
        """Show (print) the current configuration to STDOUT.

        Args:
            style: Choose between 'yaml' (default), or 'json'"""

        xfmu.echo('Output of configuration:')
        if style in ('yaml', 'yml'):
            yaml.dump(self.config, stream=sys.stdout)
        elif style in ('json', 'jason'):
            stream = json.dumps(self.config, indent=4, default=str)
            print(stream)

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
            raise ValueError('Both destionation and template are None.'
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

    def to_ipl(self, rootname='global_variables.ipl', destination=None,
               template=None, tool='rms'):
        """Export the config as a global variables IPL and/or template.

        Args:
            rootname: Root file name without extension. An extension
                .ipl will be added for destination, and .tmpl
                for template output.
            destination (str): The output file destination (folder)
            template (str): The folder for the templated version of the
                IPL (for ERT).
            tool (str): Which section in the master to use (default is 'rms')
        """

        if not destination and not template:
            raise ValueError('Both destination and template for IPL cannot '
                             'be None.')

        declarations = []
        expressions = []

        metadata = self._get_sysinfo(commentmarker='//')
        declarations.extend(metadata)

        hdecl, hlist = self._ipl_stringlist_format('horizons', tool=tool)
        if hdecl is not None:
            declarations.extend(hdecl)
            expressions.extend(hlist)

        hdecl, hlist = self._ipl_stringlist_format('zones', tool=tool)
        if hdecl is not None:
            declarations.extend(hdecl)
            expressions.extend(hlist)

        hdecl, hlist = self._ipl_freeform_format()
        if hdecl is not None:
            declarations.extend(hdecl)
            expressions.extend(hlist)

        if template:
            expressions_dest = self._get_tmpl_form(expressions)
        else:
            expressions_dest = self._get_dest_form(expressions)

        with open(destination, 'w') as stream:
            for line in declarations:
                stream.write(line)

            for line in expressions_dest:
                stream.write(line)

    def _ipl_stringlist_format(self, subtype, tool='rms'):
        """Process the rms horizons etc, and return declarations and values."""

        cfg = self.config[tool].get(subtype)
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
        """Process the RMS IPL YAML config freeform types.

        The freeform types are e.g. like this::

            rms:
              GOC:
                dtype: float
                values:
                  - 2010.0
                  - 2016.0

        I.e. they are defined as BIG_LETTER keys within
        the RMS section, in contrast to 'horizons' and 'zones'
        """

        decl = ['// Declare free form:\n']
        expr = ['// Free form expressions:\n']

        cfg = self.config['rms']

        # collect uppercase keys in 'rms'
        freeform_keys = []
        for key in cfg:
            if all(word[0].isupper() for word in key if word.isalpha()):
                freeform_keys.append(key)

        if len(freeform_keys) == 0:
            return None, None

        for variable in freeform_keys:
            print('Variable to process is {}'.format(variable))
            expr.append('\n')
            mydtype = cfg[variable]['dtype']
            if 'str' in mydtype:
                subtype = 'String'
            elif 'int' in mydtype:
                subtype = 'Int'
            elif 'float' in mydtype:
                subtype = 'Float'
            elif 'date' in mydtype:
                subtype = 'String'
            else:
                raise ValueError('Do not understand dtype: {}'.format(mydtype))

            myvalue = cfg[variable].get('value')
            myvalues = cfg[variable].get('values')

            if mydtype == 'date':
                if myvalue:
                    if type(myvalue) in (datetime.datetime, datetime.date):
                        myvalue = str(myvalue)
                        myvalue = myvalue.replace('-', '')

                if myvalues:
                    mynewvalues = []
                    for val in myvalues:
                        if type(val) in (datetime.datetime, datetime.date):
                            val = str(val)
                            val = val.replace('-', '')
                            mynewvalues.append(val)
                    myvalues = mynewvalues

            if mydtype == 'datepair':
                if myvalue:
                    date1, date2 = myvalue
                    if type(date1) in (datetime.datetime, datetime.date):
                        date1 = str(date1)
                        date1 = date1.replace('-', '')

                    if type(date2) in (datetime.datetime, datetime.date):
                        date2 = str(date2)
                        date2 = date1.replace('-', '')
                    myvalue = date1 + '_' + date2

                if myvalues:
                    mynewvalues = []
                    for val in myvalues:
                        date1, date2 = val
                        if type(date1) in (datetime.datetime, datetime.date):
                            date1 = str(date1)
                            date1 = date1.replace('-', '')
                        if type(date2) in (datetime.datetime, datetime.date):
                            date2 = str(date2)
                            date2 = date2.replace('-', '')
                        mynewvalues.append(date1 + '_' + date2)

                    myvalues = mynewvalues

            listtype = ''
            if myvalue:
                fnutt = ''
                if subtype == 'String':
                    fnutt = '"'
                myexpr = '{} = {}{}{}\n'.format(variable, fnutt, myvalue,
                                                fnutt)
                expr.append(myexpr)

            # list of values:
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

        decl.append('{}\n'.format('/' * 79))
        return decl, expr

    def to_eclipse(self):
        """Export the config templates and actuals under `eclipse`"""

        cfg = self.config

        for deck in cfg['eclipse']:
            print('Deck is %s', deck)
            edeck = cfg['eclipse'][deck]

            content = edeck['content']
            content_dest = self._get_dest_form(content)
            content_tmpl = self._get_tmpl_form(content)
            print(content_dest)
            print(content_tmpl)

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
        now = str(datetime.datetime.now())

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
            print('STREAM is a list object')
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
            print('STREAM is a list object')
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
