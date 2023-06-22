from src.services.redisservice import RedisService

class ClearHandler():
    def __init__(self, redis: RedisService, id : str):
        self.redis = redis
        self.id = id
        
    def handle(self):
        self.redis.delete(self.id)