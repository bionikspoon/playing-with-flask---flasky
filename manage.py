#!/usr/bin/env python
# coding=utf-8
import os

from flask.ext.migrate import MigrateCommand, Migrate
from flask.ext.script import Manager
from flask.ext.script import Shell

from app import create_app, db
from app.email import send_email
from app.models import User, Role

app = create_app(os.getenv('FLASK_CONFIG', 'default'))

manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, send_email=send_email, User=User, Role=Role)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
