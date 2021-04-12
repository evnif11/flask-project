from flask import jsonify
from flask import request
from flask import Blueprint
from flask import session
from models import Todo, db, User
import datetime
import requests

from . import api

def send_slack(msg):
    res = requests.post('https://hooks.slack.com/services/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', json={
        'text': msg
    }, headers={ 'Content-Type': 'application/json'})

@api.route('/todos/done', methods=['PUT'])
def todos_done():
    userid = session.get('userid', 1)
    if not userid:
        return jsonify(), 401

    data = request.get_json()
    todo_id = data.get('todo_id')

    todo = Todo.query.filter_by(id=todo_id).first()
    user = User.query.filter_by(userid=userid).first()

    if todo.user_id != user.id:
        return jsonify(), 400

    todo.status = 1

    db.session.commit()


    send_slack('TODO가 완료되었습니다.\n사용자: %s\n할일 제목: %s'%(user.userid, todo.title))


    return jsonify()


@api.route('/todos', methods=['GET', 'POST', 'DELETE'])
def todos():
    userid = session.get('userid', None)

    if not userid:
        return jsonify(), 401

    if request.method == 'POST':

        data = request.get_json()

        todo = Todo()
        todo.title = data.get('title')

        user = User.query.filter_by(userid=userid).first()
        todo.user_id = user.id

        todo.due=data.get('due')
        todo.status = 0

        db.session.add(todo)
        db.session.commit()

        send_slack('TODO가 생성되었습니다.\n사용자: %s\n할일 제목: %s\n기한: %s'%(user.userid, todo.title, todo.due))

        return jsonify(), 201

    elif request.method == 'GET':
        print(userid)
        todos = Todo.query.filter_by(user_id=userid)
        print(userid)
        return jsonify([t.serialize for t in todos])

    elif request.method == 'DELETE':
        data = request.get_json()
        todo_id = data.get('todo_id')

        todo = Todo.query.filter_by(id=todo_id).first()

        db.session.delete(todo)
        db.session.commit()

        return jsonify(), 203

    return jsonify(data)


@api.route('/slack/todos', methods=['POST'])
def slack_todos():
    res = request.form['text'].split(' ')
    cmd, *args = res

    ret_msg = ''
    if cmd == 'create':
        todo_user_id = args[0]
        todo_name = args[1]
        todo_due = args[2]

        user = User.query.filter_by(userid=todo_user_id).first()

        todo = Todo()
        todo.user_id = user.id
        todo.title = todo_name
        todo.due = todo_due
        todo.status = 0

        db.session.add(todo)
        db.session.commit()
        ret_msg = 'todo가 생성되었습니다'

        send_slack('[%s] %s'%(str(datetime.datetime.now()), todo_name)) # 날짜, 할 일 제목
    elif cmd == 'list':
        todo_user_id = args[0]
        user = User.query.filter_by(userid=todo_user_id).first()

        todos = Todo.query.filter_by(user_id=user.id)

        for todo in todos:
            ret_msg += '%d. %s (~ %s, %s)\n'%(todo.id, todo.title, todo.due, ('미완료', '완료')[todo.status])
    elif cmd == 'done':
        todo_id = args[0]
        todo = Todo.query.filter_by(id=todo_id).first()

        todo.status = 1
        db.session.commit()


        ret_msg = 'todo가 완료 처리되었습니다'

    elif cmd == 'undo':
        todo_id = args[0]
        todo = Todo.query.filter_by(id=todo_id).first()

        todo.status = 0
        db.session.commit()

        ret_msg = 'todo가 미완료 처리되었습니다'

    return ret_msg
