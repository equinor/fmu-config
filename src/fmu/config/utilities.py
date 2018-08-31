# -*- coding: utf-8 -*-
"""Module with some simple functions, e.g. for parsing for YAML into RMS
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

# for ordered dicts!
from fmu.config import oyaml as yaml


def yaml_load(filename, safe=True, tool=None):
    """Load as YAML file, return a dictionary which is the config.

    Args:
        filename (str): Name of file (YAML formatted)
        safe (bool): If True (default), then use `safe_load`
        tool (str): Refers to a particular main section in the config.
            Default is None, which measn 'all'.

    Example::
        >>> import fmu.config.utilities as utils
        >>> cfg = utils.yaml_load('somefile.yml')

    """

    if not os.path.isfile(filename):
        raise IOError('File {} cannot be read'.format(filename))

    with open(filename, 'r') as stream:
        if safe:
            cfg = yaml.safe_load(stream)
        else:
            cfg = yaml.load(stream)

    if tool is not None:
        try:
            newcfg = cfg[tool]
            cfg = newcfg
        except Exception as exc:
            print('Cannot import: {}'.format(exc))
            return None

    return cfg
