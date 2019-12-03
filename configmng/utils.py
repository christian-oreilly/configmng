from collections.abc import Mapping
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
        dv = d.get(k, {})
        if not isinstance(dv, Mapping) and not hasattr(dv, "keys"):
            d[k] = v
        elif isinstance(v, Mapping) or hasattr(v, "keys"):
            d[k] = update(dv, v)
        else:
            d[k] = v
    return d


def join(loader, _, node):
    seq = loader.construct_sequence(node)
    return ''.join([str(i) for i in seq])


class ConfigMngLoader(Loader):
    pass


ConfigMngLoader.add_multi_constructor("!join", join)
