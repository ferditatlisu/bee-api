from typing import List
from src.services.kafkaserviceinterface import KafkaServiceInterface

class GetConsumerInfoHandler():
    def __init__(self, kafka_service : KafkaServiceInterface, group_id: str):
        self.kafka_service = kafka_service
        self.group_id = group_id

    def handle(self):    
        admin_client = self.kafka_service.get_admin_client()
        describes = admin_client.describe_consumer_groups([self.group_id])
        describe = describes[0]
        state = describe.state
        members = describe.members
        protocol = describe.protocol
        if protocol is None or protocol == '':
            protocol = "None"
            
        result = {
            'state' : state,
            'protocol': protocol,
            "member_count": len(members),
            'consumer_unassigments': [],
            'consumer_assigments': [],
            'all_ips': {}
        }
        
        if members:
            consumer_assigments = []
            possible_consumer_unassigments = []
            for member in members:
                ip_address = member.client_host
                result['all_ips'][ip_address] = 1
                assigments = self.get_assigment(member)
                if len(assigments) == 0:
                    possible_consumer_unassigments.append(ip_address)
                    continue
                
                for assigment in assigments:
                    topic_name = assigment[0]
                    partitions = assigment[1]
                    consumer_assigments.append({ 'ip_address': ip_address, 
                                                'topic_name': topic_name,
                                                'partitions': partitions})
            
            consumer_unassigments: List[str] = []
            for ip_address in possible_consumer_unassigments:
                if not self.ip_address_in_usage(ip_address, consumer_assigments):
                    consumer_unassigments.append(ip_address)
                
            result["consumer_assigments"] = consumer_assigments
            result["consumer_unassigments"] = consumer_unassigments
             
        result['pod_count'] = len(result['all_ips'])
        return result
    
    def get_assigment(self, member):
        try:
            member_assigment = member.member_assignment
            return member_assigment.assignment
        except Exception as _:
            return []

    
    
    def ip_address_in_usage(self, ip_address, usage_assigments: List):
        for consumer_assigment in usage_assigments:
            if ip_address == consumer_assigment['ip_address']:
                return True
             
        return False
                