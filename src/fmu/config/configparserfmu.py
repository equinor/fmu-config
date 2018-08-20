# -*- coding: utf-8 -*-
"""Module for parsing global configuration for FMU.

This module will be ran from the `fmuconfig` script, which is the
front-end for the user.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import errno
import re
import getpass
import socket
import datetime
import json

# for ordered dicts!
from fmu.config import oyaml as yaml

from fmu.config._loader import Loader
from fmu.config import etc

from fmu.config import _configparserfmu_ipl

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
        """The name of the input master YAML formatted file (read only)."""
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
        # pylint: disable=too-many-arguments

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
                master config, e.g. 'rms'. Default is None which means all.
            createfolders (bool): If True then folders will be created if they
                do not exist (default is False).

        Raises:
            ValueError: If both destination and template output is None,
                or folder does not exist in advance, if createfolder=False.

        Example:

            >>> config.to_yaml('global_variables', destination='../')
        """

        if not destination and not template:
            raise ValueError('Both desitionation and template are None.'
                             'At least one of them has to be set!.')

        if createfolders:
            self._force_create_folders([destination, template])
        else:
            self._check_folders([destination, template])

        if tool is not None:
            mystream = yaml.dump(self.config[tool])
        else:
            mystream = yaml.dump(self.config)

        mystream = ''.join(self._get_sysinfo()) + mystream

        cfg1 = self._get_dest_form(mystream)
        cfg2 = self._get_tmpl_form(mystream)

        if destination:
            out = os.path.join(destination, rootname + '.yml')
            with open(out, 'w') as stream:
                stream.write(cfg1)

        if template:
            out = os.path.join(destination, rootname + '.tmpl')
            with open(out, 'w') as stream:
                stream.write(cfg2)

    def to_json(self, rootname, destination=None, template=None,
                createfolders=False, tool=None):
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
            tool (str): Using one of the specified tool sections in the
                master config, e.g. 'rms'. Default is None which means all.
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

        if tool is not None:
            mycfg = self.config[tool]
        else:
            mycfg = self.config

        mystream = json.dumps(mycfg, indent=4)

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
               template=None, createfolders=False, tool='rms'):
        """Export the config as a global variables IPL and/or template.

        Args:
            rootname (str): Root file name without extension. An extension
                `ipl` will be added for destination, and `tmpl`
                for template output.
            destination (str): The output file destination (folder).
            template (str): The folder for the templated version of the
                IPL (for ERT).
            createfolders: If True then folders will be created if they
                do not exist.
            tool (str): Which section in the master to use (default is 'rms').

        """

        if createfolders:
            self._force_create_folders([destination, template])
        else:
            self._check_folders([destination, template])

        # keep most code in separate file ( a bit lengthy)
        _configparserfmu_ipl.to_ipl(self, rootname=rootname,
                                    destination=destination,
                                    template=template,
                                    tool=tool)

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
            except OSError as errmsg:
                if errmsg.errno != errno.EEXIST:
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
    def _get_required_form(stream, template=False, ipl=False):
        """Given a variable on form 1.0 ~ <SOME>, return the required form.

        For single values, it should be flexible how it looks like, e.g.::

            19.0~<SOME>
            19.0 ~ <SOME>

        If ipl is True and template is false, it should return::

            19.0  // <SOME>

        If ipl is True and template is True, it should return::

            <SOME>  // 19.0

        Args:
            stream (:obj:`str` or :obj:`list` of :obj:`str`): Input string
                or list of strings to break up
            template (bool): If template mode
            ipl (bool): If IPL mode
        """

        result = None

        if isinstance(stream, list):
            pass
        elif isinstance(stream, str):

            if '~' in stream:
                value, tvalue = stream.split('~')
                value = value.strip()
                tvalue = tvalue.strip()

                if ipl:
                    if template:
                        result = tvalue + '  // ' + value
                    else:
                        result = value + '  // ' + tvalue
                else:
                    if template:
                        result = tvalue
                    else:
                        result = value

        else:
            raise ValueError('Input for templateconversion neither string '
                             'or list')

        return result

    @staticmethod
    def _get_tmpl_form(stream):
        """Given variables..."""

        pattern = '[a-zA-Z0-9.\s]+~\s*'

        if isinstance(stream, list):
            print('STREAM is a list object')
            result = []
            for item in stream:
                moditem = re.sub(pattern, '', item)
                moditem = re.sub('"', '', moditem)
                moditem = ' ' + moditem.strip()
                result.append(moditem)
        elif isinstance(stream, str):
            print('STREAM is a str object')
            result = re.sub(pattern, ' ', stream)
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
                moditem = re.sub('~.*>', '', item)
                result.append(moditem)
        elif isinstance(stream, str):
            result = re.sub('~.*>', '', stream)
        else:
            raise ValueError('Input for templateconversion neither string '
                             'or list')

        return result
