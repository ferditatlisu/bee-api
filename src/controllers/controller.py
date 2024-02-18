import json
from threading import Thread
from typing import Dict
from flask import Flask, redirect, request, jsonify
from src.handlers.updatetopicconfigurationhandler import UpdateTopicConfigurationHandler
from src.handlers.getcopyeventhandler import GetCopyEventHandler
from src.handlers.copyeventhandler import CopyEventHandler
from src.handlers.matchgroupandtopichandler import MatchGroupAndTopicHandler
from src.handlers.changeoffsetofgrouphandler import ChangeOffsetOfGroupHandler
from src.handlers.consumergrouphandler import ConsumerGroupHandler
from src.handlers.consumergroupoftopichandler import ConsumerGroupOfTopicHandler
from src.handlers.parametervalidationhandler import ParameterValidationHandler
from src.services.redisservice import RedisService
from src.handlers.startsearchhandler import StartSearchHandler
from src.handlers.getalltopichandler import GetAllTopicHandler
from src.services.kafkaservice import KafkaService
from src.handlers.getallconsumergroupshandler import GetAllConsumerGroupsHandler
from src.handlers.gettopmessagehandler import GetTopMessageHandler
from src.handlers.getonemessagehandler import GetOneMessageHandler
from src.handlers.gettopicconfigurationhandler import GetTopicConfigurationHandler
from src.handlers.gettopicinfohandler import GetTopicInfoHandler
from src.handlers.getconsumerinfohandler import GetConsumerInfoHandler
from src.util.util import convert_to_offset_type, get_kafka_id_from_header, prepare_kafka_header_from_string
from src.handlers.simulationofchangeoffsethandler import SimulationOfChangeOffsetHandler
from src.handlers.cacheclearhandler import CacheClearHandler
from src.exceptions.KafkaSearchException import KafkaSearchException
from src.handlers.deletecopyeventhandler import DeleteCopyEventHandler
from src.handlers.deletesearchhandler import DeleteSearchHandler
from src.services.kafkaserviceinterface import KafkaServiceInterface
from src.configs.config import get_config
from src.handlers.deleteconsumergrouphandler import DeleteConsumerGroupHandler
from src.handlers.deletetopichandler import DeleteTopicHandler
from src.handlers.changepartitioncounthandler import ChangePartitionCount
from src.handlers.deletepartitiondistributehandler import DeletePartitionDistributeHandler
from src.handlers.getpartitiondistributehandler import GetPartitionDistributeHandler
from src.handlers.partitiondistributehandler import PartitionDistributeHandler

class SearchController():
    def __init__(self):
        self.redis_service = RedisService()
        self.kafka_service = KafkaService()

def controller_initialize(app: Flask, controller: SearchController):
    @app.errorhandler(Exception) 
    def handle_error(error):
        print('Error occured when request was processing. ', str(error))
        return {'message' : str(error)}, 500
    
    @app.route("/test")
    def test_endpoint():
        kafka_id = get_kafka_id_from_header(request)
        cluster = controller.kafka_service.get_kafka_cluster(kafka_id)
        consumer = cluster.get_consumer()
        topics = consumer.topics()
        print(topics)
        
    
    @app.route("/")
    def index():
        return redirect('/swagger/index.html')
    
    @app.route("/kafka-cluster")
    def kafka_cluster():
        configs = []
        for kafka_config in get_config().kafka_configs:
             c = {'id': kafka_config.id, 'name': kafka_config.name}
             configs.append(c)
        
        return configs
    
    @app.route('/search', methods = ['GET'])
    def search():
        query_parameters = request.args.to_dict()
        validation = ParameterValidationHandler(query_parameters)
        is_valid = validation.handle()
        if not is_valid:
            raise Exception('topicName or value is empty')
        
        kafka_id = get_kafka_id_from_header(request)
        handler = StartSearchHandler(kafka_id, controller.redis_service, 
                                     query_parameters)
        
        res = handler.handle()
        return res
    
    @app.route('/search', methods = ['DELETE'])
    def delete_search(): 
        query_parameters = request.args.to_dict()
        validation = ParameterValidationHandler(query_parameters)
        is_valid = validation.handle()
        if not is_valid:
            return { 'message' : "topicName or (key or value) is empty"}
        
        handler = DeleteSearchHandler(controller.redis_service, 
                                     query_parameters)
        
        res = handler.handle()
        return res
    
    
    @app.route('/topics', methods = ['GET'])
    def topics():
        kafka_service = controller.kafka_service.get_kafka_cluster(get_kafka_id_from_header(request))
        handler = GetAllTopicHandler(kafka_service, controller.redis_service, True)
        return handler.handle()
    
    
    @app.route('/consumer-group-by-topic', methods = ['GET'])
    def consumer_by_topic():
        kafka_service = controller.kafka_service.get_kafka_cluster(get_kafka_id_from_header(request))
        query_parameters = request.args.to_dict()
        handler = ConsumerGroupOfTopicHandler(kafka_service,
                                        controller.redis_service,
                                        query_parameters["topic"])
        
        response = []
        topic_data_list = handler.handle()
        for topic_data in topic_data_list:
            response.append(topic_data.__dict__)

        return response
    
    @app.route('/consumer-group-by-group-id', methods = ['GET'])
    def consumer_by_group_id():
        kafka_service = controller.kafka_service.get_kafka_cluster(get_kafka_id_from_header(request))
        query_parameters = request.args.to_dict()
        handler = ConsumerGroupHandler(kafka_service,
                                       query_parameters["group_id"])
        
        response = []
        topic_data_list = handler.handle()
        for topic_data in topic_data_list:
            response.append(topic_data.__dict__)

        return response
    
    
    @app.route('/consumers', methods = ['GET'])
    def consumers():
        kafka_service = controller.kafka_service.get_kafka_cluster(get_kafka_id_from_header(request))
        handler = GetAllConsumerGroupsHandler(kafka_service, controller.redis_service, True)
        return handler.handle()
    
    
    
    @app.route('/get-top-messages', methods = ['GET'])
    def get_top_messages():
        query_parameters = request.args.to_dict()
        kafka_service = controller.kafka_service.get_kafka_cluster(get_kafka_id_from_header(request))
        
        handler = GetTopMessageHandler(kafka_service, 
                                       query_parameters["topic"],
                                       query_parameters.get("size", "10"),
                                       query_parameters.get("partition", None))
        
        return handler.handle()
    
    @app.route('/get-message', methods = ['GET'])
    def get_message():
        kafka_service = controller.kafka_service.get_kafka_cluster(get_kafka_id_from_header(request))
        query_parameters = request.args.to_dict()
        handler = GetOneMessageHandler(kafka_service, 
                                       query_parameters["topic"],
                                       query_parameters.get("partition", None),
                                       query_parameters.get("offset", None))
        
        return handler.handle()
    
    @app.route('/get-topic-info', methods = ['GET'])
    def get_topic_info():
        query_parameters = request.args.to_dict()
        
        kafka_service = controller.kafka_service.get_kafka_cluster(get_kafka_id_from_header(request))
        handler = GetTopicInfoHandler(kafka_service, 
                                       query_parameters["topic"])
        
        return handler.handle()
        
    @app.route('/get-topic-configuration', methods = ['GET'])
    def get_topic_configuration():
        query_parameters = request.args.to_dict()
        
        kafka_service = controller.kafka_service.get_kafka_cluster(get_kafka_id_from_header(request))
        handler = GetTopicConfigurationHandler(kafka_service, 
                                       query_parameters["topic"])
        
        return handler.handle()

    @app.route('/get-consumer-info', methods = ['GET'])
    def get_consumer_info():
        kafka_service = controller.kafka_service.get_kafka_cluster(get_kafka_id_from_header(request))
        query_parameters = request.args.to_dict()
        
        handler = GetConsumerInfoHandler(kafka_service, 
                                       query_parameters["group_id"])
        
        return handler.handle()
    
    @app.route('/put-change-offset', methods = ['PUT'])
    def put_change_offset():
        kafka_service = controller.kafka_service.get_kafka_cluster(get_kafka_id_from_header(request))
        body: Dict = json.loads(request.data)
        handler = ChangeOffsetOfGroupHandler(kafka_service,
                                        controller.redis_service, 
                                        body["group_id"],
                                        body["topic_name"],
                                        convert_to_offset_type(body["offset_type"]),
                                        body.get("value", None))
        
        return handler.handle()
        
    @app.route('/get-simulation-change-offset', methods = ['GET'])
    def get_simulation_change_offset():
        kafka_service = controller.kafka_service.get_kafka_cluster(get_kafka_id_from_header(request))
        query_parameters = request.args.to_dict()
        handler = SimulationOfChangeOffsetHandler(kafka_service, 
                                       query_parameters["group_id"],
                                       query_parameters["topic_name"],
                                       convert_to_offset_type(query_parameters["offset_type"]),
                                       query_parameters.get("value", None))
        
        return handler.handle()
    
    
    @app.route('/get-match-topic-and-groups-job', methods = ['GET'])
    def get_match_topic_and_groups_job():
        def background(kafka_service: KafkaServiceInterface):
            MatchGroupAndTopicHandler(kafka_service, controller.redis_service).handle()

        for kafka_id, kafka_service in controller.kafka_service.kafka_clusters.items():
            thread = Thread(target=background, args=(kafka_service,))
            thread.start()
        
        return {}
        
        
    @app.route('/cache-clear', methods = ['GET'])
    def get_cache_clear():
        def background(kafka_service: KafkaServiceInterface):
            CacheClearHandler(kafka_service, controller.redis_service).handle()

        for kafka_id, kafka_service in controller.kafka_service.kafka_clusters.items():
            thread = Thread(target=background, args=(kafka_service,))
            thread.start()
        
        return {}
    
    @app.route('/<topic>/publish-message', methods = ['POST'])
    def post_publish_message(topic):     
        if not request.view_args:
            raise KafkaSearchException("request empty")
        
        topic_name = request.view_args.get('topic', None)
        if not topic_name:
            raise KafkaSearchException("topic can not be empty")
        
        key = request.args.to_dict().get("key", None) 
        headers = request.headers.get('headers', None)
        header_list = prepare_kafka_header_from_string(headers)     
        
        kafka_id = get_kafka_id_from_header(request)
        cluster = controller.kafka_service.get_kafka_cluster(kafka_id)       
        cluster.publish(topic_name, key, request.data, header_list)
        
        return {}
        
        
    @app.route('/copy-event', methods = ['POST'])
    def post_copy_event():
        data = json.loads(request.data)
        handler = CopyEventHandler(controller.redis_service,
                                       data["fromTopic"],
                                       data["fromId"],
                                       data["toTopic"],
                                       data["toId"])
        
        return handler.handle()
    
    @app.route('/copy-event', methods = ['GET'])
    def get_copy_event():
        queries = request.args.to_dict();
        from_topic = queries.get("fromTopic", None)
        to_topic = queries.get("toTopic", None)
        if from_topic is None or to_topic is None:
            raise Exception("Parameter is null")
        
        handler = GetCopyEventHandler(controller.redis_service, from_topic, to_topic)
        
        return handler.handle()
    
    
    @app.route('/copy-event', methods = ['DELETE'])
    def delete_copy_event():
        queries = request.args.to_dict();
        from_topic = queries.get("fromTopic", None)
        to_topic = queries.get("toTopic", None)
        if from_topic is None or to_topic is None:
            raise Exception("Parameter is null")
        
        handler = DeleteCopyEventHandler(controller.redis_service,
                                       from_topic,
                                       to_topic)
        
        return handler.handle()
    
    
    @app.route('/consumers', methods = ['DELETE'])
    def delete_consumer():
        kafka_service = controller.kafka_service.get_kafka_cluster(get_kafka_id_from_header(request))
        group_id = request.args.get('id', None)
        handler = DeleteConsumerGroupHandler(kafka_service, controller.redis_service, group_id)
        return handler.handle()
    
    @app.route('/topics', methods = ['DELETE'])
    def delete_topic():
        kafka_service = controller.kafka_service.get_kafka_cluster(get_kafka_id_from_header(request))
        topic = request.args.get('topic', None)
        handler = DeleteTopicHandler(kafka_service, controller.redis_service, topic)
        return handler.handle()
    
    @app.route('/<topic>/topic-configuration', methods = ['PUT'])
    def put_topic_configuration(topic):
        kafka_service = controller.kafka_service.get_kafka_cluster(get_kafka_id_from_header(request))
        body: Dict = json.loads(request.data)
        topic_name = request.view_args.get('topic', None)
        handler = UpdateTopicConfigurationHandler(kafka_service,
                                        topic_name,
                                        body["key"],
                                        body["value"])
        
        return handler.handle()
    
    
    @app.route('/<topic>/change-partition-count', methods = ['PUT'])
    def put_change_partition_count(topic):
        kafka_service = controller.kafka_service.get_kafka_cluster(get_kafka_id_from_header(request))
        body: Dict = json.loads(request.data)
        topic_name = request.view_args.get('topic', None)
        handler = ChangePartitionCount(kafka_service,
                                        topic_name,
                                        body["count"])
        
        return handler.handle()
    
    
    @app.route('/partition-event', methods = ['POST'])
    def post_partition_distribute():
        data = json.loads(request.data)
        handler = PartitionDistributeHandler(controller.redis_service,
                                       get_kafka_id_from_header(request),
                                       data["groupId"],
                                       data["topic"],
                                       data["ignoredPartitions"])
        
        return handler.handle()
    
    
    @app.route('/partition-event', methods = ['DELETE'])
    def delete_partition_distribute():
        queries = request.args.to_dict();
        topic = queries.get("topic", None)
        ignored_partitions = queries.get("ignoredPartitions", None)
        if topic is None or ignored_partitions is None:
            raise Exception("Parameter is null")
        
        handler = DeletePartitionDistributeHandler(
                                    controller.redis_service,
                                    topic,
                                    ignored_partitions)
        
        return handler.handle()
    
    @app.route('/partition-event', methods = ['GET'])
    def get_partition_distribute():
        queries = request.args.to_dict();
        topic = queries.get("topic", None)
        ignored_partitions = queries.get("ignoredPartitions", None)
        if topic is None or ignored_partitions is None:
            raise Exception("Parameter is null")
        
        handler = GetPartitionDistributeHandler(controller.redis_service, topic, ignored_partitions)
        
        return handler.handle()