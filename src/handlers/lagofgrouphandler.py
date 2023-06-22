from typing import List
from kafka.structs import TopicPartition

from src.dto.topicdata import TopicData
from src.services.kafkaserviceinterface import KafkaServiceInterface

class LagOfGroupHandler():
    def __init__(self, stretch_kafka : KafkaServiceInterface, 
                 group_id : str,
                 topic_name):
        self.stretch_kafka = stretch_kafka
        self.group_id = group_id
        self.topic_name = topic_name
    
    def handle(self):
        admin_client = self.stretch_kafka.get_admin_client()
        consumer = self.stretch_kafka.get_consumer()
        group_topics : List[TopicData] = []
        group_offsets = admin_client.list_consumer_group_offsets(self.group_id)
        for topic_key, value in group_offsets.items():   
            topic_data = self.get_topic_data(group_topics, topic_key.topic)
            if topic_data:
                topic_data.add_partition(topic_key.partition, value.offset) 
        
        topic_partitions = []
        for topic_data in group_topics:
            for partition in topic_data.partitions:
                topic_partition = TopicPartition(topic_data.topic_name, partition["partition"])
                topic_partitions.append(topic_partition)
        
        if len(topic_partitions) == 0:
            return None
        
        end_offsets = consumer.end_offsets(topic_partitions)
        if end_offsets:
            for topic_partition, highwater in end_offsets.items():
                topic_data = self.get_topic_data(group_topics, topic_partition[0])
                if topic_data:
                    topic_data.add_topic_offset(topic_partition[1], highwater)
            
        for topic_data in group_topics:
            topic_data.calculate_total_lag()
            
        return group_topics

    def get_topic_data(self, topic_data_list : List[TopicData], topic_name):
        for topic_data in topic_data_list:
            if topic_data.topic_name == topic_name:
                return topic_data
        
        if self.topic_name is None or (self.topic_name and topic_name == self.topic_name):
            topic_data = TopicData(topic_name, self.group_id)
            topic_data_list.append(topic_data)
            return topic_data
            
        return None