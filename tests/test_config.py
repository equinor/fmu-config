import fmu_config

tfile1 = 'tests/data/yaml/troll1/global_variables.yaml'
rfile1 = 'tests/data/yaml/reek1/global_variables.yaml'


def test_basic_troll():
    """Test basic behaviour"""

    cfg = fmu_config.ConfigParser()

    assert isinstance(cfg, fmu_config.ConfigParser)

    cfg.parse(tfile1)

    cfg.show()

    assert len(cfg.config['horizons']) == 6

    # export the config as a global variables IPL
    cfg.to_ipl('myfile')


def test_basic_reek():
    """Test basic behaviour, Reek setup"""

    cfg = fmu_config.ConfigParser()

    assert isinstance(cfg, fmu_config.ConfigParser)

    cfg.parse(rfile1)

    cfg.show()

    # assert len(cfg.config['horizons']) == 6

    # # export the config as a global variables IPL
    # cfg.to_ipl('myfile')
