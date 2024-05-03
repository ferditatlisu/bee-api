import json
from typing import List
from src.services.kafkaserviceinterface import KafkaServiceInterface

from src.services.redisservice import TOPIC_WITH_CONSUMER_GROUPS, RedisService
from src.services.kafkaservice import KafkaService
from src.handlers.lagofgrouphandler import LagOfGroupHandler
from src.dto.topicdata import TopicData
from kafka.admin import NewTopic


class CreateTopicHandler:
    def __init__(self, kafka_service: KafkaServiceInterface, 
                 topic_name: str, partition_count: int, 
                 retention_ms: int):
        self.kafka_service = kafka_service
        self.topic_name = topic_name
        self.partition_count = partition_count
        self.retention_ms = retention_ms

    def handle(self):
        admin_client = self.kafka_service.get_admin_client()
        
        config = {
                "min.insync.replicas": "2",
                "retention.ms": self.retention_ms,
                "segment.ms": self.retention_ms,
                "cleanup.policy": "delete"
            }
        
        new_topic = NewTopic(
            name= self.topic_name, 
            num_partitions= self.partition_count, 
            replication_factor= 3, 
            topic_configs= config)
        
        response = admin_client.create_topics([new_topic])
        print(response)
        return {}
    
