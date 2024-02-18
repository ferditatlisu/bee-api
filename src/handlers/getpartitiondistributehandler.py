from src.services.redisservice import RedisService
from src.configs.config import get_config
from src.util.key import  get_partition_result_key


class GetPartitionDistributeHandler():
    def __init__(self, 
                 redis_service: RedisService,
                 topic: str,
                 ignored_partitions: str):
        self.redis_service = redis_service
        self.topic = topic
        self.ignored_partitions = ignored_partitions
    
    def handle(self):
        ignored_partition_as_str = ","
        ignored_partition_as_str = ignored_partition_as_str.join([str(partition) for partition in self.ignored_partitions])
        key = get_partition_result_key(self.topic, ignored_partition_as_str)
        data = self.redis_service.get_hash_data(key)
        if data is None or len(data) == 0:
            raise Exception("Not found")
        
        event = {'key': key, 'topic' : self.topic, 'ignored_partitions' : self.ignored_partitions}
        for item in data:
            event[item.decode("utf-8")] = data[item].decode("utf-8")
        
        return event