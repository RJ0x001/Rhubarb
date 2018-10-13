import tasks
import argparse, json
from flask import Flask, request, render_template, redirect, url_for, jsonify
from urlparse import urlparse
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, update, create_engine, DateTime, Boolean
from sqlalchemy.sql import select, exists
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base


@tasks.task(name='multiprint',
            json_schema={'type': 'object',
                                            'properties': {
                                                'msg': {'type': 'string'},
                                                'count': {'type': 'integer', 'minimum': 1}
                                            },
                                            'required': ['msg']})
def multi_print(msg, count):
    return '\n'.join(msg for _ in xrange(count))


@tasks.task(name='mult',
            json_schema={'type': 'object',
                                    'properties': {
                                    'operands': {'type': 'array',
                                    'minItems': 1,
                                    'items': {'type': 'number'}}
                                    },
                                    'required': ['operands']})
def mult(operands):
    return reduce(lambda x, y: x*y, operands)

functions_params = {'multiprint': (multi_print, 'msg, count'),
                    'mult': (mult, 'operands')}

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_task = str(request.form.get('task'))
        try:
            json_ut = json.loads(user_task)
            user_type = json_ut['task_name']
            if user_type in functions_params:
                functions_params[user_type][0]('hi', 2)

        except ValueError:
            print {
                "status": "Value Error",
                "error_code": 100,
                "error_msg": "not JSON format"
            }
        '''
        if session.query(Tasks.id).filter_by(task_type=user_type).scalar():  # check type in db
            print 'Yes!'
        else:
            print 'No =('
        '''
    return render_template('home.html')





if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('runserver')
    args = parser.parse_args()
    #multi_print('hi', 3)
    if args.runserver:
        app.run(debug=True)
        multi_print('hi', 3)
