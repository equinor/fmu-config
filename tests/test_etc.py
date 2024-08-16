"""Testing the classes/functions in in the etc module."""

import os

import pytest
import yaml
from yaml.constructor import ConstructorError

from fmu.config import etc, utilities as util

fmux = etc.Interaction()
logger = fmux.basiclogger(__name__)

logger.info("Running tests...")


DROGON = "tests/data/yml/drogon/input/global_master_config.yml"

# always this statement
if not fmux.testsetup():
    raise SystemExit


def test_info_logger_plain():
    """Test basic logger behaviour plain, will capture output to stdin"""
    logger.info("This is a test")
    # no assert is intended


@pytest.fixture(name="mylogger")
def fixture_mylogger():
    """Add logger"""
    # need to do it like this...
    return fmux.basiclogger(__name__, level="DEBUG")


def test_info_logger(mylogger, caplog):
    """Test basic logger behaviour, will capture output to stdin"""

    mylogger.info("This is a test")
    assert "This is a test" in caplog.text

    logger.warning("This is a warning")
    assert "This is a warning" in caplog.text


def test_more_logging_tests(caplog):
    """Testing on the logging levels, see that ENV variable will override
    the basiclogger setting.
    """

    os.environ["FMU_LOGGING_LEVEL"] = "INFO"

    fmumore = etc.Interaction()  # another instance
    locallogger = fmumore.basiclogger(__name__, level="WARNING")
    locallogger.debug("Display debug")
    assert caplog.text == ""  # shall be empty
    locallogger.info("Display info")
    assert "info" in caplog.text  # INFO shall be shown, overrided by ENV!
    locallogger.warning("Display warning")
    assert "warning" in caplog.text
    locallogger.critical("Display critical")
    assert "critical" in caplog.text


def test_timer(capsys):
    """Test the timer function"""

    time1 = fmux.timer()
    for inum in range(100000):
        inum += 1

    fmux.echo(f"Used time was {fmux.timer(time1)}")
    captured = capsys.readouterr()
    assert "Used time was" in captured[0]
    # repeat to see on screen
    fmux.echo("")
    fmux.warn(f"Used time was {fmux.timer(time1)}")


def test_print_fmu_header():
    """Test writing an app header."""
    fmux.print_fmu_header("MYAPP", "0.99", info="Beta release (be careful)")


def test_user_msg():
    """Testing user messages"""

    fmux.echo("")
    fmux.echo("This is a message")
    fmux.warn("This is a warning")
    fmux.warning("This is also a warning")
    fmux.error("This is an error")
    fmux.critical("This is a critical error", sysexit=False)


def test_load_input_extended_yaml():
    """Test loading YAML will extended "fmu" option."""
    cfg = util.yaml_load(DROGON, loader="fmu")

    assert cfg["revision"] == "21.x.0.dev"
    assert (
        cfg["masterdata"]["smda"]["coordinate_system"]["uuid"]
        == "ad214d85-dac7-19da-e053-c918a4889309"
    )


def test_load_input_extended_yaml_shallfail():
    """Test loading non-standard YAML which shall fail when allow_extended is False."""
    with pytest.raises(ConstructorError, match=r"!include"):
        _ = util.yaml_load(DROGON, loader="standard")


def test_load_yaml_compare(tmp_path):
    """Test loading YAML and compare results with/without allow_extended."""

    cfg = util.yaml_load(DROGON, loader="fmu")

    yfile = tmp_path / "drogon.yml"
    with open(yfile, "w", encoding="utf-8") as stream:
        yaml.dump(cfg, stream, allow_unicode=True)

    # read a standard YAML file both with normal and extended option
    cfg1 = util.yaml_load(yfile, loader="fmu")
    cfg2 = util.yaml_load(yfile, loader="standard")

    assert cfg1 == cfg2
