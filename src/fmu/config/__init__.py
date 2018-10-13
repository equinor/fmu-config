# -*- coding: utf-8 -*-

"""Top-level package for fmu_config"""

from ._theversion import theversion
__version__ = theversion()

del theversion

from .configparserfmu import ConfigParserFMU  # noqa
