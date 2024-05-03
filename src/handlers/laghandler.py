from typing import List
from src.exceptions.KafkaSearchException import KafkaSearchException
from src.handlers.lagofgrouphandler import LagOfGroupHandler
from src.services.kafkaserviceinterface import KafkaServiceInterface
from src.dto.topicdata import TopicData

class LagHandler():
    def __init__(self, stretch_kafka : KafkaServiceInterface, 
                 group_id : str,
                 topic_name):
        self.stretch_kafka = stretch_kafka
        self.group_id = group_id
        self.topic_name = topic_name
    
    def handle(self):
        topic_data: List[TopicData] = LagOfGroupHandler(self.stretch_kafka, self.group_id, self.topic_name).handle()
        if topic_data and len(topic_data):
            return { "lag": topic_data[0].total_lag}
        
        raise KafkaSearchException("Lag couldn't fetch from topic")
        
        
        
        

