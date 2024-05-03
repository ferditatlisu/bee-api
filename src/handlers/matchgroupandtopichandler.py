from src.services.redisservice import TOPIC_WITH_CONSUMER_GROUPS, RedisService
from src.services.kafkaserviceinterface import KafkaServiceInterface

class MatchGroupAndTopicHandler():
    def __init__(self, kafka_service : KafkaServiceInterface, redis_service: RedisService):
        self.kafka_service = kafka_service
        self.redis_service=redis_service
        
    def handle(self):    
        all_topics = {}
        all_groups = self.kafka_service.get_admin_client().list_consumer_groups()
        for group in all_groups:
            group_offsets = self.kafka_service.get_admin_client().list_consumer_group_offsets(group[0])
            for metadata, _ in group_offsets.items():
                topic_name = metadata[0]
                group_id = group[0]
                group_ids_of_topic = all_topics.get(topic_name, [])
                if group_id not in group_ids_of_topic:
                    group_ids_of_topic.append(group_id)
                    all_topics[topic_name] = group_ids_of_topic
                
        kafka_id = self.kafka_service.get_id()
        for topic, groups in all_topics.items():
            key = TOPIC_WITH_CONSUMER_GROUPS.format(kafka_id, topic)
            self.redis_service.save_topic_consumer(key, groups)


