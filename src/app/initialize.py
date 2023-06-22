import json
from threading import Thread
import time
from src.handlers.matchgroupandtopichandler import MatchGroupAndTopicHandler
from src.handlers.cacheclearhandler import CacheClearHandler
from src.controllers.controller import SearchController
from src.services.kafkaserviceinterface import KafkaServiceInterface
from src.configs.config import get_config
from flask_swagger_ui import get_swaggerui_blueprint

def initialize_swagger():
    swagger_path = 'static/swagger.json'
    f = open(swagger_path)
    data = json.load(f)
    data["schemes"] = [get_config().schema]
    f.close()
    
    json_object = json.dumps(data, indent=2)
    with open(swagger_path, "w") as outfile:
        outfile.write(json_object)
        
    swagger = get_swaggerui_blueprint(
        '/swagger',
        f'/{swagger_path}',
        config={
            'app_name': "Bee"
        },
    )
    
    return swagger

def initialize_cache(search_controller: SearchController):
    def background(kafka_service: KafkaServiceInterface):
        while True:
            try:
                key = f"app_cache:{kafka_service.get_id()}" 
                has_value = search_controller.redis_service.get_app_cache(key)
                if has_value is None:
                    search_controller.redis_service.set_app_cache(key)
                    CacheClearHandler(kafka_service, search_controller.redis_service).handle()
                    MatchGroupAndTopicHandler(kafka_service, search_controller.redis_service).handle()
            except Exception as ex:
                print('Error occured when cache was refreshing. ', ex)

            time.sleep(300)

    for _, kafka_service in search_controller.kafka_service.kafka_clusters.items():
        thread = Thread(target=background, args=(kafka_service,))
        thread.start()