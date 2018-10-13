import argparse, jsonschema, json
from functools import wraps
from flask import Flask, request, render_template
from multiprocessing import Process, Queue, current_process
from time import sleep, time
from random import randint
from email_test import *


def send_email(email, time_before, time_after, result, name):
    msg = MIMEText('Function %r have completed. Result %r. Execution time %s' %
                       (name, result, (time_after - time_before)))
    msg['Subject'] = 'Function %r have completed.' % name
    s = smtplib.SMTP_SSL(smtp_server)
    s.login(me, my_pass)
    msg['From'] = me
    msg['To'] = email
    s.sendmail(me, [you], msg.as_string())
    s.quit()


def task(name, json_schema):
    def dec(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            jsonschema.validate(args[0]['params'], json_schema)
            try:
                time_before = time()
                result = func(*args[0]['params'].values())
                time_after = time()
                if args[0]['email']:
                    send_email(args[0]['email'], time_before, time_after, result, func.__name__)
                return result
            except TypeError:
                print 'Error! Incorrect values'

        return wrapper
    return dec


@task(name='multiprint',
            json_schema={'type': 'object',
                        'properties': {
                            'msg': {'type': 'string'},
                            'count': {'type': 'integer', 'minimum': 1}
                        },
                        'email': 'email',
                        'required': ['msg']})
def multi_print(msg, count):
    sleep(randint(8, 12))
    print current_process().name
    return '\n'.join(msg for _ in xrange(count))



@task(name='mult',
            json_schema={'type': 'object',
                                    'properties': {
                                    'operands': {'type': 'array',
                                    'minItems': 1,
                                    'items': {'type': 'number'}}
                                    },
                                    'required': ['operands']})
def mult(operands):
    sleep(randint(4, 10))
    print reduce(lambda x, y: x*y, operands)


func_map = {'multiprint': multi_print,
            'mult': mult}
app = Flask(__name__)
q = Queue()


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_task = str(request.form.get('task'))
        try:
            json_ut = json.loads(user_task)
            user_type = json_ut['task_name']
            if user_type in func_map:
                q.put(json_ut)
                func = func_map[json_ut['task_name']]
                func_proc = Process(target=func, args=((q.get()),))
                func_proc.start()
                #result_json = json.dumps({"result": func(json_ut['params'])})
        except ValueError:
            print json.dumps({"status": "Value Error", "error_code": 142, "error_msg": "not JSON format"})

    return render_template('home.html')


def run_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--params', type=str)
    parser.add_argument('t_type')
    args = parser.parse_args()
    if args.t_type == 'runserver':
        app.run()
    else:
        json_params = json.loads(args.params)
        func = func_map[args.t_type]
        print func(json_params)
    q.close()
