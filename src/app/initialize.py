import json
from threading import Thread
import time
from src.handlers.matchgroupandtopichandler import MatchGroupAndTopicHandler
from src.handlers.cacheclearhandler import CacheClearHandler
from src.services.kafkaserviceinterface import KafkaServiceInterface
from flask_swagger_ui import get_swaggerui_blueprint
from src.services.redisservice import RedisService

def initialize_swagger():
    swagger_path = 'static/swagger.json'
    f = open(swagger_path)
    data = json.load(f)
    data["schemes"] = ["http", "https"]
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