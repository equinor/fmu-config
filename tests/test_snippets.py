# -*- coding: utf-8 -*-
"""Testing config parsing of very small principal YAML snippets, e.g. for debugging"""
import fmu.config as fcfg

from fmu.config import utilities as ut

fmux = fcfg.etc.Interaction()
logger = fmux.basiclogger(__name__)

# always this statement
if not fmux.testsetup():
    raise SystemExit()


def test_dict_with_scalar_and_lists1(tmp_path):
    """s01, testing small inline snippets"""

    inp = b"""
    global:
        ADICT_WITH_SCALAR_OR_LISTS:
            1: ascalar
            3: [item1, item2, 33, 44.0]
    """

    target = tmp_path / "generic.yml"
    with open(target, "wb") as out:
        out.write(inp)

    cfg = fcfg.ConfigParserFMU()
    cfg.parse(target)

    assert cfg._config["global"]["ADICT_WITH_SCALAR_OR_LISTS"][1] == "ascalar"
    assert cfg._config["global"]["ADICT_WITH_SCALAR_OR_LISTS"][3][2] == 33


def test_dict_with_scalar_and_lists2(tmp_path):
    """s02"""

    inp = b"""
    global:
        ACOMPLICATED:
            1: ascalar
            2: number ~ <>
            3: [2, 33, [12, 13, 14], manana]
    """

    target = tmp_path / "generic.yml"
    with open(target, "wb") as out:
        out.write(inp)

    cfg = fcfg.ConfigParserFMU()
    cfg.parse(target)

    assert cfg._config["global"]["ACOMPLICATED"][1] == "ascalar"
    assert cfg._config["global"]["ACOMPLICATED"][3][0] == 2
    assert cfg._config["global"]["ACOMPLICATED"][3][3] == "manana"


def test_process_value1(tmp_path):
    """s03"""

    inp = b"""
    global:
        WELLCONCEPT: REV1_A15 ~ <WELL_CONS>
    """

    target = tmp_path / "generic.yml"
    with open(target, "wb") as out:
        out.write(inp)

    cfg = fcfg.ConfigParserFMU()
    cfg.parse(target)

    outfolder = tmp_path
    out = outfolder.resolve()

    cfg.to_yaml(rootname="s03", destination=out, template=out)

    actual = ut.yaml_load(outfolder / "s03.yml")

    assert actual["global"]["WELLCONCEPT"] == "REV1_A15"

    tmpl = ut.yaml_load(outfolder / "s03.yml.tmpl")

    assert tmpl["global"]["WELLCONCEPT"] == "<WELL_CONS>"


def test_process_value2(tmp_path):
    """s04"""

    inp = b"""
    global:
        WHATEVER: &onx ONX ~ <ONX>
        WHATEVER2: *onx
        NUMBER1: 2.0 ~ <NUM1>
    """

    target = tmp_path / "generic.yml"
    with open(target, "wb") as out:
        out.write(inp)

    cfg = fcfg.ConfigParserFMU()
    cfg.parse(target)

    out = tmp_path.resolve()

    cfg.to_yaml(rootname="s04", destination=out, template=out)

    actual = ut.yaml_load(tmp_path / "s04.yml")
    print(actual)

    assert actual["global"]["WHATEVER"] == "ONX"
    assert actual["global"]["NUMBER1"] == 2.0

    tmpl = ut.yaml_load(tmp_path / "s04.yml.tmpl")
    print(tmpl)

    assert tmpl["global"]["WHATEVER"] == "<ONX>"
