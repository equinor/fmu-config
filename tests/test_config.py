# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os.path

from fmu import config
# import fmu.config.fmuconfigrunner as fmurun

from xtgeo.common import XTGeoDialog

tfile1 = 'tests/data/yaml/troll1/global_variables.yml'
tfile2 = 'tests/data/yaml/troll2/global_master_config.yml'
rfile1 = 'tests/data/yaml/reek1/global_variables.yml'

xxx = XTGeoDialog()
logger = xxx.basiclogger(__name__)
testdir = 'TMP'

try:
    os.makedirs(testdir)
except OSError:
    if not os.path.isdir(testdir):
        raise


def test_basic_troll():
    """Test basic behaviour"""

    cfg = config.ConfigParserFMU()

    assert isinstance(cfg, config.ConfigParserFMU)

    cfg.parse(tfile1)

    cfg.show()

    assert len(cfg.config['horizons']) == 6


def test_basic_troll2():
    """Test basic behaviour"""

    cfg = config.ConfigParserFMU()

    assert isinstance(cfg, config.ConfigParserFMU)

    cfg.parse(tfile2)

    cfg.show()
    cfg.show(style='json')

    # export the config as a global variables IPL
    logger.info('Test dir is {}'.format(testdir))
    cfg.to_ipl(destination=os.path.join(testdir),
               template=os.path.join(testdir))


# def test_basic_reek():
#     """Test basic behaviour, Reek setup"""

#     cfg = config.ConfigParserFMU()

#     assert isinstance(cfg, config.ConfigParserFMU)

#     cfg.parse(rfile1)

#     cfg.show()

#     # will write the eclipse files
#     cfg.to_eclipse()
#     cfg.to_ipl()
#     cfg.to_yaml('myyaml', destination='TMP')
#     cfg.to_json('myjson', destination='TMP')

#     # assert len(cfg.config['horizons']) == 6

#     # # export the config as a global variables IPL
#     # cfg.to_ipl('myfile')


# def test_command_make_ipls():
#     """Make IPL both global_variable.ipl and global_variables.tmpl, Reek."""
#     fmurun.main(['--input', rfile1, '--mode', 'ipl'])  # noqa


# def test_command_make_yamls():
#     """Make IPL both global_variables_rms.yml and global_variables_tmpl.yml,
#     Reek.
#     """

#     fmurun.main(['--input', rfile1, '--mode', 'yaml', --tool, 'rms'])  # noqa
