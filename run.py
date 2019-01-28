import tasks


@tasks.task_deco(name='multiprint')
def multi_print(msg, count=10):
    return '\n'.join(msg for _ in xrange(count))


@tasks.task_deco(name='greet')
def greetings(name):
    return 'Hello, ' + name


class Multiply(tasks.BaseTask):
    name = 'mult'

    def run(self, operands):
        return reduce(lambda x, y: x * y, operands)


class Summa(tasks.BaseTask):
    name = 'sum'

    def run(self, operands):
        return reduce(lambda x, y: x + y, operands)


if __name__ == '__main__':
    print tasks.run_cli()
