from pathlib import Path

from configmng import Config, Schema


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


def test_merging():

    insertion_node = ["level1", "level2"]
    config1 = Config({"level1": {"level2": "value1"}})
    assert(config1["level1"]["level2"] == "value1")
    config2 = Config({"level3": "value1"}, insertion_node=insertion_node)
    assert(config2.insertion_node == insertion_node)
    merged_config = config1 + config2
    assert(merged_config["level1"]["level2"]["level3"] == "value1")
    assert("level3" not in config1["level1"]["level2"])
    config1 += config2
    assert(config1["level1"]["level2"]["level3"] == "value1")

    # Checking merging of schema files
    path_schema = Path(__file__).parent / "test_artifacts" / "test_config_schema.yaml"
    path_schema2 = Path(__file__).parent / "test_artifacts" / "test_config_schema2.yaml"
    config1 = Config({"level1": {"level2a": ["value1a"]}}, schemas=path_schema)
    assert(len(config1.schemas) == 1)
    config2 = Config({"level1": {"level2b": ["value1b"]}}, schemas=path_schema)
    merged_config = config1 + config2
    assert(len(merged_config.schemas) == 1)
    config3 = Config({"level1": {"level2b": ["value1b"]}}, schemas=path_schema2)
    merged_config = config1 + config3
    assert(len(merged_config.schemas) == 2)


def test_to_json():
    path = Path(__file__).parent/ "test_artifacts" / "test_config.yaml"
    config = Config(path)
    config.to_json()


def test_add_dublon_schema():

    config = Config()
    path_schema = Path(__file__).parent / "test_artifacts" / "test_config_schema.yaml"
    config.add_schemas(path_schema)
    assert(len(config.schemas) == 1)
    config.add_schemas(path_schema)
    assert(len(config.schemas) == 1)
    config.add_schemas(Schema(""))
    assert(len(config.schemas) == 2)