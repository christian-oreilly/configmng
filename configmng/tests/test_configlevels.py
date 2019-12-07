from configmng import ConfigLevel


def test_add_config():

    config_level = ConfigLevel(name="test")
    config_level.add_config({"level1": {"level2": "value1"}}, name=None, insertion_node=None, schemas=None)
    assert(isinstance(config_level.get_configs(), list))
    assert(config_level.config["level1"]["level2"] == "value1")
    config_level.add_config({"level3": "value1"}, name="inserted_config", insertion_node=["level1", "level2"])
    assert(config_level.config["level1"]["level2"]["level3"] == "value1")
    assert(len(config_level.get_configs()) == 2)
    assert(config_level.get_a_config("inserted_config")["level3"] == "value1")


def test_to_json():
    config_level = ConfigLevel(name="test")
    config_level.add_config({"level1": {"level2": "value1"}}, name=None, insertion_node=None, schemas=None)
    config_level.to_json()
