import json
import math
from kafka.structs import TopicPartition
from src.services.kafkaservice import KafkaService
from src.util.util import prepare_event_message
from src.services.kafkaserviceinterface import KafkaServiceInterface

class GetTopMessageHandler():
    def __init__(self, kafka_service : KafkaServiceInterface, topic_name : str, size : str, partition):
        self.kafka_service = kafka_service
        self.topic_name=topic_name
        self.size=int(size)
        self.partition = partition
        
    def get_topic_partition(self):
        consumer = self.kafka_service.get_consumer()
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
    
    def get_offset(self, partition_lenght: int):    
        plus = self.size % partition_lenght
        per_size = self.size // partition_lenght;
        per_size_list = []
        
        for _ in range(0, partition_lenght):
            number = per_size
            if plus > 0:
                number += 1
                plus -=1
            
            per_size_list.append(number)
        
        return per_size_list
        
    def handle(self):    
        consumer = self.kafka_service.get_consumer()    
        topic_partitions = self.get_topic_partition()
        consumer.assign(topic_partitions)
        end_offsets = consumer.end_offsets(topic_partitions)
        offsets = self.get_offset(len(topic_partitions))
        index = 0
        if end_offsets:
            for topic_partition, hw in end_offsets.items():
                offset = hw - offsets[index]
                if offset < 0:
                    offset = 0
                consumer.seek(topic_partition, offset)
                index +=1

        messages = []
        while True:
            msgs = consumer.poll(2000, self.size, False)
            if len(msgs) == 0:
                break
            
            for _, msgs in msgs.items():
                for msg in msgs:
                    if len(messages) >= self.size:
                        break
                    
                    m = prepare_event_message(msg)
                    messages.append(m)
                        
            if len(messages) >= self.size:
                break
        
        consumer.unsubscribe()
        messages.sort(key=lambda x: x['publish_date_utc'], reverse=True)
        return messages
