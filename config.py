#!/usr/bin/env python
# coding=utf-8

import os
from pathlib import Path

ROOT_DIR = Path(os.path.abspath('.'))


# noinspection PyPep8Naming
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret'

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_DATABASE_URI = NotImplemented

    MAIL_HOSTNAME = 'localhost'
    MAIL_PORT = 1025

    WTF_CSRF_ENABLED = NotImplemented

    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <no-reply@flasky.com>'
    FLASKY_ADMIN = 'Manu Phatak <admin@flasky.com>'
    FLASKY_ADMIN_EMAIL = 'admin@flasky.com'
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 50
    FLASKY_COMMENTS_PER_PAGE = 30

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % (ROOT_DIR / 'db-dev.sqlite')
    WTF_CSRF_ENABLED = False
    FLASKY_POSTS_PER_PAGE = 5
    FLASKY_FOLLOWERS_PER_PAGE = 5
    FLASKY_COMMENTS_PER_PAGE = 5


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % (ROOT_DIR / 'db-test.sqlite')
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % (ROOT_DIR / 'db.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
