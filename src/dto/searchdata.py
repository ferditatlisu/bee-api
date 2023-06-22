import json
from typing import Dict, Optional

class SearchData:
    topic_name : str
    value : str
    
    def __init__(self, dict: Dict):
        self.topic_name = dict.get("topicName", None)
        self.value = dict.get("value", None)
        self.key = f"{self.topic_name}v-{self.value}"
        
    def to_json(self):
        return json.dumps(self.__dict__)