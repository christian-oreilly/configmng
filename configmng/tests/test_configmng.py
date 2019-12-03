
from configmng import ConfigMng, Config

def test__init__():
    ConfigMng({"another_field":{"inner1":"property"}})
    ConfigMng(Config({"another_field":{"inner1":"property"}}))
    ConfigMng([{"another_field":{"inner1":"property"}}])


def test_config_update():
    mng = ConfigMng(instance_configs = [{"another_field":{"inner1":"property"}},
                                        {"another_field":{"inner2":"property"}}])
    assert("inner1" in mng.config["another_field"])
    assert("inner2" in mng.config["another_field"])
