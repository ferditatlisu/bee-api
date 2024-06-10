from threading import Thread
from typing import Set
from kafka import KafkaConsumer
from src.handlers.singlematchgroupandtopichandler import SingleMatchGroupAndTopicHandler
from src.services.kafkaserviceinterface import KafkaServiceInterface
from src.dto.offsettype import OffsetType
from src.handlers.getnewoffsethandler import GetNewOffsetHandler
from src.services.redisservice import RedisService
from src.handlers.groupcacheclearhandler import GroupCacheClearHandler

class ChangeOffsetOfGroupHandler():
    def __init__(self, kafka_service: KafkaServiceInterface, redis_service: RedisService, group_id: str,
                 topic_name: str, offset_type: OffsetType, value, partitions_to_update: Set[int] = None):
        self.kafka_service = kafka_service
        self.redis_service = redis_service
        self.group_id=group_id
        self.topic_name=topic_name
        self.offset_type: OffsetType = offset_type
        self.value = value
        self.partitions_to_update = partitions_to_update

    def handle(self):
        consumer, offsets = GetNewOffsetHandler(self.kafka_service, self.group_id, self.topic_name,
                                                self.offset_type, self.value, self.partitions_to_update).handle()

        return self.return_state(consumer, offsets)
        
    def update_topic_group_match(self):
        def background():
            GroupCacheClearHandler(self.kafka_service, self.redis_service).handle()
            SingleMatchGroupAndTopicHandler(self.kafka_service, self.redis_service, self.topic_name, self.group_id).handle()

        thread = Thread(target=background)
        thread.start()
        
    
    def return_state(self, consumer: KafkaConsumer, offsets):
        try:
            if offsets != {}:
                consumer.commit(offsets)
                consumer.close()
                self.update_topic_group_match()
            else:
                return {'message' : 'Not found offset', 'is_success' : False}
        except Exception as ex:
            return {'message' : ex.args[0], 'is_success' : False}
        
        return {'message' : 'Success', 'is_success' : True}   