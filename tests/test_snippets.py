# -*- coding: utf-8 -*-
"""Testing config parsing of very small principal YAML snippets, e.g. for debugging"""

from fmu.config import ConfigParserFMU

fmux = config.etc.Interaction()
logger = fmux.basiclogger(__name__)

# always this statement
if not fmux.testsetup():
    raise SystemExit()

S01 = "yaml/snippets/s01.yml"


def test_dict_with_scalar_and_lists():
    """s01"""

    cfg = ConfigParserFMU()
    cfg.parse(S01)
