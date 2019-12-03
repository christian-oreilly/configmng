from collections import OrderedDict

from .config import Config
from .schema import Schema


class ConfigLevel:

    def __init__(self, name, configs=(), interactive=False):
        self.name = name
        self._configs = OrderedDict()
        self._insertion_nodes = OrderedDict()
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
        self._insertion_nodes = OrderedDict([(key, self._insertion_nodes[key]) for key in order])

    def add_config(self, config, name=None, insertion_node=None, schemas=None):
        if not isinstance(config, Config):
            config = Config(config=config, schemas=schemas)

        if name is None:
            no = len(self._configs)
            while "conf_{}".format(no) in self._configs:
                no += 1
            name = "conf_{}".format(no)

        if insertion_node is None:
            insertion_node = []

        config.add_schemas(self._level_schemas)
        config.values()
        self._configs[name] = config
        self._insertion_nodes[name] = insertion_node

    def set_schemas(self, schemas):
        for config in self._configs.values():
            config.set_schemas(schemas)

        self._level_schemas = schemas
        self.validate()

    def add_schema(self, schema):
        if not isinstance(schema, Schema):
            schema = Schema(schema)
        for config in self._configs.values():
            config.add_schemas([schema])
        self._level_schemas.append(schema)
        self.validate()

    def validate(self, raise_exception=True, interactive=None):
        if interactive is None:
            interactive = self.interactive
        for config in self._configs.values():
            config.validate(raise_exception, interactive)

    def get_configs(self, as_dict=False):
        if as_dict:
            return self._configs
        return list(self._configs.values())

    def get_a_config(self, name: str):
        return self._configs[name]

    def get_a_config_insertion_node(self, name: str):
        return self._insertion_nodes[name]

    def change_insertion_node(self, name: str, insertion_node: list):
        self._insertion_nodes[name] = insertion_node

    def make_serializable(self):
        for config in self._configs.values():
            config._tmp_file = None
