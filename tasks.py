# -*- coding: UTF-8 -*-

import argparse
import types
import json
from functools import wraps
import jsonschema
import multiprocessing
from flask import Flask, request, render_template


MAPPING_DICT = {}


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Flask main page.
    Taking task from users
    """
    if request.method == 'POST':

        user_task = str(request.form.get('task'))
        json_user_task = json.loads(user_task)

        q = multiprocessing.Queue()

        try:

            q.put(json_user_task)

        except TypeError:
            print json.dumps({"status": "ERROR",
                              "error_code": 901,
                              "error_msg": "wrong task name"})
        except KeyError:
            print json.dumps({"status": "ERROR",
                              "error_code": 902,
                              "error_msg": "wrong task params"})
        worker(q)
    return render_template('home.html')


def worker(queue):
    json_user_task = queue.get()
    p = multiprocessing.Process(target=get_task, args=(json_user_task['task_name'], json_user_task['params']))
    p.start()


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


def get_task(task, json_params):
    try:
        if task not in MAPPING_DICT.keys():
            for cls in list(BaseTask.__subclasses__()):
                if task in cls.__dict__.values():
                    t = cls
        else:
            t = MAPPING_DICT[task]
        if isinstance(t, types.FunctionType):
            return t(**json_params)
        else:
            if hasattr(t, 'run') and callable(t.run):
                if hasattr(t, 'json_schema'):
                    check_json_schema(json_params, t.json_schema)
                return t().run(**json_params)
            else:
                raise ValueError('Child class should have run() method')
    except UnboundLocalError:
        raise ('Wrong task name')


def run_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--params')
    parser.add_argument('t_type')
    args = parser.parse_args()

    if args.t_type == 'runserver':
        app.run()

    json_params = json.loads(args.params)
    return get_task(args.t_type, json_params)


