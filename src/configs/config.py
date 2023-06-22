import json
import os
from typing import Dict
from dacite import from_dict
import yaml
from src.configs.applicationconfig import ApplicationConfig, KafkaConfig

class ConfigurationManager:
    config : ApplicationConfig
    def __init__(self):
        with open(f'resources/application.json') as f:
            data = json.load(f)
            data = self.update_config(data)
            self.config = from_dict(data_class=ApplicationConfig, data= data)
            
        self.update_kafka_config()
            
            
    def update_kafka_config(self):
        self.config.kafka_configs = []
        kafka_configs = os.getenv("KAFKA_CONFIGS", None)        
        kafka_configs_data = json.loads(kafka_configs)
        for kafka_config in kafka_configs_data:
            kafka = from_dict(data_class=KafkaConfig, data= kafka_config)
            self.config.kafka_configs.append(kafka)
            if kafka.certificate is None:
                continue
            
            with open(f"resources/{kafka.name}.pem", "w") as txt_file:
                for line in kafka.certificate:
                    txt_file.write(line + "\n")
    
    def get(self):
        return self.config    
    
    def update_config(self, data: Dict):
        master_url = os.getenv("MASTER_URL", None)
        data['master']['copy'] = f'{master_url}{data["master"]["copy"]}'
        data['master']['search'] = f'{master_url}{data["master"]["search"]}'
        data['master']['delete'] = f'{master_url}{data["master"]["delete"]}'
        
        redis_host: str = os.getenv("REDIS_HOST", "")
        data["redis"]["host"] = redis_host.strip().split(",")
        
        redis_password: str = os.getenv("REDIS_PASSWORD", "")
        data["redis"]["password"] = redis_password
        
        redis_mastername: str = os.getenv("REDIS_MASTERNAME", "")
        data["redis"]["masterName"] = redis_mastername
        
        redis_port = os.getenv("REDIS_PORT", 0)
        data["redis"]["port"] = redis_port
        
        redis_db = os.getenv("REDIS_DB", 0)
        data["redis"]["database"] = redis_db
        
        return data

cfg = ConfigurationManager()        

def get_config():
    return cfg.config

