import redis


class RedisService():

    def __init__(self):
        self.r = redis.Redis(host='redis-12898.c16.us-east-1-2.ec2.cloud.redislabs.com', port=12898,
                             password='k7wHdL5obJiGGTVhd4hjrpZUmsPImLpi')

    def read(self, key):
        return self.r.get(key).decode('utf-8')

    def write(self, key, value):
        try:
            self.r.set(key, str(value)).encode('utf-8')
            return 'ok'
        except:
            return 'error'

    def write_with_expire(self, key, value, time):
        try:
            self.r.set(key, str(value), ex=time).encode('utf-8')
            return 'ok'
        except:
            return 'error'

    def delete_key(self, key):
        try:
            self.r.delete(key)
            return 'ok'
        except:
            return 'error'
