import json
from kafka import KafkaAdminClient, KafkaConsumer, KafkaProducer

from src.services.kafkaserviceinterface import KafkaServiceInterface
from src.configs.applicationconfig import KafkaConfig
from src.configs.config import get_config

class UnsecureKafkaService(KafkaServiceInterface):
    config: KafkaConfig
    consumer: KafkaConsumer
    admin_client : KafkaAdminClient
    producer: KafkaProducer
    
    def __init__(self, config: KafkaConfig):
        self.config = config
        self.consumer = self.create_consumer()
        self.admin_client = self.create_admin_client()
        self.producer = self.create_producer()
        
    def get_id(self):
        return self.config.id
        
    def get_consumer(self):
        return self.consumer

    def get_admin_client(self):
        return self.admin_client
    
    def get_producer(self):
        return self.producer

    def create_consumer(self):
        return KafkaConsumer(bootstrap_servers=self.config.host, 
                                      auto_offset_reset="earliest",
                                      consumer_timeout_ms=5000,
                                      enable_auto_commit=False)
        
    def create_admin_client(self):
        return KafkaAdminClient(bootstrap_servers=self.config.host)

    def create_consumer_with_group_id(self, group_id):
        return KafkaConsumer(bootstrap_servers=self.config.host, 
                                      auto_offset_reset="earliest",
                                      consumer_timeout_ms=25000,
                                      enable_auto_commit=False,
                                      group_id= group_id)
        
        
    def create_producer(self):
        return KafkaProducer(bootstrap_servers=self.config.host)

    def publish(self, topic_name, key, value, headers):
        if key:
            key=bytes(key, 'utf-8')
            
        json_value = json.loads(value)            
        self.producer.send(topic=topic_name, key=key, value=bytearray(json.dumps(json_value), "utf-8"), headers=headers)