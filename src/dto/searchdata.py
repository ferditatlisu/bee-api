import json
from typing import Dict, Optional

class SearchData:
    topic_name : str
    value : str
    
    def __init__(self, dict: Dict):
        self.topic_name = dict.get("topicName", None)
        self.value = dict.get("value", None)
        self.key = f"{self.topic_name}v-{self.value}"
        
        if dict.get("startDate", None):
            self.start_date = int(dict.get("startDate", None))
        if dict.get("endDate", None):
            self.end_date = int(dict.get("endDate", None))
            
        if dict.get("valueType", None):
            self.value_type = int(dict.get("valueType", None))
        
    def to_json(self):
        return json.dumps(self.__dict__)