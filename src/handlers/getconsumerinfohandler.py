from typing import Any, Dict, List

from kafka.admin import ConfigResource, ConfigResourceType, KafkaAdminClient
from kafka.protocol.admin import DescribeConfigsResponse
from kafka.structs import TopicPartition

from src.configs.config import get_config
from src.services.kafkaservice import KafkaService
from src.services.kafkaserviceinterface import KafkaServiceInterface

class GetConsumerInfoHandler():
    def __init__(self, kafka_service : KafkaServiceInterface, group_id: str):
        self.kafka_service = kafka_service
        self.group_id = group_id

    def handle(self):    
        admin_client = self.kafka_service.get_admin_client()
        describes = admin_client.describe_consumer_groups([self.group_id])
        describe = describes[0]
        state = describe.state
        result = {
            'state' : state
        }
        members = describe.members
        if members:
            result["member_count"] = len(members)
            
        return result
    