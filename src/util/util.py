import json
import json.decoder

from typing import Dict

from flask import Request
from src.dto.offsettype import OffsetType

def convert_to_offset_type(value: str):
    return  getattr(OffsetType, value)


def get_kafka_id_from_header(request : Request):
    kafka_id = request.headers.get('kafka-id', None)
    return int(kafka_id)


def prepare_kafka_header_from_string(headers_as_json: str | None):
    header_list = []
    if headers_as_json:   
        headers = json.loads(headers_as_json)
        for item in headers:
            key = tuple(item)[0]
            v = bytes(str(item[key]), 'utf-8')
            if (key, v) in header_list:
                continue
            
            header_list.append((key, v))
        
        return header_list
            
    return None


def prepare_headers_from_kafka_to_response(headers):
    if not headers: 
        return None
    
    header_list = []
    for item in headers:
        v = None
        if not item[1]:
            continue
        
        if 'x00' in str(item[1]):
            continue
        
        v = item[1].decode('UTF-8')
        if {item[0]: v} in header_list:
            continue
        
        header_list.append({item[0]: v})    
    
    return header_list


def prepare_event_message(event_message):
    m = {}
    value = json.loads(event_message.value)
    m['value'] = value
    m['offset'] = event_message.offset
    m['partition'] = event_message.partition
    m['publish_date_utc'] = event_message.timestamp
    m['key'] = event_message.key.decode("utf-8") if event_message.key is not None else None
    m['headers'] = prepare_headers_from_kafka_to_response(event_message.headers)
    
    return m