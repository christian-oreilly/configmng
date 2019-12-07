import typing

if typing.TYPE_CHECKING:
    from .config import Config

class ConfigProv:

    def __init__(self):
        self._mergings: typing.List[Config] = []

    def merging(self, configs : "Config"):
        self._mergings.append(configs)

    def propagate_changes(self, value, key, path):
        for merging in self._mergings:
            for config in merging:
                config.set_value_at_path(value, key, path, silent_fail=True, only_if_key_in=True)
