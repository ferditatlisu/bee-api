from src.handlers.lagofgrouphandler import LagOfGroupHandler
from src.services.kafkaservice import KafkaService
from src.services.kafkaserviceinterface import KafkaServiceInterface

class ConsumerGroupHandler():
    def __init__(self, kafka_service : KafkaServiceInterface, group_id : str):
        self.kafka_service = kafka_service
        self.group_id=group_id
        
    def handle(self):
        topic_data_list = LagOfGroupHandler(self.kafka_service, self.group_id, None).handle()
        return topic_data_list