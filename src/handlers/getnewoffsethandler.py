from typing import List
from kafka import KafkaConsumer
from kafka.structs import TopicPartition, OffsetAndMetadata
from src.exceptions.ChangeOffsetValueEmptyException import ChangeOffsetValueEmptyException
from src.services.kafkaservice import KafkaService
from src.dto.offsettype import OffsetType
from src.services.kafkaserviceinterface import KafkaServiceInterface

class GetNewOffsetHandler():
    def __init__(self, kafka_service : KafkaServiceInterface, group_id : str, topic_name: str, offset_type: OffsetType, value):
        self.kafka_service = kafka_service
        self.group_id=group_id
        self.topic_name=topic_name
        self.offset_type: OffsetType = offset_type
        self.value = int(value) if value else None
        
    def handle(self):    
        consumer = self.kafka_service.create_consumer_with_group_id(self.group_id)   
        topic_partitions = self.get_topic_partitions(consumer)             
        consumer.assign(topic_partitions)
        offsets = self.get_offset(consumer, topic_partitions)
        return consumer, offsets
        
    def by_offset(self, topic_partitions):
        if not self.value:
            raise ChangeOffsetValueEmptyException()
        
        offmeta = OffsetAndMetadata(self.value, '')
        offset = {}
        for topic_partition in topic_partitions:
            offset[topic_partition] = offmeta
            
        return offset

    def by_timestamp(self, consumer: KafkaConsumer, topic_partitions):
        if not self.value:
            raise ChangeOffsetValueEmptyException()
        
        timestamps = {}
        for topic_partition in topic_partitions:
            timestamps[topic_partition] = self.value
            
        offset ={}
        offset_timestamps = consumer.offsets_for_times(timestamps)
        if offset_timestamps:
            for topic_partition, timestamp in offset_timestamps.items():
                if timestamp:
                    offmeta = OffsetAndMetadata(timestamp.offset, '')
                else:
                    end_offset = consumer.end_offsets([topic_partition])
                    if not end_offset:
                        continue
                    
                    offmeta = OffsetAndMetadata(end_offset[topic_partition], '')
                        
                offset[topic_partition] = offmeta
            
        return offset
    
    def by_end(self, consumer: KafkaConsumer, topic_partitions):
        offsets = {}
        end_topic_partitions = consumer.end_offsets(topic_partitions)
        if end_topic_partitions:
            for topic_partition in topic_partitions:
                offset = end_topic_partitions[topic_partition]
                offmeta = OffsetAndMetadata(offset, '')
                offsets[topic_partition] = offmeta
                
        return offsets;
    
    def by_beginning(self, consumer: KafkaConsumer, topic_partitions):
        offsets = {}
        beginning_topic_partitions = consumer.beginning_offsets(topic_partitions)
        if beginning_topic_partitions:
            for topic_partition in topic_partitions:
                offset = beginning_topic_partitions[topic_partition]
                offmeta = OffsetAndMetadata(offset, '')
                offsets[topic_partition] = offmeta
        
        return offsets;
    
    def get_offset(self, consumer: KafkaConsumer, topic_partitions: List[TopicPartition]):
        offsets = {}        
        match self.offset_type:
            case OffsetType.BEGINNING:
                offsets = self.by_beginning(consumer, topic_partitions);
            case OffsetType.END:
                offsets = self.by_end(consumer, topic_partitions);
            case OffsetType.SHIFTBY:
                offsets = self.by_offset(topic_partitions)
            case OffsetType.DATE:
                offsets = self.by_timestamp(consumer, topic_partitions)
                
        return offsets;
    
    def get_topic_partitions(self, consumer: KafkaConsumer):
        topic_partitions: List[TopicPartition] = []        
        partitions = consumer.partitions_for_topic(self.topic_name)
        if partitions:
            for partition in partitions:
                topic_partitions.append(TopicPartition(self.topic_name, partition))
                
        return topic_partitions
