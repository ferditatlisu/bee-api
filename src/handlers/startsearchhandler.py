import json
from typing import Dict

import urllib3
from src.configs.config import get_config
from src.dto.searchdata import SearchData
from src.services.redisservice import RedisService
from src.util.key import get_search_metadata_key

class StartSearchHandler():
    def __init__(self, kafka_id: str, redis: RedisService, data : Dict):
        self.kafka_id = kafka_id
        self.redis = redis
        self.data= SearchData(data)
        
    def handle(self):
        metadata_key = get_search_metadata_key(self.data.key)
        data = self.redis.get_hash_data(metadata_key)
        response = {}
        results = []
        if len(data) == 0:
            self.start_search()
            data = self.redis.get_hash_data(metadata_key)
        
        for k, v in data.items():
            response[k.decode('UTF-8')] = v.decode('UTF-8')
        
        results = self.redis.get_result(self.data.key)
        results = self.get_active_search_result(results)    
        response['data'] = results
        
        return response

    def start_search(self):
        self.send_master()
    
    def get_active_search_result(self, results):
        res = []
        for result in results:
            res.append(json.loads(result.decode('UTF-8')))
            
        return res
    
    def send_master(self):
        payload = {
            "topic": self.data.topic_name,
            "kafkaId": self.kafka_id,
            "value": self.data.value,
            "key": self.data.key,
            "metadataKey": get_search_metadata_key(self.data.key)
        }
        body = json.dumps(payload).encode("utf-8")
        http = urllib3.PoolManager()
        res: urllib3.HTTPResponse = http.request(
            "POST",
            get_config().master.search,
            body=body,
            headers={"Content-Type": "application/json"})
        
        if res.status != 200:
            raise Exception(res.data)