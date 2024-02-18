import json
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Redis:
    host: List[str]
    port: int | str
    password: str
    database: int | str
    masterName: str

@dataclass
class Master:
    copy : str
    search : str   
    partition: str
    delete: str 
    
@dataclass
class KafkaConfig:
    id : int
    name :str
    host: str
    userName: None | str
    password: None | str
    certificate: None | List[str]

@dataclass
class ApplicationConfig:
    port : int
    redis : Redis
    master: Master
    kafka_configs: None | List[KafkaConfig]