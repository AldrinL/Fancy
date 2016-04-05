import redis

r = redis.Redis(host='localhost',port=6379,db=0)
for key in r.hgetall('6073617'): print(key,r.hgetall('6073617')[key])