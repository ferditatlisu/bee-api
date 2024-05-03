from flask import Flask
from flask_cors import CORS
from src.app.initialize import initialize_swagger
from src.configs.config import get_config
from src.controllers.healthcontroller import health_controller_initialize
from src.controllers.controller import SearchController, controller_initialize

def main():    
    print("Api started")
    swagger = initialize_swagger()
    app = Flask(__name__)
    CORS(app)
    health_controller_initialize(app)
    search_controller = SearchController()
    controller_initialize(app, search_controller)
    app.register_blueprint(swagger)
    app.run(host="0.0.0.0", port=get_config().port, debug=False, threaded=True)
try:
    main()
except Exception as ex:
    print(ex)