from kafka.structs import TopicPartition
from src.services.kafkaserviceinterface import KafkaServiceInterface

from src.handlers.getnewoffsethandler import GetNewOffsetHandler
from src.dto.offsettype import OffsetType
from src.services.kafkaservice import KafkaService
from src.handlers.lagofgrouphandler import LagOfGroupHandler

class SimulationOfChangeOffsetHandler():
    def __init__(self, 
                 kafka_service : KafkaServiceInterface, 
                 group_id : str,
                 topic_name,
                 offset_type: OffsetType, value):
        self.kafka_service = kafka_service
        self.group_id = group_id
        self.topic_name = topic_name
        self.offset_type: OffsetType = offset_type
        self.value = value
    
    def handle(self):
        current = LagOfGroupHandler(self.kafka_service, self.group_id, self.topic_name).handle()
        if not current:
            return self.create_response(0, [])
            
        _, simulation_offset = GetNewOffsetHandler(self.kafka_service, self.group_id, self.topic_name, self.offset_type, self.value).handle()
        simulation_partition_data = []
        change_lag = 0
        if len(current)> 0 and len(current[0].partitions):
            for partition_data in current[0].partitions:
                new_offset = simulation_offset[TopicPartition(self.topic_name, partition_data['partition'])].offset
                topic_offset = partition_data['topic_offset']
                partition_id = partition_data['partition']
                exist_offset = partition_data['group_offset']
                exist_lag = partition_data['lag']
                new_lag = topic_offset - new_offset
                data = {'id' : partition_id, 'topic_offset': topic_offset, 'exist_offset': exist_offset, 'new_offset': new_offset,
                        'exist_lag': exist_lag, 'new_lag': new_lag }
                
                change_lag += (new_lag - exist_lag)
                
                simulation_partition_data.append(data)
        
        simulation_data = self.create_response(change_lag, simulation_partition_data)
        
        
        return simulation_data
    
    
    def create_response(self, change_lag: int, partitions):
        return {'topic_name': self.topic_name, 'group_id': self.group_id, 'change': change_lag, 'partitions': partitions}