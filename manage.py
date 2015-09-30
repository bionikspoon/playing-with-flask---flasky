#!/usr/bin/env python
# coding=utf-8

import os

from flask.ext.migrate import MigrateCommand, Migrate
from flask.ext.script import Manager
from flask.ext.script import Shell

from app import create_app, db
from app.email import send_email
from app.models import User, Role, Permission, Post, Follow, Comment

app = create_app(os.getenv('FLASK_CONFIG', 'default'))

manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, send_email=send_email, User=User, Role=Role, Post=Post, Permission=Permission,
                Follow=Follow, Comment=Comment)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def generate_fake():
    """Generate fake data"""
    Role.insert_roles()

    admin = User(email='admin@flasky.com', password='secret', confirmed=True, username='Admin')
    db.session.add(admin)
    db.session.commit()
    print('Inserting admin user: admin@flasky.com')

    User.generate_fake()
    Post.generate_fake()
    Comment.generate_fake()
    Follow.generate_fake()


if __name__ == '__main__':
    manager.run()
