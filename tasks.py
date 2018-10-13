import argparse
import json
import jsonschema
from functools import wraps




def task(name, json_schema):
    def dec(func):
        @wraps(func)
        def wrapper():
            parser = argparse.ArgumentParser()
            parser.add_argument('--params', type=str)
            args = parser.parse_args()
            d = vars(args)  # dict
            json_params = json.loads(args.params)
            jsonschema.validate(json_params, json_schema)
            try:
                return func(**json_params)
            except TypeError:
                print 'Error! Incorrect values'

        return wrapper
    return dec

'''
class BaseTask(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--params', '--foo')
        self.args = self.parser.parse_args()
        self.params = self.args.params
        self.json_params = json.loads(self.args.params)


class Multiply(BaseTask):

    def run(self, operands):
        return reduce(lambda x, y: x * y, operands)


if __name__ == '__main__':
    tasks.run_cli()
'''