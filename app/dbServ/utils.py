#内置的密码加密模块
from hashlib import sha256
from hmac import HMAC
import os

def HAMC_password(password,salt=None):
    #密码和随机生成的salt字符串混淆，然后再进行 hash
    #最后把 hash 值和 salt 值一起存储。
    #验证密码的时候只要用 salt再与密码原文做一次相同步骤的运算，比较结果与存储的 hash 值就可以了。
    if salt is None:
    #随机生成4个字节（32bits）的字节串，类型是byte
        salt=os.urandom(4)
    #将str类型的password编码为byte
    password = password.encode('UTF-8')
    return salt+HMAC(password, salt, sha256).digest()

def check_password(password,hashed):
    return hashed==HAMC_password(password,salt=hashed[:4])

if __name__ =='__main__':
    a=HAMC_password('123')
    print(a)
    print(type(a))
