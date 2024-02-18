import json
from typing import List
import urllib3

from src.services.redisservice import RedisService
from src.configs.config import get_config
from src.util.key import get_partition_result_key

class PartitionDistributeHandler():
    def __init__(self, 
                 redis_service: RedisService,
                 cluster_id: int,
                 group_id: str,
                 topic: str,
                 ignored_partitions: List[int]):
        self.cluster_id = cluster_id
        self.group_id = group_id
        self.topic = topic
        self.ignored_partitions = ignored_partitions
        self.redis_service = redis_service
    
    def handle(self):
        ignored_partition_as_str = ","
        ignored_partition_as_str = ignored_partition_as_str.join([str(partition) for partition in self.ignored_partitions])
        key = get_partition_result_key(self.topic, ignored_partition_as_str)
        status = self.redis_service.get_hash_result(key)
        if len(status) > 0 and status[0] is not None:
            raise Exception("Partition process is already exist.")
        
        self.send_master(key)
        return {}
    
    def send_master(self, key: str):
        payload = {
            "clusterId": int(self.cluster_id),
            "groupId": self.group_id,
            "topic": self.topic,
            "ignoredPartitions": self.ignored_partitions,
            "key": key
        }
        body = json.dumps(payload).encode("utf-8")
        http = urllib3.PoolManager()
        res: urllib3.HTTPResponse = http.request(
            "POST",
            get_config().master.partition,
            body=body,
            headers={"Content-Type": "application/json"})
        
        if res.status != 200:
            raise Exception(res.data)