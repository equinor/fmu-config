# -*- coding: utf-8 -*-
"""Testing fmu-config."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os.path
import json

import fmu.config as config
from fmu.config import oyaml as yaml
# import fmu.config.fmuconfigrunner as fmurun

JFILE1 = 'tests/data/yaml/jsverdrup/global_master_variables.yml'
TFILE1 = 'tests/data/yaml/troll1/global_variables.yml'
TFILE2 = 'tests/data/yaml/troll2/global_master_config.yml'
RFILE1 = 'tests/data/yaml/reek1/global_variables.yml'

fmux = config.etc.Interaction()
logger = fmux.basiclogger(__name__)

# always this statement
if not fmux.testsetup():
    raise SystemExit()


def test_jsverdrup():
    """Test table output behaviour"""

    cfg = config.ConfigParserFMU()

    assert isinstance(cfg, config.ConfigParserFMU)

    cfg.parse(JFILE1)

    cfg.show()

    cfg.to_table(rootname='JS', destination=fmux.tmpdir,
                 template=fmux.tmpdir, entry='global.FWL', sep='      ')


def test_basic_troll():
    """Test basic behaviour"""

    cfg = config.ConfigParserFMU()

    assert isinstance(cfg, config.ConfigParserFMU)

    cfg.parse(TFILE1)

    cfg.show()

    assert len(cfg.config['horizons']) == 6


def test_to_yaml_troll2():
    """Test the output for the YAML files, both templated and normal for rms"""

    cfg = config.ConfigParserFMU()

    assert isinstance(cfg, config.ConfigParserFMU)

    cfg.parse(TFILE2)
    rootn = 'troll2_yaml'

    cfg.to_yaml(rootname=rootn, destination=fmux.tmpdir,
                template=fmux.tmpdir, tool='rms')

    # now read the files again to assert tests
    with open(os.path.join(fmux.tmpdir, rootn + '.yml'), 'r') as stream:
        cfg_yml = yaml.load(stream)

    with open(os.path.join(fmux.tmpdir, rootn + '.tmpl'), 'r') as stream:
        cfg_tmpl = yaml.load(stream)

    assert cfg_yml['KH_MULT_CSAND']['value'] == 1.0
    assert cfg_tmpl['KH_MULT_CSAND']['value'] == '<KH_MULT_CSAND>'


def test_to_json_troll2():
    """Test the output for the JSON files, both templated and normal for
    rms section.
    """

    cfg = config.ConfigParserFMU()

    assert isinstance(cfg, config.ConfigParserFMU)

    cfg.parse(TFILE2)
    rootn = 'troll2_json'

    cfg.to_json(rootname=rootn, destination=fmux.tmpdir,
                template=fmux.tmpdir, tool='rms')

    with open(os.path.join(fmux.tmpdir, rootn + '.json'), 'r') as myfile:
        cfg_json = json.load(myfile)

    assert cfg_json['KH_MULT_CSAND']['value'] == str(1.0)


def test_ipl_troll2():
    """Test basic behaviour"""

    cfg = config.ConfigParserFMU()

    assert isinstance(cfg, config.ConfigParserFMU)

    cfg.parse(TFILE2)

    cfg.show()
    cfg.show(style='json')

    # export the config as a global variables IPL
    logger.info('Test dir is %s', fmux.tmpdir)
    cfg.to_ipl(destination=os.path.join(fmux.tmpdir),
               template=os.path.join(fmux.tmpdir))


# def test_basic_reek():
#     """Test basic behaviour, Reek setup"""

#     cfg = config.ConfigParserFMU()

#     assert isinstance(cfg, config.ConfigParserFMU)

#     cfg.parse(RFILE1)

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
#     fmurun.main(['--input', RFILE1, '--mode', 'ipl'])  # noqa


# def test_command_make_yamls():
#     """Make IPL both global_variables_rms.yml and global_variables_tmpl.yml,
#     Reek.
#     """

#     fmurun.main(['--input', RFILE1, '--mode', 'yaml', --tool, 'rms'])  # noqa
