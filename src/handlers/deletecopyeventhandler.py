import urllib3
from src.services.redisservice import RedisService
from src.configs.config import get_config
from src.util.key import  get_copy_result_key

class DeleteCopyEventHandler():
    def __init__(self, 
                 redis_service: RedisService,
                 from_topic,
                 to_topic):
        self.from_topic = from_topic
        self.to_topic = to_topic
        self.redis_service = redis_service
    
    def handle(self):
        key = get_copy_result_key(self.from_topic, self.to_topic)
        copy_event = self.redis_service.get_hash_data(key)
        
        if copy_event is None or len(copy_event) == 0:
            raise Exception("Related Copy event could'nt found")
        
        pod_name = copy_event[b'podName'].decode('utf-8')
        self.redis_service.delete(key)
        self.send_master(pod_name)
        return {}
    
    def send_master(self, pod_name: str):
        http = urllib3.PoolManager()
        res: urllib3.HTTPResponse = http.request(
            "DELETE",
            f"{get_config().master.delete}{pod_name}" ,
            headers={"Content-Type": "application/json"})
        
        if res.status != 200:
            raise Exception(res.data)