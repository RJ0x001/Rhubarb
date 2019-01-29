import argparse
import types
import json
from functools import wraps
import jsonschema


MAPPING_DICT = {}


def check_json_schema(json_schema, params):
    return jsonschema.validate(json_schema, params)


def task_deco(name, json_schema=None):
    def dec(real_func):
        @wraps(real_func)
        def wrapper(*args, **kwargs):
            if json_schema:
                check_json_schema(kwargs, json_schema)
            return real_func(*args, **kwargs)
        MAPPING_DICT[name] = wrapper
        return wrapper
    return dec


class BaseTask(object):
    pass


def get_task(task):
    for cls in list(BaseTask.__subclasses__()):
        if task in cls.__dict__.values():
            return cls
    try:
        return MAPPING_DICT[task]
    except KeyError:
        raise KeyError('Wrong task name')


def run_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--params')
    parser.add_argument('t_type')
    args = parser.parse_args()
    json_params = json.loads(args.params)
    t = get_task(args.t_type)
    if isinstance(t, types.FunctionType):
        return t(**json_params)
    else:
        if hasattr(t, 'run') and callable(t.run):
            if hasattr(t, 'json_schema'):
                check_json_schema(json_params, t.json_schema)
            return t().run(**json_params)
        else:
            raise ValueError('Child class should have run() method')

