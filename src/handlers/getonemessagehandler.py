import json
from kafka import KafkaConsumer
from kafka.structs import TopicPartition, OffsetAndMetadata
from src.services.kafkaservice import KafkaService
from src.util.util import prepare_event_message
from src.services.kafkaserviceinterface import KafkaServiceInterface

class GetOneMessageHandler():
    def __init__(self,
                 kafka_service : KafkaServiceInterface, 
                 topic_name : str,
                 partition: str | int |None,
                 offset: str | None
                 ):
        self.kafka_service = kafka_service
        self.topic_name=topic_name
        self.partition = int(partition) if partition else None
        self.offset = offset
        
    def get_topic_partition(self, consumer: KafkaConsumer):
        topic_partitions = []
        if not self.partition:
            partitions = consumer.partitions_for_topic(self.topic_name)
            if partitions:
                for partition in partitions:
                    topic_partition = TopicPartition(self.topic_name, partition)
                    topic_partitions.append(topic_partition)
        
        if self.partition:
            topic_partitions.append(TopicPartition(self.topic_name, int(self.partition)))
                    
        return topic_partitions
            
            
    def from_last(self, consumer: KafkaConsumer, topic_partitions):
        end_offsets = consumer.end_offsets(topic_partitions)
        if end_offsets:
            for topic_partition, hw in end_offsets.items():
                offset = hw - 1
                if offset < 0:
                    offset = 0
                consumer.seek(topic_partition, offset)
        
    def from_offset(self, consumer: KafkaConsumer, topic_partitions):
        if not self.offset:
            return
        
        for topic_partition in topic_partitions:
            consumer.seek(topic_partition, int(self.offset))
            
    def handle(self):    
        consumer: KafkaConsumer = self.kafka_service.get_consumer()    
        topic_partitions = self.get_topic_partition(consumer)
        consumer.assign(topic_partitions)
        if self.offset:
            self.from_offset(consumer, topic_partitions)
        else:
            self.from_last(consumer, topic_partitions)

        msgs = consumer.poll(5000, 1, False)
        for _, msgs in msgs.items():
            for msg in msgs:
                m = prepare_event_message(msg)
                
                return m
            
        return {}