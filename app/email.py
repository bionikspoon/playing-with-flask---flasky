#!/usr/bin/env python
# coding=utf-8

from threading import Thread

from flask import render_template, current_app
from flask.ext.mail import Message

from . import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **context):
    app = current_app._get_current_object()
    msg = Message('%s %s' % (current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'], subject),
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template('%s.txt' % template, **context)
    msg.html = render_template('%s.html' % template, **context)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
