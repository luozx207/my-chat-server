from .mysqlConn  import connectMysql
from .redisServ import r
from .utils import HAMC_password,check_password

#处理数据库数据的业务逻辑

def insertMsg(msg):
    with connectMysql() as cursor:
        #mysql.connector用 %s 作为占位符
        #pymysql用 ? 作为占位符
        cursor.execute('insert into message (name,data,time) value (%s,%s,%s)',
                        (msg['name'],msg['data'],msg['time']))

def historyMsg(sid):
    with connectMysql(True) as cursor:
        end=int(r.get(sid))
        start=end-14
        r.set(sid,start-1)
        #即使下限是负数也可以取到值
        cursor.execute('select * from message where msg_id between %s and %s',
                        (start,end))
        msg=cursor.fetchall()
        return msg

def initMsg(sid):
    with connectMysql() as cursor:
        cursor.execute('select count(msg_id) from message')
        count=cursor.fetchone()[0]
        start=count-14
        #记录下一次取数的末尾
        r.set(sid,start-1)
        cursor.execute('select * from message where msg_id between %s and %s',
                        (start,count))
        msg=cursor.fetchall()
        return msg

def getRoom(invitor,guest):
    with connectMysql() as cursor:
        cursor.execute('select room_id from room where invitor in (%s,%s) and guest in (%s,%s)',
                        (invitor,guest,invitor,guest))
        room_id=cursor.fetchone()
        if room_id:
            room_id=room_id[0]
        return room_id

def getRooms(name):
    with connectMysql(True) as cursor:
        cursor.execute('select * from room where invitor=%s or guest=%s',
                        (name,name))
        rooms=cursor.fetchall()
        return rooms

def getRoomMsg(id):
    with connectMysql(True) as cursor:
        cursor.execute('select * from room_msg where room_id=%s',(id,))
        msg=cursor.fetchall()
        return msg

def createRoom(invitor,guest):
    with connectMysql() as cursor:
        cursor.execute('insert into room (invitor,guest)values(%s,%s)',
                        (invitor,guest))
        cursor.execute('select last_insert_id()')
        room_id=cursor.fetchone()[0]
        return room_id

def addRoomMsg(msg):
    with connectMysql() as cursor:
        cursor.execute('insert into room_msg (room_id,name,data,time) value (%s,%s,%s,%s)',
                        (msg['room'],msg['name'],msg['data'],msg['time']))

def getName():
    with connectMysql() as cursor:
        cursor.execute('select name from user')
        name=cursor.fetchall()
        return name

def addUser(name,password):
    with connectMysql() as cursor:
        #将密码用HAMC算法加密后再存入数据库，加密后password是byte类型
        password=HAMC_password(password)
        #可能在用户注册的过程中，有其他用户在这期间注册了这个名字，那么存数据就会出问题
        #name具有唯一性的属性，利用异常处理再次验证一下重名问题
        try:
            cursor.execute('insert into user (name,password) value (%s,%s)',
                            (name,password))
        except mysql.connector.errors.IntegrityError:
            #重名错误
            #1062 (23000): Duplicate entry '123' for key 'name_UNIQUE'
            #type:mysql.connector.errors.IntegrityError
            return {'code':0,'msg':"该用户名已被注册"}
        return {'code':1,'msg':"注册成功"}

def checkForm(name,password):
    #code=False会将数据库连接的参数use_unicode置为false，这样mysqlconnector
    #就不会试图将数据库密码字段的字节转为字符串
    with connectMysql(code=False) as cursor:
        #判断数据是否存在性能较高的写法，select count(*) from user where name=.. 会浪费性能
        #下面sql语句会在找到第一个数据之后就停止，并返回，如果没找到会返回空集
        cursor.execute('select password from user where name=%s limit 1',(name,))
        real_password=cursor.fetchone()
        print(type(real_password[0]))
        if real_password:
            #用户名存在，检查密码
            #将密码经过同样的加密计算，然后判断是否与数据库中计算结果相同
            if check_password(password,real_password[0]):
                code=0
                msg=name
            else:
                code=1
                msg="密码错误"
        else:
            code=2
            msg="用户名不存在"
        return {'code':code, "msg":msg}

if __name__=='__main__':
    print(checkForm('123','456'))
