# -*- coding: utf-8 -*-
"""Testing fmu-config tools."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import fmu.config as config
from fmu.config import utilities as utils

# import fmu.config.fmuconfigrunner as fmurun

fmux = config.etc.Interaction()
logger = fmux.basiclogger(__name__)

REEK = "tests/data/yaml/reek1/global_variables.yml"

# always this statement
if not fmux.testsetup():
    raise SystemExit()


def test_basic_tools():
    """Test basic tools behaviour"""

    cfg = utils.yaml_load(REEK)

    assert cfg["global"]["name"] == "Reek"
