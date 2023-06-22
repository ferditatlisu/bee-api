from typing import Any, Dict, List

from kafka.admin import ConfigResource, ConfigResourceType, KafkaAdminClient
from kafka.protocol.admin import DescribeConfigsResponse
from kafka.structs import TopicPartition

from src.configs.config import get_config
from src.services.kafkaservice import KafkaService
from src.services.kafkaserviceinterface import KafkaServiceInterface


class GetTopicInfoHandler():
    def __init__(self, kafka_service : KafkaServiceInterface, topic: str):
        self.kafka_service = kafka_service
        self.topic = topic
        
    def get_topic_partition(self):
        consumer = self.kafka_service.get_consumer()
        topic_partitions = []
        partitions = consumer.partitions_for_topic(self.topic)
        if partitions:
            for partition in partitions:
                topic_partition = TopicPartition(self.topic, partition)
                topic_partitions.append(topic_partition)
    
                    
        return topic_partitions
    
    def get_total_message_count(self):
        consumer = self.kafka_service.get_consumer()    
        topic_partitions = self.get_topic_partition()
        consumer.assign(topic_partitions)
        end_offsets = consumer.end_offsets(topic_partitions)
        beginning_offsets = consumer.beginning_offsets(topic_partitions)
        messages = {}
        
        if end_offsets:
            for topic_partition, hw in end_offsets.items():
                messages[topic_partition.partition] = hw
        
        if beginning_offsets:
            for topic_partition, hw in beginning_offsets.items():
                messages[topic_partition.partition] -= hw
        
        total_message_count = 0
        for count in messages.values():
            total_message_count += count
            
        return total_message_count
        
    
        
    def get_retention_ms(self):
        admin_client = self.kafka_service.get_admin_client()
        configs = admin_client.describe_configs(config_resources=[ConfigResource(ConfigResourceType.TOPIC, self.topic)])
        config_list = configs[0].resources[0][4]
        configs = []
        for config in config_list:
            if config[0] == 'retention.ms':
                return int(config[1]) /1000 /60 /60 /24
            
        return None
    
    def get_partition_count(self):
        topic_partitions = self.get_topic_partition()
        return len(topic_partitions)
        
    def handle(self):    
        partition_count = self.get_partition_count()
        retention_day = self.get_retention_ms()
        total_message_count = self.get_total_message_count()
        return { 
                'partition_count': partition_count,
                'retention_day' : retention_day,
                'message_count' : total_message_count  
            }
