from flask import Flask, render_template, json
import redis
import uuid
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)
r = redis.Redis(host='localhost', port=6379, db=0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    messages = r.hgetall('messages')
    message_list = []

    for message_id, message_data in messages.items():
        message = {
            'id': message_id.decode(),
            'data': json.loads(message_data.decode())
        }
        message_list.append(message)

    emit('message_list', message_list, broadcast=True, namespace='/chat')

    return render_template('chat.html')

@socketio.on('message')
def handle_message(data):
    if 'username' not in data:
        return
    username = data['username']
    message = data['message']
    message_id = str(uuid.uuid4())

    r.hset('messages', message_id, json.dumps({'username': username, 'message': message}))

    emit('message', {'username': username, 'message': message}, broadcast=True)

def emit_saved_messages():
    messages = r.hgetall('messages')
    message_list = []

    for message_id, message_data in messages.items():
        message = json.loads(message_data)
        message_list.append({'id': message_id.decode(), 'data': message})

    emit('message_list', message_list, broadcast=True, namespace='/chat')

def emit_message(message_id):
    message_data = json.loads(r.hget('messages', message_id))
    emit('message', {'id': message_id, 'data': message_data}, broadcast=True, namespace='/chat')

if __name__ == '__main__':
    socketio.run(app, debug=True)
