from collections import OrderedDict
import typing
from typing import List
import json
from pathlib import Path

from .configlevel import ConfigLevel
from .config import Config, ConfigArg


class ConfigMng:
    """
     ConfigMng allows for different layers of configuration files. By default,
     the following levels are considered:

      - Application level
      - Project level
      - User level
      - Instance level

     Configuration files at the application levels are considered to be static,
     meaning that ConfigMng will not modify them. These, for example, can be a
     configuration file of a library using ConfigMng with default values.

     The project level regroup configuration specific to a particular project,
     regardless of users or applications.

     The user level should contain information specific to a given user, such as
     name, emails, account ID, etc.

     Instance levels group all the configuration information not related to any
     of the other levels and specific to a given use of the ConfigMng object
     (e.g., a specific data processing task or analysis).

     These different levels are transversals. For example, a given project
     can involve different users (with specific configurations such as account
     information) and use different applications. Similarly, the same users
     and applications can be used in different projects. Therefore, there is no
     hierarchy between these levels, although they are applied in order during
     the their merging in a unified configuration file. The merging order
     is important because fields defined in more than one configuration file
     will by design be silently overshaddowed by the last configuration file
     to be merged. The name of the levels and their order can be queried using
     ConfigMng.level_order and be changed by using ConfigMng.level_order = order.

     There can be more than one configuration file within a level. These are
     applied in order they have been added to the ConfigMng object
     (calling ConfigMng.add_config(). Order of cofiguration files within a level
     can be modified using ConfigMng.reorder_a_level(level_name, order).

     When specific use cases requires it, a new level of configuration files can be
     added using ConfigMng.add_level(level_name). This level will be inserted right
     before the user level.
    """
    def __init__(self,
                 instance_configs: typing.Optional[ConfigArg] = None,
                 user_configs: typing.Optional[ConfigArg] = None,
                 project_configs: typing.Optional[ConfigArg] = None,
                 application_configs: typing.Optional[ConfigArg] = None,
                 interactive: bool = True):
        """
        :param instance_configs: Configuration files for the 'instance' level.
        :param user_configs: Configuration for the 'user' level.
        :param project_configs: Configuration for the 'project' level.
        :param application_configs: Configuration for the 'application' level.
        :param interactive: If true, validation errors will prompt users for information to correct
                            the error or the missing fields. If false, validation errors raises exceptions.
        """
        self.interactive = interactive

        self._levels: typing.Mapping[str, ConfigLevel] = OrderedDict([
            ("application", ConfigLevel("application", interactive=False, read_only=True)),
            ("project", ConfigLevel("project", interactive=self.interactive)),
            ("user", ConfigLevel("user", interactive=self.interactive)),
            ("instance", ConfigLevel("instance", interactive=self.interactive))])

        #if merged_schemas is None:
        #    self._merged_schemas: list = []
        #else:
        #    self._merged_schemas: list = merged_schemas

        self.set_level_configs(instance_configs, "instance", update=False)
        self.set_level_configs(user_configs, "user", update=False)
        self.set_level_configs(project_configs, "project", update=False)
        self.set_level_configs(application_configs, "application", update=False)

        self._update_merged_config()

    def set_level_schemas(self, level_name: str, schemas: List[str], update=True):
        """
         Reset the schemas for a given ConfigLevel.

        :param level_name: Name of the level which should use the 'schemas'.
        :param schemas: List of schemas to be used at level 'level_name.
        :param update: If true, the merged config will be updated.
        :return: None
        """
        self._levels[level_name].set_schemas(schemas)
        if update:
            self._update_merged_config()

    def set_level_configs(self, configs, level_name: str = "instance", update=True):
        if configs is not None:
            if not isinstance(configs, list):
                configs = [configs]
            for config in configs:
                self.add_config(config, level_name, update=False)
        if update:
            self._update_merged_config()

    def add_schema(self, schema, level_name="instance"):
        """
        """
        #if level_name == "merged":
        #    self._merged_schemas.append(schema)
        #else:
        self._levels[level_name].add_schema(schema)

    def add_config(self, config, level_name="instance", config_name=None, insertion_node=None,
                   schemas=None, update=True):

        self._levels[level_name].add_config(config, config_name, insertion_node, schemas)
        if update:
            self._update_merged_config()

    def add_level(self, new_level_name, interactive=None):
        if interactive is None:
            interactive = self.interactive

        new_levels = OrderedDict()
        for name, level in self._levels.items():
            if name == "user":
                new_levels[new_level_name] = ConfigLevel(new_level_name, interactive=interactive)
            new_levels[name] = level
        self._levels = new_levels

    def to_json(self):
        return {"config_paths": [config.path for config in self.get_configs()],
                "merged_config": self._merged_config.to_json()}

    def __repr__(self):
        return str(self.to_json())

    def __str__(self):
        return json.dumps(self.to_json(), indent=4, sort_keys=True)

    @property
    def level_order(self):
        return tuple(self._levels.keys())

    @level_order.setter
    def level_order(self, order):

        keys = list(self._levels.keys())
        err_msg = "order must have the same levels as already contained in the " + \
                  "object, only with a different order. Order received " + \
                  "{}, current order {}.".format(order, keys)
        if len(keys) != len(order):
            raise ValueError(err_msg)
        for key in keys:
            if key not in order:
                raise ValueError(err_msg)

        self._levels = OrderedDict([(key, self._levels[key]) for key in order])

    def reorder_a_level(self, level_name: str, order: typing.Iterable):
        self._levels[level_name].reorder(order)

    @property
    def config(self):
        return self._merged_config

    def get_configs(self):
        configs = []
        for level in self._levels.values():
            configs.extend(level.get_configs())
        return configs

    # def get_schemas(self):
    #    schemas = []
    #    for level in self._levels.values():
    #        schemas.extend(level.get_schemas())
    #    return schemas

    def _update_merged_config(self, validate=True):
        configs = self.get_configs()
        if len(configs) == 0:
            self._merged_config = Config()
            return

        if len(configs) == 1:
            self._merged_config = configs[0]
        else:
            self._merged_config = Config()
            for level in self._levels.values():
                self._merged_config += level.config

        #self._merged_config.add_schemas(self._merged_schemas)
        if validate:
            self.validate(interactive=self.interactive)

    def validate(self, raise_exception=True, interactive=None):
        if interactive is None:
            interactive = self.interactive
        self._merged_config.validate(raise_exception, interactive)

    def save_config(self, path=None):
        self._merged_config.save(path)

    def make_serializable(self):
        self._merged_config._tmp_file = None
        for level in self._levels.values():
            level.make_serializable()
