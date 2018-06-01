# -*- coding: utf-8 -*-
import fmu_config
import fmu_config.fmuconfigrunner as rr

from xtgeo.common import XTGeoDialog

tfile1 = 'tests/data/yaml/troll1/global_variables.yaml'
rfile1 = 'tests/data/yaml/reek1/global_variables.yaml'

xxx = XTGeoDialog()
logger = xxx.basiclogger(__name__)
testdir = xxx.testsetup()


def test_basic_troll():
    """Test basic behaviour"""

    cfg = fmu_config.ConfigParserFMU()

    assert isinstance(cfg, fmu_config.ConfigParserFMU)

    cfg.parse(tfile1)

    cfg.show()

    assert len(cfg.config['horizons']) == 6

    # export the config as a global variables IPL
    # cfg.to_ipl(testdir + '/myfile.ipl')


def test_basic_reek():
    """Test basic behaviour, Reek setup"""

    cfg = fmu_config.ConfigParserFMU()

    assert isinstance(cfg, fmu_config.ConfigParserFMU)

    cfg.parse(rfile1)

    cfg.show()

    # will write the eclipse files
    cfg.to_eclipse()
    cfg.to_ipl()
    cfg.to_yaml('myyaml', destination='TMP')
    cfg.to_json('myjson', destination='TMP')

    # assert len(cfg.config['horizons']) == 6

    # # export the config as a global variables IPL
    # cfg.to_ipl('myfile')


def test_command_make_ipls():
    """Make IPL both global_variable.ipl and global_variables.tmpl, Reek."""
    rr.main(['--input', rfile1, '--mode', 'ipl'])  # noqa


def test_command_make_yamls():
    """Make IPL both global_variables_rms.yml and global_variables_tmpl.yml,
    Reek.
    """

    rr.main(['--input', rfile1, '--mode', 'yaml', --tool, 'rms'])  # noqa
