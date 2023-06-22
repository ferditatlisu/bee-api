from src.services.redisservice import TOPIC_WITH_CONSUMER_GROUPS, RedisService
from src.services.kafkaserviceinterface import KafkaServiceInterface

class SingleMatchGroupAndTopicHandler():
    def __init__(self, kafka_service : KafkaServiceInterface, redis_service: RedisService, topic, group_id):
        self.kafka_service = kafka_service
        self.redis_service=redis_service
        self.topic = topic
        self.group_id = group_id
    def handle(self):    
        kafka_id = self.kafka_service.get_id()
        key = TOPIC_WITH_CONSUMER_GROUPS.format(kafka_id, self.topic)
        self.redis_service.add_topic_consumer(key, self.group_id)


