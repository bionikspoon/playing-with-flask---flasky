#!/usr/bin/env python
# coding=utf-8
from flask import g
from flask.ext.httpauth import HTTPBasicAuth

from . import api
from .errors import unauthorized, forbidden
from ..models import AnonymousUser, User

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email, password):
    if not email:
        g.current_user = AnonymousUser()
        return True

    user = User.query.filter_by(email=email).first()
    if not user:
        return False
    g.current_user = user

    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    if not g.currrent_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('Unconfirmed account')
