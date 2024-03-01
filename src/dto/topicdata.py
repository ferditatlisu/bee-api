from typing import List

class TopicData():
    topic_name: str
    total_lag: int
    partitions: List
    group_id : str
    
    def __init__(self, topic_name, group_id):
        self.topic_name = topic_name
        self.group_id = group_id
        self.partitions = []
        self.total_lag = 0
    
    def add_partition(self, id, group_offset):
        self.partitions.append({'partition': id, 'group_offset': group_offset})
        
    def add_topic_offset(self, id, topic_offset):
        for partition_data in self.partitions:
            if id == partition_data['partition']:
                partition_data['topic_offset'] = topic_offset
                partition_data['lag'] = topic_offset - partition_data['group_offset']
                
    def calculate_total_lag(self):
        for partition_data in self.partitions:
            self.total_lag += partition_data.get('lag', 0)