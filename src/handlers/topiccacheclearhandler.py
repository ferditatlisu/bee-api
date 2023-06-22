from src.services.kafkaserviceinterface import KafkaServiceInterface
from src.services.redisservice import ALL_TOPICS_BY_ID, RedisService
from src.handlers.getalltopichandler import GetAllTopicHandler


class TopicCacheClearHandler:
    def __init__(self, kafka_service: KafkaServiceInterface, redis_service: RedisService):
        self.kafka_service = kafka_service
        self.redis_service = redis_service
        self.kafka_id = self.kafka_service.get_id()
    def handle(self):
        topics = GetAllTopicHandler(self.kafka_service, self.redis_service, False).handle()
        if topics and len(topics) > 0:
            self.redis_service.delete(ALL_TOPICS_BY_ID.format(self.kafka_id))
            self.redis_service.set_topics(self.kafka_id, topics)

        print("cache removed")