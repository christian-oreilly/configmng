from collections.abc import Mapping
from copy import deepcopy

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def yn_choice(message, default='y'):
    choices = 'Y[yes]/n[no)/a[abort]' if default.lower() in ('y', 'yes') else 'y[yes]/N[no)/a[abort]'
    choice = input("%s (%s) " % (message, choices))
    values = ('y', 'yes', '') if choices == 'Y/n' else ('y', 'yes')
    if choice.strip().lower() in ('a', 'abort'):
        raise RuntimeError("Execution aborted by the user.")
    return choice.strip().lower() in values


def get_node(dict_obj, path):
    obj_to_return = dict_obj
    for level in path:
        obj_to_return = obj_to_return[level]
    return obj_to_return


# Recursive updates. Default dictionary update is not recursive, which
# cause dict within dict to be simply overwritten rather than merged
def update(d, u):
    for k, v in u.items():
        if k not in d:
            if isinstance(v, Mapping) or hasattr(v, "keys"):
                if isinstance(v, Mapping):
                    d[k] = deepcopy(v)
                else:
                    d[k] = v
            else:
                d[k] = v
        else:
            dv = d.get(k, {})
            if not isinstance(dv, Mapping) and not hasattr(dv, "keys"):
                d[k] = v
            elif isinstance(v, Mapping) or hasattr(v, "keys"):
                d[k] = update(dv, deepcopy(v))
            else:
                d[k] = v
    return d


def eq_mappable(map1, map2):
    if isinstance(map1, Mapping) and isinstance(map2, Mapping):
        if len(map1) != len(map2):
            return False
        for key in map1:
            if key not in map2:
                return False
            if isinstance(map1[key], Mapping) and isinstance(map2[key], Mapping):
                if not eq_mappable(map1[key], map2[key]):
                    return False
            if map1[key] != map2[key]:
                return False
        return True
    return map1 == map2


def join(loader, _, node):
    seq = loader.construct_sequence(node)
    return ''.join([str(i) for i in seq])


def pretty_print(data):
    print(yaml.dump(data, default_flow_style=False, default_style=''))


class ConfigMngLoader(Loader):
    pass


ConfigMngLoader.add_multi_constructor("!join", join)
