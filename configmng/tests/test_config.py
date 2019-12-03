from pathlib import Path

from configmng import Config


def test__init__():

    path = Path(__file__).parent/ "test_artifacts" / "test_config.yaml"
    # Testing that loading configs speficied as different types do not crash
    config1 = Config(path)
    config2 = Config(str(path))
    assert(config1 == config2)

    config3 = Config(config1)
    assert(config1 == config3)

    config4 = Config({"level1":{"level2a": ["property1", "property2"], "level2b": []}})
    assert(config1 == config4)

    assert("level1" in config4)
    assert("level2a" in config4["level1"])
    assert("property1" in config4["level1"]["level2a"])

    Config()

def test_validate():

    path_conf = Path(__file__).parent / "test_artifacts" / "test_config.yaml"
    path_schema = Path(__file__).parent / "test_artifacts" / "test_config_schema.yaml"
    # Testing that loading configs speficied as different types do not crash
    config1 = Config(config=path_conf, schemas=path_schema)
    config1.validate()