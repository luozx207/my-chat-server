import redis

r = redis.StrictRedis(host='localhost', port=6379,decode_responses=True)
#decode_responses=True使redis将返回的字符串解码为string类型（存在redis数据库中的仍然是未解码的数据）

def check_online(sid):
    return r.hexists('online_name',sid)

def delete_all(sid):
    name = r.hget('online_name',sid)
    r.hdel('online_name',sid)
    #删除自身缓存，但房间的聊天内容会被存储
    r.delete(sid)
    return name
