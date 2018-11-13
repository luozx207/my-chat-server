import mysql.connector

config={
    'host': 'localhost',
    'user': 'root',
    'password': '123',
    'port': 3306,
    'database': 'mychat',
    'charset': 'utf8mb4'
    #为了能保存表情，同时数据库中data字段也要设置为utf8mb4编码
    #utf8mb4 是 utf8 的超集，由于一个表情由四个字节组成，但utf8只能存储3个字节
    #因此只能使用可以储存四个字节的utf8mb4
    #使用utf8mb4的字段最好都使用varchar，否则
    #MySQL必须为一个使用 utf8mb4 字符集的  char（10）的列保留40字节空间
}

#这个类是连接数据库的上下文管理器，它建立数据库连接，并在程序运行后关闭数据库连接
class connectMysql:
    def __init__(self,dic=None,code=True):
        self.dic=dic
        self.code=code

    def __enter__(self):
        self.conn=mysql.connector.connect(**config,use_unicode=self.code)
        self.cursor=self.conn.cursor(dictionary=self.dic)
        return self.cursor

    def __exit__(self, *args):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()
