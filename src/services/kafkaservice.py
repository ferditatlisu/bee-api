import datetime
import time
from threading import Thread
from typing import Dict
from src.services.securekafkaservice import SecureKafkaService
from src.services.unsecurekafkaservice import UnsecureKafkaService
from src.services.kafkaserviceinterface import KafkaServiceInterface
from src.configs.config import get_config
from src.configs.applicationconfig import KafkaConfig
from src.services.redisservice import RedisService
from src.services.cacheservice import CacheService

class KafkaService():    
    kafka_clusters : Dict[int, KafkaServiceInterface] = {}
    
    def __init__(self, redis: RedisService):
        self.redis = redis
        print("Kafka service tries to connect")
        self.create_connections()
        print("Kafka service connected")
    
    def create_connections(self):
        kafka_configs = get_config().kafka_configs
        for kafka_config in kafka_configs:
            thread = Thread(target=self.create_connection, args=(kafka_config,))
            thread.start()

    def get_kafka_cluster(self, kafka_id: int):
        return self.kafka_clusters[kafka_id]
    
    def create_connection(self, kafka_config: KafkaConfig):
        while True:
            try:
                print(f"{kafka_config.name} kafka service is trying to connection || {datetime.datetime.now()}")
                if kafka_config.certificate and len(kafka_config.certificate) > 0:
                    self.kafka_clusters[kafka_config.id] = SecureKafkaService(kafka_config)
                else:
                    self.kafka_clusters[kafka_config.id] = UnsecureKafkaService(kafka_config)
                    
                print(f"{kafka_config.name} kafka service connection created || {datetime.datetime.now()}")
                CacheService(self.kafka_clusters[kafka_config.id], self.redis)
                break
            except Exception as ex:
                print(f"{kafka_config.name} Couldn't create kafka service {ex} || {datetime.datetime.now()}")