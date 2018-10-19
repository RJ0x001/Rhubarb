import argparse, types, json, jsonschema, random, smtplib
from functools import wraps
from time import sleep, time
from multiprocessing import Process, Queue, current_process
from config import *
from email.mime.text import MIMEText
from email_params import *
from config import *


def send_email(email, time_before, time_after, result, name):
    '''
    Send email to user

    '''
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
    '''
    :param task_type: user task name
    :return: decorated function
    '''
    for name, obj in list(globals().items()):
        if isinstance(obj, types.FunctionType) and obj.__name__ == task_type:
            true_func_str = name
            f = globals()[true_func_str]
            return f


@app.route('/', methods=['GET', 'POST'])
def home():
    '''
    Flask main page.
    Taking task from users
    :return:
    '''
    if request.method == 'POST':
        q = Queue()
        user_task = str(request.form.get('task'))
        try:
            json_user_task = json.loads(user_task)
            f = get_func(json_user_task['task_name'])
            try:
                q.put(json_user_task)
                f_proc = Process(target=f, kwargs=q.get())
                f_proc.start()
            except (jsonschema.ValidationError, KeyError, ValueError):
                print json.dumps({"status": "Value Error", "error_code": 9, "error_msg": "uncorrected task parameters"})
        except ValueError:
            print json.dumps({"status": "Value Error", "error_code": 142, "error_msg": "uncorrected JSON format"})
    return render_template('home.html')


def task(name, json_schema=None):
    '''
    Decorator to executing functions. Validate user parameters, adding data to database
    :param name: task name
    :param json_schema: schema to validation user's parameters
    :return: result of function execute
    '''
    def dec(real_func):
        @wraps(real_func)
        def wrapper(*args, **kwargs):
            if 'email' in kwargs:
                email = kwargs['email']
            else:
                email = None
            if 'params' in kwargs:
                kwargs = kwargs['params']
            if json_schema:
                jsonschema.validate(kwargs, json_schema)
            print json.dumps({"status": "OK"})
            session.add(Tasks(params=str(kwargs), mail=email, task_name=name))
            session.commit()
            row_id = session.query(Tasks.id).order_by(Tasks.id.desc()).first()
            time_before = time()
            result = real_func(*args, **kwargs)
            time_after = time()
            if email:
                send_email(email, time_before, time_after, result, name)
                print json.dumps({"msg": "explanatory letter was sent to specified email"})
            session.query(Tasks).filter(Tasks.id == row_id[0]). \
                update({Tasks.done: 1,
                        Tasks.time_execute: time_after - time_before,
                        Tasks.result: unicode(str(result), )
                        })
            session.commit()
            return result
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
    '''
    Test function to making tasks
    '''
    return '\n'.join(msg for _ in xrange(count))


@task(name='mult')
def run(operands):
    '''
    Test function to making tasks
    '''
    print reduce(lambda x, y: x * y, operands)


def run_cli():
    '''
    Taking parameters from cli, then run flask server or executing function
    '''
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
