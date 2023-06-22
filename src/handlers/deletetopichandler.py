from threading import Thread
from src.handlers.topiccacheclearhandler import TopicCacheClearHandler
from src.services.redisservice import RedisService
from src.services.kafkaserviceinterface import KafkaServiceInterface

class DeleteTopicHandler():
    def __init__(self, kafka_service : KafkaServiceInterface, redis_service: RedisService, topic: str):
        self.kafka_service = kafka_service
        self.redis_service = redis_service
        self.topic = topic
        
    def handle(self):
        admin_client = self.kafka_service.get_admin_client()
        admin_client.delete_topics(topics=[self.topic])
        self.update_topics()
        return {}
    
    def update_topics(self):
        def background():
            TopicCacheClearHandler(self.kafka_service, self.redis_service).handle()
            
        thread = Thread(target=background)
        thread.start()