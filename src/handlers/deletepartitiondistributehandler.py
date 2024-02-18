import urllib3
from src.services.redisservice import RedisService
from src.configs.config import get_config
from src.util.key import get_partition_result_key

class DeletePartitionDistributeHandler():
    def __init__(self, 
                 redis_service: RedisService,
                 topic,
                 ignored_partitions):
        self.topic = topic
        self.ignored_partitions = ignored_partitions
        self.redis_service = redis_service
    
    def handle(self):
        ignored_partition_as_str = ","
        ignored_partition_as_str = ignored_partition_as_str.join([str(partition) for partition in self.ignored_partitions])
        key = get_partition_result_key(self.topic, ignored_partition_as_str)
        event = self.redis_service.get_hash_data(key)
        if event is None or len(event) == 0:
            raise Exception("Related Partition event couldn't found")
        
        pod_name = event[b'podName'].decode('utf-8')
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