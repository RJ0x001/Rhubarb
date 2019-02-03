import tasks
from time import sleep, time
from random import randint


@tasks.task_deco(name='multiprint',
                 json_schema={'type': 'object',
                              'properties': {
                                  'msg': {'type': 'string'},
                                  'count': {'type': 'integer', 'minimum': 1}
                              },
                              'required': ['msg']})
def multi_print(msg, count=2):
    sleep(randint(3, 9))
    print '\n'.join(msg for _ in xrange(count))


@tasks.task_deco(name='greet')
def greetings(name):
    print 'Hello, ' + name


class Multiply(tasks.BaseTask):
    name = 'mult'
    json_schema = {'type': 'object',
                   'properties': {
                       'operands': {'type': 'array',
                                    'minItems': 1,
                                    'items': {'type': 'number'}}
                   },
                   'required': ['operands']}

    def run(self, operands):
        sleep(randint(3, 9))
        print reduce(lambda x, y: x * y, operands)


class Summa(tasks.BaseTask):
    name = 'sum'

    def run(self, operands):
        print reduce(lambda x, y: x + y, operands)


if __name__ == '__main__':
    print tasks.run_cli()
