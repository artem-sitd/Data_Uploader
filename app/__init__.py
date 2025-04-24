from flask import Flask
from .config import Config
from .db import db
from .routes import bp


# создание приложения, разовая миграция, париснг конфигов в словарь фласка
def create_app():
    app = Flask(__name__, template_folder='../templates/')
    app.config.from_object(Config)

    db.init_app(app)
    app.register_blueprint(bp)

    with app.app_context():
        from . import models
        db.create_all()

    return app
