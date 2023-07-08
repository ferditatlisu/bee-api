class MessageCountHandler():
    def __init__(self, end_offsets, beginning_offsets):
        self.end_offsets = end_offsets
        self.beginning_offsets = beginning_offsets
        
    def handle(self):    
        messages = {}
        
        if self.end_offsets:
            for topic_partition, hw in self.end_offsets.items():
                messages[topic_partition.partition] = hw
        
        if self.beginning_offsets:
            for topic_partition, hw in self.beginning_offsets.items():
                messages[topic_partition.partition] -= hw
        
        total_message_count = 0
        for count in messages.values():
            total_message_count += count
            
        return total_message_count