import yaml
from pathlib import Path
from collections.abc import MutableMapping
from tempfile import NamedTemporaryFile
from warnings import warn
from pykwalify.core import Core
from pykwalify.errors import SchemaError
import json
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from .schema import Schema
from .utils import ConfigMngLoader, update, get_node

def get_schema_node(schema, path, key):
    obj_to_return = schema
    for level in path:
        if "mapping" in obj_to_return:
            obj_to_return = obj_to_return["mapping"][level]
        else:
            raise NotImplementedError
    if "mapping" in obj_to_return:
        return obj_to_return["mapping"][key]
    raise NotImplementedError


class Config(MutableMapping):

    def __init__(self, config=None, schemas=None, temp_dir_node=("paths", "log_dir"),
                 delete_tmp_files=False):
        self.store = dict()
        self._path = None
        self.temp_dir_node = temp_dir_node
        self.delete_tmp_files = delete_tmp_files
        self._tmp_file = None
        self._schemas = []

        if schemas is not None:
            self.set_schemas(schemas)
        if config is not None:
            self.set_config(config, validate=False)
        self.validate()

    def add_schemas(self, schemas):
        def _check_schema_type_(schema_to_check):
            if isinstance(schema_to_check, (str, Path)):
                return Schema(schema_to_check)
            if isinstance(schema_to_check, Schema):
                return schema_to_check
            raise TypeError("schema must be a path to a schema file or a Schema object.")

        if isinstance(schemas, list):
            for schema in schemas:
                self._schemas.append(_check_schema_type_(schema))
        else:
            self._schemas.append(_check_schema_type_(schemas))

    def set_schemas(self, schemas):
        self._schemas = []
        self.add_schemas(schemas)

    def set_config(self, config, schemas=None, validate=True):

        if isinstance(config, (str, Path)):
            self.path = Path(config)
            with Path(config).open('r') as check_stream:
                config = yaml.load(check_stream, Loader=ConfigMngLoader)
                if config is None:
                    return

        elif isinstance(config, Config):
            self.path = config.path
            self.temp_dir_node = config.temp_dir_node
            self.delete_tmp_files = config.delete_tmp_files
            self._tmp_file = config._tmp_file
            self._schemas = config.schemas

        elif isinstance(config, dict):
            self.path = None

        else:
            raise TypeError("Received a configs object of an unrecognized type ({})."
                            .format(type(config)))

        if schemas is not None:
            self.set_schemas(schemas)

        self.update(config, validate=validate)

    @property
    def path(self):
        return self._path

    def get_temporary_path(self):
        dir_ = None
        store = self.store.copy()
        for key in self.temp_dir_node:
            if key in store:
                store = store[key]
            else:
                store = None
                break
        if store is not None:
            assert(isinstance(store, str))
            dir_ = Path(store)
            try:
                dir_.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                warn("The path specified in your configuration file in ['path']['log_dir']" +
                     "(i.e., {}) does not exist and could not be created."
                     .format(self.store["paths"]["log_dir"]))
                dir_ = None

        self._tmp_file = NamedTemporaryFile(mode='w+b', delete=self.delete_tmp_files,
                                            prefix=".tmp_conf_", dir=dir_, suffix=".yaml")
        return Path(self._tmp_file.name)

    @path.setter
    def path(self, path):
        if path is None:
            self._path = self.get_temporary_path()
        elif isinstance(path, str):
            self._path = Path(path)
        elif isinstance(path, Path):
            self._path = path
        else:
            raise TypeError("path must be of type str or Path if it is not None.")
        if not self._path.exists():
            raise FileNotFoundError("The configuration file {} was not found.".format(self._path))

    @property
    def schemas(self):
        return self._schemas

    @schemas.setter
    def schemas(self, schemas):
        self._schemas = schemas

    def validate(self, raise_exception=True, interactive=False):
        if len(self.schemas):
            schema_files = [str(schema.path) for schema in self.schemas]

            try:
                core = Core(source_file=str(self.path),
                            schema_files=schema_files,
                            source_data={})
                core.validate(raise_exception=raise_exception)
            except SchemaError:
                if interactive:
                    for error in core.errors:
                        self.manage_error(core, error)
                    self.validate(raise_exception, interactive)
                else:
                    raise

    def set_value_at_path(self, value, key, path):
        get_node(self.store, path.split("/")[1:])[key]  = value

    def get_schema_key_type(self, schema, key, path):
        return get_schema_node(schema,  path.split("/")[1:], key)["type"]

    def manage_error(self, core, error: SchemaError.SchemaErrorEntry):

        if "Cannot find required key" in error.msg:

            if self.get_schema_key_type(core.schema, error.key, error.path) == "map":
                value = {}
            else:
                value = input("The key {} at path {} of the ".format(error.key, error.path) +
                              "configuration file {} is missing.".format(self.path) +
                              " Please provide a value.")
            self.set_value_at_path(value, error.key, error.path)

        elif "does not match pattern" in error.msg:
            value = input("The value {} for the configuration key {}".format(error.value, error.path) +
                          " is not compatible with the pattern {}.".format(error.pattern) +
                          " required by the schema. Please provide a compatible value.")
            key = error.path.split("/")[-1]
            path = "/".join(error.path.split("/")[:-1])
            self.set_value_at_path(value, key, path)

        elif "is not of type" in error.msg:
            value = input("The type for value {} for the configuration key {}".format(error.value, error.path) +
                          " is not compatible with the type {}.".format(error.scalar_type) +
                          " required by the schema. Please provide a compatible value.")

            key = error.path.split("/")[-1]
            path = "/".join(error.path.split("/")[:-1])
            self.set_value_at_path(value, key, path)
        else:
            raise
        self.save()



    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __contains__(self, item):
        return item in self.store

    def __repr__(self):
        return str(self.to_json())

    def __str__(self):
        return json.dumps(self.to_json(), indent=4, sort_keys=True)

    def to_json(self):
        return {"config_path": self._path,
                "schema_paths": [schema.path for schema in self._schemas],
                "config_dict": self.store}

    def pretty_print(self):
        print(yaml.dump(self.store, default_flow_style=False, default_style=''))

    def update(self, *args, validate=True, **kwargs):
        if not args:
            raise TypeError("descriptor 'update' of 'Config' object "
                            "needs an argument")
        if len(args) > 1:
            raise TypeError('update expected at most 1 arguments, got {}'.format(len(args)))
        if args:
            update(self.store, args[0])
        update(self.store, kwargs)

        if validate:
            self.validate()

    def save(self, path=None):
        if path is not None:
            self.path = path

        with self.path.open("w") as stream:
            yaml.dump(self.store, stream, Dumper=Dumper)
