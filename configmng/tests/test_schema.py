from configmng import Schema
from pathlib import Path
import pytest
from io import StringIO
from copy import deepcopy



import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def test__init__():
    schema_path = Path(__file__).parent / "test_artifacts" / "test_config_schema.yaml"

    schema1 = Schema(str(schema_path))
    schema2 = Schema(schema_path)
    assert(schema1 == schema2)
    schema3 = Schema([schema1, Schema(schema1.load(normalize=False))])
    schema1.set(["name"], "")
    schema3.set(["name"], "")
    assert(schema1 == schema3)

    with pytest.raises(FileNotFoundError):
        Schema("/some/unexisting/path.yaml")

    with pytest.raises(TypeError):
        Schema(2)


def test_normalize():

    schema_path = Path(__file__).parent / "test_artifacts" / "test_config_schema.yaml"
    schema1 = Schema(schema_path)
    schema1_data = schema1.load()

    schema2 = Schema(schema_path)
    schema2.insertion_node = ("root_level",)
    schema2_data1 = schema2.load(normalize=True)

    schema2.normalize()
    schema2_data2 = schema2.load(normalize=False)

    assert("level1" in schema1_data["mapping"])
    print(schema2_data1)
    assert("level1" in schema2_data1["mapping"]["root_level"]["mapping"])
    assert("level1" in schema2_data2["mapping"]["root_level"]["mapping"])


def test_merging():

    schema_path = Path(__file__).parent / "test_artifacts" / "test_config_schema.yaml"
    schema1 = Schema(schema_path)
    schema2 = Schema(StringIO("""
                                 name: schema1
                                 type: map
                                 mapping:
                                   level1:
                                     required: False
                                     type: map
                                     mapping:
                                       level2a:
                                         type: seq
                                         sequence:
                                           - type: str
                                       level2c:
                                         type: seq
                                         sequence:
                                           - type: str
                              """))

    merged_schema = Schema.merge_schemas([schema1, schema2])
    merged_schema_data = merged_schema.load()
    assert("level2a" in merged_schema_data["mapping"]["level1"]["mapping"])
    assert("level2b" in merged_schema_data["mapping"]["level1"]["mapping"])
    assert("level2c" in merged_schema_data["mapping"]["level1"]["mapping"])
