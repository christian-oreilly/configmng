from collections import OrderedDict
import typing
import json

from .configlevel import ConfigLevel
from .config import Config


# insertion node
# create output config
# validation of the output config
# add_config(config, level, name, insertion_node, schema)
# get_a_config(name)
# get_configs() return list(config)
# .config (accessor for the merged config)

class ConfigMng:
    """
     ConfigMng allows for different layers of configuration files. By default,
     the following levels are considered:

      - Application level
      - Project level
      - User level
      - Instance level

     Application levels are considered to be static configurations which will
     not be modified by ConfigMng. These, for example, can be a configuration
     file of a library using ConfigMng with default values.

     The project level regroup configuration specific to a particular project,
     regardless of users or applications.

     The user level should contain information specific to a given user, such as
     name, emails, account ID, etc.

     Instance levels group all the configuration information not related to any
     of the other levels and specific to a given use of th

     These different levels are transversals. For example, a given project
     can involve different users (with specific configurations such as account
     information) and uses different applications. Similarly, the same users
     and applications can be used in different projects. Therefore, there is no
     hierarchy between these levels, although they are applied in order during
     the merging.



     The actual configuration is the result of merging configuration files,
     in this order. The order of merging is important, as fields defined
     in more than one configuration file will be overshaddowed by the last
     configuration file. The name of the levels and their order is defined
     by the list ConfigMng.levels and can be altered by modifying this list.

     There can be more than one configuration file within a level. These are
     applied in order they have been added to the ConfigMng object
     (calling ConfigMng.add_config()
    """
    def __init__(self,
                 instance_configs: typing.Optional[list] = None,
                 user_config_path: typing.Optional[str] = None,
                 project_config_path: typing.Optional[str] = None,
                 application_config_path: typing.Optional[str] = None,
                 merged_schemas: typing.Optional[list] = None,
                 interactive: bool = False):

        self.interactive = interactive
        self._merged_schemas = merged_schemas
        self.set_configs(instance_configs, user_config_path,
                         project_config_path, application_config_path)

    def set_configs(self,
                 instance_configs: typing.Optional[list] = None,
                 user_config_path: typing.Optional[str] = None,
                 project_config_path: typing.Optional[str] = None,
                 application_config_path: typing.Optional[str] = None):
        self._levels = OrderedDict([("application", ConfigLevel("application", interactive=self.interactive)),
                                    ("project", ConfigLevel("project", interactive=self.interactive)),
                                    ("user", ConfigLevel("user", interactive=self.interactive)),
                                    ("instance", ConfigLevel("instance", interactive=self.interactive))])

        if application_config_path is not None:
            self.add_config(application_config_path, "application", update=False)
        if project_config_path is not None:
            self.add_config(project_config_path, "project", update=False)
        if user_config_path is not None:
            self.add_config(user_config_path, "user", update=False)
        if instance_configs is not None:
            if not isinstance(instance_configs, list):
                instance_configs = [instance_configs]
            for config in instance_configs:
                self.add_config(config, "instance", update=False)

        self._update_merged_config()

    def set_level_schemas(self,
                          instance_schemas: typing.Optional[list] = None,
                          user_schemas: typing.Optional[list] = None,
                          project_schemas: typing.Optional[list] = None,
                          application_schemas: typing.Optional[list] = None):

        if application_schemas is not None:
            self._levels["application"].set_schemas(application_schemas)
        if project_schemas is not None:
            self._levels["project"].set_schemas(project_schemas)
        if user_schemas is not None:
            self._levels["user"].set_schemas(user_schemas)
        if instance_schemas is not None:
            self._levels["instance"].set_schemas(instance_schemas)

        self._update_merged_config()

    def add_schema_to_level(self, level, schema):
        self._levels[level].add_schema(schema)

    def to_json(self):
        return {"config_paths": [config.path for config in self.get_configs()],
                "merged_config": self._merged_config.to_json()}

    def __repr__(self):
        return str(self.to_json())

    def __str__(self):
        return json.dumps(self.to_json(), indent=4, sort_keys=True)

    @property
    def config(self):
        return self._merged_config

    def get_configs(self):
        configs = []
        for level in self._levels.values():
            configs.extend(level.get_configs())
        return configs

    def _update_merged_config(self, validate=True):
        configs = self.get_configs()
        if len(configs) == 0:
            self._merged_config = Config()
            return

        if len(configs) == 1:
            self._merged_config = configs[0]
        else:
            self._merged_config = Config()
            for config in configs:
                self._merged_config.update(config)

        if validate:
            self.validate(interactive=self.interactive)

    def validate(self, raise_exception=True, interactive=None):
        if interactive is None:
            interactive = self.interactive
        self._merged_config.validate(raise_exception, interactive)

    def add_config(self, config, level="instance", name=None, insertion_node=None,
                   schemas=None, update=True):

        self._levels[level].add_config(config, name, insertion_node, schemas)
        if update:
            self._update_merged_config()

    def save(self, path=None):
        self._merged_config.save(path)

    def make_serializable(self):
        self._merged_config._tmp_file = None
        for level in self._levels.values():
            level.make_serializable()
