from abc import abstractmethod

from kafka import KafkaAdminClient

class KafkaServiceInterface():
    @abstractmethod
    def get_id(self):
        raise NotImplementedError()
    
    @abstractmethod
    def get_consumer(self):
        raise NotImplementedError()
    
    @abstractmethod
    def get_admin_client(self) -> KafkaAdminClient:
        raise NotImplementedError()
    
    @abstractmethod
    def get_producer(self, ):
        raise NotImplementedError()
    
    @abstractmethod
    def create_consumer(self):
        raise NotImplementedError()
    
    @abstractmethod
    def create_consumer_with_group_id(self, group_id):
        raise NotImplementedError()    
    
    @abstractmethod
    def publish(self, topic_name, key, value, headers):
        raise NotImplementedError()