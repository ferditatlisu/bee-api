from kafka import KafkaConsumer
from kafka.structs import TopicPartition
from src.util.util import prepare_event_message
from src.services.kafkaserviceinterface import KafkaServiceInterface
from src.handlers.messagecounthandler import MessageCountHandler

class GetTopMessageHandler():
    def __init__(self, kafka_service : KafkaServiceInterface, topic_name : str, size : str, partition):
        self.kafka_service = kafka_service
        self.topic_name=topic_name
        self.size=int(size)
        self.partition = partition
        self.consumer: KafkaConsumer = kafka_service.create_consumer()
        
    def get_topic_partition(self):
        topic_partitions = []
        if not self.partition:
            partitions = self.consumer.partitions_for_topic(self.topic_name)
            if partitions:
                for partition in partitions:
                    topic_partition = TopicPartition(self.topic_name, partition)
                    topic_partitions.append(topic_partition)
        
        if self.partition:
            topic_partitions.append(TopicPartition(self.topic_name, int(self.partition)))
                    
        return topic_partitions

        
    def handle(self):    
        topic_partitions = self.get_topic_partition()
        self.consumer.assign(topic_partitions)
        end_offsets = self.consumer.end_offsets(topic_partitions)
        beginning_offsets = self.consumer.beginning_offsets(topic_partitions)
        offsets = self.get_offsets(topic_partitions, end_offsets, beginning_offsets)
        total_message_count = MessageCountHandler(end_offsets, beginning_offsets).handle()
        for topic_partition in topic_partitions:
            offset = offsets[topic_partition.partition]
            self.consumer.seek(topic_partition, offset)

        messages = []
        while True:
            msgs = self.consumer.poll(2000, self.size, False)
            if len(msgs) == 0:
                break
            
            for _, msgs in msgs.items():
                for msg in msgs:
                    if len(messages) >= self.size:
                        break
                    
                    m = prepare_event_message(msg)
                    messages.append(m)
                        
            if len(messages) >= self.size or len(messages) >= total_message_count:
                break
        
        self.consumer.unsubscribe()
        self.consumer.close()
        messages.sort(key=lambda x: x['publish_date_utc'], reverse=True)
        return messages


    def get_offsets(self, topic_partitions, end_offsets, beginning_offsets):
        end_messages = {}
        begin_messages = {}
        
        if end_offsets:
            for topic_partition, hw in end_offsets.items():
                end_messages[topic_partition.partition] = hw
                
        if beginning_offsets:
            for topic_partition, hw in beginning_offsets.items():
                begin_messages[topic_partition.partition] = hw
                
        index = 0
        for _ in range(0, self.size):
            for key, _ in end_messages.items():
                end_offset = end_messages[key]
                begin_offset = begin_messages[key]
                
                if end_offset > begin_offset:
                    end_messages[key] = end_offset-1
                    index +=1
                    if index == self.size:
                        break
            
            if index == self.size:
                break
        
        return end_messages