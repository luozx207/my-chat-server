#标准库导入
from datetime import datetime

#第三方库导入
import eventlet
from flask import render_template, session, request, jsonify, send_from_directory
from flask_socketio import emit, join_room, leave_room, rooms

#本地应用程序导入
#.dvServ相对导入，表示在同级目录下寻找
from .dbServ import mysqlServ
from .dbServ import redisServ
#绝对导入，必须从项目根目录开始
from app import socketio

eventlet.monkey_patch()

@socketio.on('connect')
def user_connect():
    #连接后先把所有名字发到新客户端，用于判断重名
    all_name = mysqlServ.getName()
    #返回的数据一行是一个tuple，每个tuple依次存在数组
    #例如[('123',), ('adf',)]。
    name_list = [x[0] for (x) in all_name]
    emit('all_name', {'data': name_list})
    #之前不知道怎么判断连接的唯一性，后来知道了可以用request.sid，那就不用每次断开连接就点名了
    #sid是socket建立连接时三次握手成功时服务器返回，是请求的cookie
    print((' - Client {} connected.'.format(request.sid)))

@socketio.on('disconnect')
def user_disconnect():
    name = redisServ.delete_all(request.sid)
    emit('del_name', name, broadcast=True)
    print(' - Client {} disconnected.'.format(request.sid))

# @socketio.on('roll_call_back', namespace='/test_conn')
# def roll_call_back(name):
#     global now_name
#     now_name.append(name)

@socketio.on('login')
def user_login(form):
    #http与ws都是明文传输，传输安全程度是一样的
    name = form['name']
    #判断此用户是否在线
    if name in redisServ.r.hvals('online_name'):
        emit('login_feedback', {'code':3,'msg':"该用户已在线"})
    else:
        result = mysqlServ.checkForm(name, form['password'])
        #登录成功，记录登录信息，由于sid是连接建立时服务器确认客户端的唯一标示
        #因此一个sid绑定一个客户端，不可能伪造
        if result['code'] == 0:
            #online_name则记录了当前在线用户，要将当前连接的sid与用户名字绑定
            redisServ.r.hset('online_name', request.sid,name)
            #向所有用户广播新用户名字，此时自己的聊天室组件还未渲染，因此自己不会收到
            emit('add_name', name, broadcast=True)
        emit('login_feedback', result)

@socketio.on('regist')
def user_regist(form):
    n = form['name']
    p = form['password']
    #确认表单不为空，姓名和密码字段不超长
    if n and p and len(n)<=40 and len(p)<=20:
        result = mysqlServ.addUser(form['name'], form['password'])
        emit('regist_feedback', result)

@socketio.on('online')
def user_online(name):
    #接收到登录后才能发送的事件时，要先验证登录状态，否则未登录的客户端也可以发送这些事件来获取数据
    #验证登录的方式是：判断此客户端的sid是否在online_name中
    if redisServ.check_online(request.sid):
        # 先将在线用户列表发给当前新用户
        # 只需要把所有的名字取出来，取出来后是一个列表
        online_name = redisServ.r.hvals('online_name')
        emit('online_name', online_name)

        #****************加载大厅历史消息*********************
        msg_list = mysqlServ.initMsg(request.sid)
        #每个元素是一个tuple，例如(12, 'iii', '10', '2018/10/15 上午10:17:46')
        emit('history_message',[{'name':x[1],
                                'data':x[2],
                                'time':x[3]}for x in msg_list])

        #****************加载私聊聊天记录*********************
        rooms = mysqlServ.getRooms(name)
        data = []
        for room in rooms:
            msg_list = mysqlServ.getRoomMsg(room['room_id'])
            #有聊天记录的才发到前端
            if msg_list:
                data.append({'room':room['room_id'],
                            'name':room['guest'] if (room['invitor'] == name) else room['invitor'],
                            'msg':[{'name':m['name'],
                                    'data':m['data'],
                                    'time':m['time']}for m in msg_list]})
        emit('rooms',data)


@socketio.on('load_msg')
def load_msg():
    if redisServ.check_online(request.sid):
        #以sid为key，记录下一批消息的末位数据id
        if int(redisServ.r.get(request.sid))<=0:
            emit('no_more_message')
        else:
            msg_list = mysqlServ.historyMsg(request.sid)
            emit('history_message',[{'name':m['name'],
                                    'data':m['data'],
                                    'time':m['time']}for m in msg_list])

@socketio.on('imessage')
def test_message(message):
    if redisServ.check_online(request.sid):
        #判断消息内容的合法性
        if message['data'] and len(message['data'])<=250:
            mysqlServ.insertMsg(message)
            emit('message', message, broadcast=True)

@socketio.on('check_room')
def check_room(data):
    if redisServ.check_online(request.sid):
        invitor = data['name']
        guest = data['guest']
        #查看此房间是否存在
        room_id = mysqlServ.getRoom(invitor,guest)
        if room_id:
            msg_list = mysqlServ.getRoomMsg(room_id)
            #先将聊天记录发给自己，在被邀请者加入房间后再把聊天记录发给邀请者
            if msg_list:
                emit('room_msg',[{'room':m['room_id'],
                            'name':m['name'],
                            'data':m['data'],
                            'time':m['time']}for m in msg_list])
        else:
            room_id = mysqlServ.createRoom(invitor,guest)
        #自己进入房间
        join_room(room_id)
        #邀请对方进入房间
        emit('invite', {'invitor':data['name'], 'guest':data['guest'],
                        'room':room_id}, broadcast=True)

@socketio.on('join')
def join(room):
    if redisServ.check_online(request.sid):
        join_room(room)
        msg_list = mysqlServ.getRoomMsg(room)
        if msg_list:
            emit('room_msg', [{'room':m['room_id'],
                        'name': m['name'],
                        'data':m['data'],
                        'time':m['time']}for m in msg_list])

@socketio.on('room_message')
def room_message(data):
    # r.hset('message','test',{'name':message['name'],'data':message['data'],'time':message['time']})
    #其实不需要用hash类型，只要把消息按顺序存到一个列表里就行了
    #rpush是从右边push一个值，lpush是从左边
    if redisServ.check_online(request.sid):
        #判断消息内容的合法性
        if data['data'] and len(data['data']) <= 250:
            mysqlServ.addRoomMsg(data)
            emit('room_new_msg', data, room=data['room'])
