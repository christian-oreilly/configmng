from collections import OrderedDict
import typing
import json

from .config import Config, ConfigArg
from .schema import Schema, SchemaArg


class ConfigLevel:

    def __init__(self, name, configs=(), interactive=False):
        self.name = name
        self._configs = OrderedDict()
        self._level_schemas = []
        self.interactive = interactive

        if isinstance(configs, OrderedDict):
            for config_name, config in configs.items():
                self.add_config(config, config_name)
        elif isinstance(configs, list):
            for config in configs:
                self.add_config(config)
        elif isinstance(configs, Config):
            self.add_config(configs)

    def to_json(self):
        return {"config_paths": [str(config.path) for config in self.get_configs()],
                "merged_config": self.config.store,
                "schemas": [schema.to_json() for schema in self._level_schemas]}

    def __repr__(self):
        return str(self.to_json())

    def __str__(self):
        return json.dumps(self.to_json(), indent=4, sort_keys=True)

    def reorder(self, order):
        keys = list(self._configs.keys())
        if len(keys) != len(order):
            raise ValueError("order must contain the same configuration names as "
                             "already contained in the object, only with a different order."
                             "Order received {}, current order {}.".format(order, keys))
        for key in keys:
            if key not in order:
                raise ValueError("order must contain the same configuration names as "
                                 "already contained in the object, only with a different order."
                                 "Order received {}, current order {}.".format(order, keys))
        self._configs = OrderedDict([(key, self._configs[key]) for key in order])

    def add_config(self,
                   config: ConfigArg,
                   name: typing.Optional[str] = None,
                   insertion_node: typing.Optional[typing.Iterable] = None,
                   schemas: SchemaArg = None):

        if not isinstance(config, Config):
            config = Config(config=config, schemas=schemas, insertion_node=insertion_node)

        if name is None:
            no = len(self._configs)
            while "conf_{}".format(no) in self._configs:
                no += 1
            name = "conf_{}".format(no)

        self._configs[name] = config

    def set_schemas(self, schemas):
        self._level_schemas = schemas
        self.validate()

    def add_schema(self, schema):
        if not isinstance(schema, Schema):
            schema = Schema(schema)
        self._level_schemas.append(schema)
        self.validate()

    def validate(self, raise_exception=True, interactive=None):
        if interactive is None:
            interactive = self.interactive
        config = self.config
        config.save()
        config.validate(raise_exception=raise_exception, interactive=interactive)

    def get_configs(self, as_dict=False):
        if as_dict:
            return self._configs
        return list(self._configs.values())

    def get_a_config(self, name: str):
        return self._configs[name]

    def make_serializable(self):
        for config in self._configs.values():
            config._tmp_file = None

    @property
    def config(self):
        return_config = Config(delete_tmp_files=True)
        for config in self._configs.values():
            return_config = return_config + config
        return_config.delete_tmp_files = True
        return_config.add_schemas(self._level_schemas)
        return return_config
