import json
import urllib3

from src.services.redisservice import RedisService
from src.configs.config import get_config
from src.util.key import COPY_EVENT_PREFIX_KEY, get_copy_result_key


class CopyEventHandler():
    def __init__(self, 
                 redis_service: RedisService,
                 from_topic: str,
                 from_id: int,
                 to_topic: str,
                 to_id: int):
        self.from_topic = from_topic
        self.from_id = from_id
        self.to_topic = to_topic
        self.to_id = to_id
        self.redis_service = redis_service
    
    def handle(self):
        key = get_copy_result_key(self.from_topic, self.to_topic)
        status = self.redis_service.get_hash_result(key)
        if len(status) > 0 and status[0] is not None:
            raise Exception("Copy process is already exist.")
        
        self.send_master(key)
        return {}
    
    def send_master(self, key: str):
        payload = {
            "fromTopic": self.from_topic,
            "fromId": int(self.from_id),
            "toTopic": self.to_topic,
            "toId": int(self.to_id),
            "key": key
        }
        body = json.dumps(payload).encode("utf-8")
        http = urllib3.PoolManager()
        res: urllib3.HTTPResponse = http.request(
            "POST",
            get_config().master.copy,
            body=body,
            headers={"Content-Type": "application/json"})
        
        if res.status != 200:
            raise Exception(res.data)