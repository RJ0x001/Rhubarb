from web import *
import json

json_schema={'type': 'object',
                         'properties': {
                             'msg': {'type': 'string'},
                             'count': {'type': 'integer', 'minimum': 1}
                         },
                         'required': ['msg']}


@app.route('/', methods=['GET', 'POST'])
def home():
    options = [
        {"Label": "Joe", "Selected": False},
        {"Label": "Steve", "Selected": True}
    ]
    if request.method == 'POST':
        user_task = str(request.form.get('task'))
        '''
        if session.query(Tasks.id).filter_by(task_type=user_type).scalar():  # check type in db
            print 'Yes!'
        else:
            print 'No =('
        '''
        print user_task
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)





'''
tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]


@app.route('/', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})


if __name__ == '__main__':
    app.run(debug=True)
'''



