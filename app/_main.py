#!/usr/bin/env python
# coding=utf-8
import os
from datetime import datetime
from flask import Flask, request, redirect, render_template, session, url_for
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail, Message
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.moment import Moment
from flask.ext.script import Manager, Shell
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from threading import Thread

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % os.path.join(ROOT_DIR, 'db.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['MAIL_HOSTNAME'] = 'localhost'
app.config['MAIL_PORT'] = 1025
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <no-reply@flasky.com>'
app.config['FLASKY_ADMIN'] = 'Manu Phatak <admin@flasky.com>'

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)


def make_shell_context():
    return dict(app=app, db=db, mail=mail, Message=Message, send_email=send_email, User=User, Role=Role)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **context):
    msg = Message('%s %s' % (app.config['FLASKY_MAIL_SUBJECT_PREFIX'], subject),
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template('%s.txt' % template, **context)
    msg.html = render_template('%s.html' % template, **context)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if not user:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True

        session['name'], form.name.data = form.name.data, ''

        return redirect(url_for('index'))
    user_agent = request.headers.get('User-Agent')
    context = dict(user_agent=user_agent, current_time=datetime.utcnow(), form=form,
                   name=session.get('name', 'Stranger'), known=session.get('known', False))
    return render_template('index.html', **context)


@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.html'), 404


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


if __name__ == '__main__':
    manager.run()
