from kafka.admin import ConfigResource
from src.services.kafkaserviceinterface import KafkaServiceInterface

class UpdateTopicConfigurationHandler():
    def __init__(self, kafka_service : KafkaServiceInterface,
                 topic_name: str,
                 key: str,
                 value):
        self.kafka_service = kafka_service
        self.topic_name = topic_name
        self.key = key
        self.value= value
        
    def handle(self):
        admin_client = self.kafka_service.get_admin_client()
        res = ConfigResource(resource_type='TOPIC', name=self.topic_name, configs={self.key: self.value})
        res = admin_client.alter_configs(config_resources=[res])
        if res.resources[0][0] != 0:
            raise Exception(res.resources[0][1])
        
        return {}
        