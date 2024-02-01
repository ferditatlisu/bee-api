from src.services.kafkaserviceinterface import KafkaServiceInterface
from kafka.admin.new_partitions import NewPartitions

class ChangePartitionCount():
    def __init__(self, kafka_service : KafkaServiceInterface, topic: str, count: int):
        self.kafka_service = kafka_service
        self.topic = topic
        self.count = int(count)
        
    def handle(self):
        admin_client = self.kafka_service.get_admin_client()
        admin_client.create_partitions({
            self.topic : NewPartitions(self.count)
        })
        
        return {}
    