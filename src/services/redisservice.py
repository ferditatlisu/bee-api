import json
from datetime import timedelta

from redis import Redis, SentinelConnectionPool
from redis.sentinel import Sentinel

from src.configs.config import  get_config
from src.util.key import COPY_EVENT_PREFIX_KEY

TOPIC_WITH_CONSUMER_GROUPS = "consumer_group:{}:{}"
ALL_TOPICS_BY_ID = "topics:{}"
ALL_GROUPS_BY_ID = "groups:{}"

class RedisService:
    redis_connection : Redis
    
    def __init__(self):
        print("Redis service tries to connect")
        sentinel = Sentinel(self.__get_redis_sentinel_hosts())
        redis_config = get_config().redis
        pool = SentinelConnectionPool(service_name=redis_config.masterName, sentinel_manager=sentinel,
                                      password=redis_config.password,
                                      db=redis_config.database)


        self.redis_connection = Redis(connection_pool=pool)
        print("Redis service connected")
        
    def __get_redis_sentinel_hosts(self):
        redis_config = get_config().redis
        redis_hosts = []
        redis_port = redis_config.port
        config_redis_hosts = redis_config.host
        for host in config_redis_hosts:
            redis_hosts.append((host, redis_port))
        return redis_hosts

        
    def get_result(self, key: str):
        response = self.redis_connection.lrange(key, 0, 600)
        response.reverse()
        return response

    def delete(self, key: str):
        self.redis_connection.delete(key)
    
    def get_lenght(self, key):
        return self.redis_connection.llen(key)
    
    def save_topic_consumer(self, key, values):
        if len(values) == 0:
            return
        
        self.delete(key)
        for value in values:
            self.redis_connection.rpush(key, value)
        
    def add_topic_consumer(self, key, value):
        self.redis_connection.rpush(key, value)
        self.redis_connection.expire(key, timedelta(minutes=20))
        
    def get_topics(self, id: int):
        return self.get(ALL_TOPICS_BY_ID.format(id))
    
    def set_topics(self, id: int, topics):
        self.set(ALL_TOPICS_BY_ID.format(id), topics)
        
    def get_groups(self, id: int):
        return self.get(ALL_GROUPS_BY_ID.format(id))
    
    def set_groups(self, id: int, topics):
        self.set(ALL_GROUPS_BY_ID.format(id), topics)
        
    def get_app_cache(self, key: str):
        value = self.redis_connection.get(key)
        return value
    
    def set_app_cache(self, key: str):
        self.redis_connection.set(key, "1")    
        self.redis_connection.expire(key, timedelta(minutes=6))
        
    def get(self, key):
        res = self.redis_connection.get(key)
        if res:
            return json.loads(res)
        
        return None
    
    def set(self, key, value):
        redis_value = json.dumps(value)
        self.redis_connection.set(key, redis_value)
        

    def get_hash_result(self, key: str):
        result = self.redis_connection.hmget(key, "status")
        return result

    def get_copy_pod_name(self, key: str):
        result = self.redis_connection.hmget(key, "podName")
        return result
    
    def get_hash_data(self, key: str):
        return self.redis_connection.hgetall(key)    
    
    def get_all_event_copy_results(self):
        hash_keys = self.redis_connection.keys(f"{COPY_EVENT_PREFIX_KEY}*")
        pipe = self.redis_connection.pipeline()
        for hash_key in hash_keys:
            pipe.hgetall(hash_key)
            
        pipe_values = pipe.execute()
        index = 0
        all_values = []
        for pipe_value in pipe_values:
            tuple_keys = tuple(pipe_value)
            hash_key = hash_keys[index]
            key = hash_key.decode("utf-8")
            topic_names = key.split('||')
            copy_event = {'key': key, 'from_topic' : topic_names[0].replace(COPY_EVENT_PREFIX_KEY, ''), 'to_topic' : topic_names[1]}
            for tuple_key in tuple_keys:
                value = pipe_value[tuple_key] #value
                copy_event[tuple_key.decode("utf-8")] = value.decode("utf-8")
            
            all_values.append(copy_event)
            index +=1
        
        return all_values
