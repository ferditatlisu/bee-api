from typing import Any, Dict, List

from kafka.admin import ConfigResource, ConfigResourceType, KafkaAdminClient
from kafka.protocol.admin import DescribeConfigsResponse
from kafka.structs import TopicPartition

from src.configs.config import get_config
from src.services.kafkaservice import KafkaService
from src.services.kafkaserviceinterface import KafkaServiceInterface

class GetTopicConfigurationHandler():
    def __init__(self, kafka_service : KafkaServiceInterface, topic: str):
        self.kafka_service = kafka_service
        self.topic = topic
        
    def handle(self):
        admin_client = self.kafka_service.get_admin_client()
        configs = admin_client.describe_configs(config_resources=[ConfigResource(ConfigResourceType.TOPIC, self.topic)])
        config_list = configs[0].resources[0][4]
        configs = []
        for config in config_list:
            v = {config[0] : config[1]}
            configs.append(v)
            
        return configs