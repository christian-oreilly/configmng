
from configmng import ConfigMng, Config


def test__init__():
    ConfigMng({"another_field": {"inner1": "property"}})
    ConfigMng(Config({"another_field": {"inner1": "property"}}))
    ConfigMng([{"another_field": {"inner1": "property"}}])


def test_config_update():
    mng = ConfigMng(instance_configs=[{"another_field": {"inner1": "property"}},
                                      {"another_field": {"inner2": "property"}}])
    assert("inner1" in mng.config["another_field"])
    assert("inner2" in mng.config["another_field"])


def test_config_levels():

    mng1 = ConfigMng(instance_configs={"test_instance": ["value1", "value2"]},
                     user_configs={"test_project": ["value1", "value2"]},
                     project_configs={"test_user": ["value1", "value2"]},
                     application_configs={"test_application": ["value1", "value2"]})

    mng2 = ConfigMng()

    config = {"instance": {"test_instance": ["value1", "value2"]},
              "project": {"test_project": ["value1", "value2"]},
              "user": {"test_user": ["value1", "value2"]},
              "application": {"test_application": ["value1", "value2"]}}

    for level_name, level_config in config.items():
        mng2.set_level_configs(level_config, level_name)

    assert(mng1.config == mng2.config)

    assert("test_instance" in mng1.config)
    assert("test_project" in mng1.config)
    assert("test_user" in mng1.config)
    assert("test_application" in mng1.config)
    assert(len(mng1.config) == 4)
