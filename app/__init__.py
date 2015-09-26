from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.script import Manager
from flask.ext.sqlalchemy import SQLAlchemy
from config import config

manager = Manager()
bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
mail = Mail()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    mail.init_app(app)

    #  Routes and custom error pages goes here.

    return app
