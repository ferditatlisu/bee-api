from typing import Dict
import urllib3
from src.configs.config import get_config
from src.dto.searchdata import SearchData
from src.services.redisservice import RedisService
from src.util.key import get_search_metadata_key

class DeleteSearchHandler():
    def __init__(self, redis: RedisService, data : Dict):
        self.redis = redis
        self.data= SearchData(data)
        
    def handle(self):
        self.redis.delete(self.data.key)
        metadata_key = get_search_metadata_key(self.data.key)
        search_metadata = self.redis.get_hash_data(metadata_key)
        pod_name = search_metadata[b'podName'].decode('utf-8')
        self.redis.delete(metadata_key)
        self.send_master(pod_name)
        return {}
        
    def send_master(self, pod_name: str):
        http = urllib3.PoolManager()
        res: urllib3.HTTPResponse = http.request(
            "DELETE",
            f"{get_config().master.delete}{pod_name}" ,
            headers={"Content-Type": "application/json"})
        
        if res.status != 200:
            print(res.data)