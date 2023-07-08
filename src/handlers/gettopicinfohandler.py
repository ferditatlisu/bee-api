from typing import Any, Dict, List
from kafka import KafkaConsumer

from kafka.admin import ConfigResource, ConfigResourceType
from kafka.structs import TopicPartition
from src.handlers.messagecounthandler import MessageCountHandler
from src.services.kafkaserviceinterface import KafkaServiceInterface

class GetTopicInfoHandler():
    def __init__(self, kafka_service : KafkaServiceInterface, topic: str):
        self.kafka_service = kafka_service
        self.topic = topic
        self.consumer: KafkaConsumer = self.kafka_service.get_consumer()
        
    def get_topic_partition(self):
        topic_partitions = []
        partitions = self.consumer.partitions_for_topic(self.topic)
        if partitions:
            for partition in partitions:
                topic_partition = TopicPartition(self.topic, partition)
                topic_partitions.append(topic_partition)
                   
        return topic_partitions
    
    def get_total_message_count(self):
        topic_partitions = self.get_topic_partition()
        end_offsets = self.consumer.end_offsets(topic_partitions)
        beginning_offsets = self.consumer.beginning_offsets(topic_partitions)
        total_message_count = MessageCountHandler(end_offsets, beginning_offsets).handle()
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