from typing import List

from src.services.redisservice import RedisService
from src.services.kafkaserviceinterface import KafkaServiceInterface

class GetAllConsumerGroupsHandler():
    def __init__(self, kafka_service : KafkaServiceInterface, redis_service: RedisService, from_cache:bool):
        self.kafka_service = kafka_service
        self.redis_service = redis_service
        self.from_cache = from_cache
        
    def handle(self):
        groups = self.get_from_cache()
        if not groups:
            groups = []
            admin_client = self.kafka_service.get_admin_client()
            consumer_groups = admin_client.list_consumer_groups()
            for consumer_group in consumer_groups:
                groups.append(consumer_group[0])
                
            self.set_to_cache(groups)
        
        return groups
    
    def get_from_cache(self):
        if self.from_cache:
            return self.redis_service.get_groups(self.kafka_service.get_id())
        
        return None
    
    def set_to_cache(self, groups):
        if self.from_cache and len(groups) > 0:
            self.redis_service.set_groups(self.kafka_service.get_id(), groups)
            