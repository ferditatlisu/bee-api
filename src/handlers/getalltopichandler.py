from typing import Any, Dict
from src.services.kafkaserviceinterface import KafkaServiceInterface
from src.services.kafkaservice import KafkaService
from src.services.redisservice import RedisService

class GetAllTopicHandler():
    def __init__(self, kafka_service: KafkaServiceInterface, redis_service: RedisService, from_cache:bool):
        self.kafka_service = kafka_service
        self.redis_service = redis_service
        self.from_cache = from_cache
        
    def handle(self):
        topics = self.get_from_cache()
        if not topics:
            topics = []
            consumer = self.kafka_service.create_consumer()
            topic_metadatas = consumer.topics()
            for topic_metadata in topic_metadatas:
                topics.append(topic_metadata)
                
            self.set_to_cache(topics)
            consumer.close()
            
        return topics
    
    def get_from_cache(self):
        if self.from_cache:
            return self.redis_service.get_topics(self.kafka_service.get_id())
        
        return None
    
    def set_to_cache(self, topics):
        if self.from_cache and len(topics) > 0:
            self.redis_service.set_topics(self.kafka_service.get_id(), topics)