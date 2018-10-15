import argparse, types, json, jsonschema, random, smtplib
from functools import wraps
from time import sleep
from multiprocessing import Process, Queue, current_process
from config import *
from email.mime.text import MIMEText
from email_test import *


def send_email(email, time_before, time_after, result, name):
    msg = MIMEText('Function %r have completed. Result: %r. Execution time: %s' %
                       (name, result, (time_after - time_before)))
    msg['Subject'] = 'Function %r have completed.' % name
    s = smtplib.SMTP_SSL(smtp_server)
    s.login(me, my_pass)
    msg['From'] = me
    msg['To'] = email
    s.sendmail(me, email, msg.as_string())
    s.quit()


def get_func(task_type):
    for name, obj in list(globals().items()):
        if isinstance(obj, types.FunctionType) and obj.__name__ == task_type:
            true_func_str = name
            f = globals()[true_func_str]
            return f


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        q = Queue()
        user_task = str(request.form.get('task'))
        try:
            json_user_task = json.loads(user_task)
            f = get_func(json_user_task['task_name'])
            try:
                q.put(json_user_task['params'])
                f_proc = Process(target=f, kwargs=q.get())
                f_proc.start()
            except (jsonschema.ValidationError, KeyError, ValueError):
                print json.dumps({"status": "Value Error", "error_code": 9, "error_msg": "uncorrected task parameters"})
        except ValueError:
            print json.dumps({"status": "Value Error", "error_code": 142, "error_msg": "uncorrected JSON format"})
    return render_template('home.html')


def task(name, json_schema):
    def dec(real_func):
        @wraps(real_func)
        def wrapper(*args, **kwargs):
            jsonschema.validate(kwargs, json_schema)
            return real_func(*args, **kwargs)
        wrapper.__name__ = name
        return wrapper
    return dec


@task(name='multiprint', json_schema={'type': 'object',
                         'properties': {
                             'msg': {'type': 'string'},
                             'count': {'type': 'integer', 'minimum': 1}
                         },
                         'required': ['msg']})
def multi_print(msg, count):
    sleep(random.randint(5, 9))
    print current_process()
    return '\n'.join(msg for _ in xrange(count))


@task(name='mult', json_schema={'type': 'object',
                   'properties': {
                       'operands': {'type': 'array',
                                    'minItems': 1,
                                    'items': {'type': 'number'}}
                    },
                    'required': ['operands']})
def run(operands):
    return reduce(lambda x, y: x * y, operands)


def run_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--params')
    parser.add_argument('t_type')
    args = parser.parse_args()
    if args.t_type == 'runserver':
        app.run()
    else:
        json_params = json.loads(args.params)
        task_type = args.t_type
        f = get_func(task_type)
        f(**json_params)


if __name__ == '__main__':
    run_cli()

