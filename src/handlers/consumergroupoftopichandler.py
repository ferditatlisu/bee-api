from typing import List
from src.services.kafkaserviceinterface import KafkaServiceInterface

from src.services.redisservice import TOPIC_WITH_CONSUMER_GROUPS, RedisService
from src.services.kafkaservice import KafkaService
from src.handlers.lagofgrouphandler import LagOfGroupHandler
from src.dto.topicdata import TopicData


class ConsumerGroupOfTopicHandler:
    def __init__(self, kafka_service: KafkaServiceInterface, redis_service: RedisService, topic_name: str):
        self.kafka_service = kafka_service
        self.redis_service = redis_service
        self.topic_name = topic_name

    def handle(self):
        kafka_id = self.kafka_service.get_id()
        cache_key = TOPIC_WITH_CONSUMER_GROUPS.format(kafka_id, self.topic_name)
        groups = self.redis_service.get_result(cache_key)
        topic_data_list: List[TopicData] = []
        for group_id in groups:
            if not self.has_group(group_id, topic_data_list):    
                topic_data = LagOfGroupHandler(self.kafka_service, group_id.decode("utf-8"), self.topic_name).handle()
                if topic_data:
                    topic_data_list.append(topic_data[0])

        return topic_data_list
    
    
    def has_group(self, group_id, topic_data_list):
        g_id = group_id.decode('utf-8')
        for topic_data in topic_data_list:
            if topic_data.group_id == g_id:
                return True
            
        return False
