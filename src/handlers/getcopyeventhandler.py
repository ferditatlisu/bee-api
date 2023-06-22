from src.services.redisservice import RedisService
from src.configs.config import get_config
from src.util.key import COPY_EVENT_PREFIX_KEY, get_copy_result_key


class GetCopyEventHandler():
    def __init__(self, 
                 redis_service: RedisService,
                 from_topic: str,
                 to_topic: str):
        self.redis_service = redis_service
        self.from_topic = from_topic
        self.to_topic = to_topic
    
    def handle(self):
        key = get_copy_result_key(self.from_topic, self.to_topic)
        data = self.redis_service.get_hash_data(key)
        
        if data is None or len(data) == 0:
            raise Exception("Not found")
        
        copy_event = {'key': key, 'from_topic' : self.from_topic, 'to_topic' : self.to_topic}
        for item in data:
            copy_event[item.decode("utf-8")] = data[item].decode("utf-8")
        
        return copy_event