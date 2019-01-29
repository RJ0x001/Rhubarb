import argparse
import types
import json
from functools import wraps

MAPPING_DICT = {}

def task_deco(name):
    def dec(real_func):
        @wraps(real_func)
        def wrapper(*args, **kwargs):
            result = real_func(*args, **kwargs)
            return result
        MAPPING_DICT[name] = wrapper
        return wrapper
    return dec


class BaseTask(object):
    pass


def get_task(task):
    for name, obj in MAPPING_DICT.items():
        if isinstance(obj, types.FunctionType) and name == task:
            return obj
    for cls in list(BaseTask.__subclasses__()):
        if task in cls.__dict__.values():
            return cls


def run_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--params')
    parser.add_argument('t_type')
    args = parser.parse_args()
    json_params = json.loads(args.params)
    t = get_task(args.t_type)
    if isinstance(t, types.FunctionType):
        return t(**json_params)
    return t().run(**json_params)
