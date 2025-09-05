from flask import Flask
from flasgger import Swagger
from flask_marshmallow import Marshmallow
from app.config.swagger import swagger_template
from app.config.config import Config

prefix = "/api/v1"

def create_app():
    app = Flask(__name__)
    print(" * Swagger on: http://127.0.0.1:5000/apidocs")
    
    register_extensions(app)
    register_routes(app)
    return app


def register_extensions(app):
    
    Swagger(app, template=swagger_template)
    Marshmallow(app)

def register_routes(app):
    from app.chat.controller.chat_controller import chat_controller
    app.register_blueprint(chat_controller, url_prefix=prefix)
    ...