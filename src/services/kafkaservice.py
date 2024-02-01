from typing import Dict
from src.services.securekafkaservice import SecureKafkaService
from src.services.unsecurekafkaservice import UnsecureKafkaService
from src.services.kafkaserviceinterface import KafkaServiceInterface
from src.configs.config import get_config

class KafkaService():    
    kafka_clusters : Dict[int, KafkaServiceInterface] = {}
    
    def __init__(self):
        self.create_connections()
    
    
    def create_connections(self):
        try:
            kafka_configs = get_config().kafka_configs
            for kafka_config in kafka_configs:
                if kafka_config.certificate and len(kafka_config.certificate) > 0:
                    self.kafka_clusters[kafka_config.id] = SecureKafkaService(kafka_config)
                else:
                    self.kafka_clusters[kafka_config.id] = UnsecureKafkaService(kafka_config)
        except Exception as ex:
            self.create_connections()
    
    def get_kafka_cluster(self, kafka_id: int):
        return self.kafka_clusters[kafka_id]