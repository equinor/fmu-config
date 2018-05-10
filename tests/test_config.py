import fmu_config
from xtgeo.common import XTGeoDialog

tfile1 = 'tests/data/yaml/troll1/global_variables.yaml'
rfile1 = 'tests/data/yaml/reek1/global_variables.yaml'

xxx = XTGeoDialog()
logger = xxx.basiclogger(__name__)
testdir = xxx.testsetup()


def test_basic_troll():
    """Test basic behaviour"""

    cfg = fmu_config.ConfigParser()

    assert isinstance(cfg, fmu_config.ConfigParser)

    cfg.parse(tfile1)

    cfg.show()

    assert len(cfg.config['horizons']) == 6

    # export the config as a global variables IPL
    cfg.to_ipl(testdir + '/myfile.ipl')


def test_basic_reek():
    """Test basic behaviour, Reek setup"""

    cfg = fmu_config.ConfigParser()

    assert isinstance(cfg, fmu_config.ConfigParser)

    cfg.parse(rfile1)

    cfg.show()

    # will write the eclipse files
    cfg.to_eclipse()
    cfg.to_ipl()

    # assert len(cfg.config['horizons']) == 6

    # # export the config as a global variables IPL
    # cfg.to_ipl('myfile')
