from threading import Thread
import time
from src.handlers.cacheclearhandler import CacheClearHandler
from src.handlers.matchgroupandtopichandler import MatchGroupAndTopicHandler
from src.services.kafkaserviceinterface import KafkaServiceInterface
from src.services.redisservice import RedisService


class CacheService():
    def __init__(self, kafka_service: KafkaServiceInterface, redis_service: RedisService ) -> None:
        self.kafka_service = kafka_service
        self.redis_service = redis_service
        self.update_cache()
        
    def update_cache(self):
        def background():
            while True:
                try:
                    key = f"app_cache:{self.kafka_service.get_id()}" 
                    has_value = self.redis_service.get_app_cache(key)
                    if has_value is None:
                        self.redis_service.set_app_cache(key)
                        CacheClearHandler(self.kafka_service, self.redis_service).handle()
                        MatchGroupAndTopicHandler(self.kafka_service, self.redis_service).handle()
                except Exception as ex:
                    print('Error occured when cache was refreshing. ', ex)

                time.sleep(300)
                
            
        thread = Thread(target=background, args=())
        thread.start()