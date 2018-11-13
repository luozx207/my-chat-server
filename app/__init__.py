import os

import eventlet
from flask import Flask,send_file
from flask_socketio import SocketIO

eventlet.monkey_patch()
UPLOAD_FOLDER = '/Users/zixiluo/documents/download'
ALLOWED_EXTENSIONS = set(['txt','doc', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
ASYNC_MODE = 'eventlet'
SECRET_KEY = 'secret!'

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app,async_mode=ASYNC_MODE)

from .chat import *

#react应用入口
@app.route('/')
def index():
    index_path = os.path.join(app.static_folder, 'index.html')
    return send_file(index_path)
