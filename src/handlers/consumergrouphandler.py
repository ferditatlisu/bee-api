from typing import List
from src.handlers.lagofgrouphandler import LagOfGroupHandler
from src.services.kafkaserviceinterface import KafkaServiceInterface
from src.handlers.getconsumerinfohandler import GetConsumerInfoHandler

class ConsumerGroupHandler():
    def __init__(self, kafka_service : KafkaServiceInterface, group_id : str):
        self.kafka_service = kafka_service
        self.group_id=group_id
        
    def handle(self):
        topic_data_list = LagOfGroupHandler(self.kafka_service, self.group_id, None).handle()
        consumer_info = GetConsumerInfoHandler(self.kafka_service, self.group_id).handle()
        for topic_data in topic_data_list:
            assigments = consumer_info.get("consumer_assigments", None)
            if not assigments:
                continue
            
            for partition in topic_data.partitions:
                partition['ip_address'] = self.get_ip_address_of_partition(topic_data.topic_name, partition, assigments)
                
        return topic_data_list
    
    
    def get_ip_address_of_partition(self, topic_name:str, partition_data, assigments: List):
        for assigment in assigments:
            if assigment['topic_name'] != topic_name:
                continue
            
            for assigment_partition in assigment['partitions']:
                if assigment_partition == partition_data['partition']:
                    return assigment['ip_address']
                
                
        return ''