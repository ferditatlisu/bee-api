from threading import Thread
from src.handlers.groupcacheclearhandler import GroupCacheClearHandler
from src.services.redisservice import RedisService
from src.services.kafkaserviceinterface import KafkaServiceInterface

class DeleteConsumerGroupHandler():
    def __init__(self, kafka_service : KafkaServiceInterface, redis_service: RedisService, group_id: str):
        self.kafka_service = kafka_service
        self.redis_service = redis_service
        self.group_id = group_id
        
    def handle(self):
        admin_client = self.kafka_service.get_admin_client()
        response = admin_client.delete_consumer_groups(group_ids=[self.group_id])
        if response[0][1].errno != 0:
            raise Exception(response[0][1].description)
        
        self.update_consumer_groups()
        return {}
    
    def update_consumer_groups(self):
        def background():
            GroupCacheClearHandler(self.kafka_service, self.redis_service).handle()
            
        thread = Thread(target=background)
        thread.start()
        