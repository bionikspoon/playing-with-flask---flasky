#!/usr/bin/env python
# coding=utf-8
import os
from datetime import datetime
from flask import Flask, request, redirect, render_template, session, url_for, flash
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.script import Manager
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % os.path.join(ROOT_DIR, 'db.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)


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
