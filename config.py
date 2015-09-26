#!/usr/bin/env python
# coding=utf-8

import os
from pathlib import Path

ROOT_DIR = Path(os.path.abspath('.'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secret')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_DATABASE_URI = NotImplemented
    MAIL_HOSTNAME = NotImplemented
    MAIL_PORT = NotImplemented
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <no-reply@flasky.com>'
    FLASKY_ADMIN = 'Manu Phatak <admin@flasky.com>'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_HOSTNAME = 'localhost'
    MAIL_PORT = 1025
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % (ROOT_DIR / 'db-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % (ROOT_DIR / 'db-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % (ROOT_DIR / 'db.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
