#!/usr/bin/env python
# coding=utf-8
from wtforms import ValidationError
from wtforms.validators import Regexp

from app.models import User


def Unique(column, message=None):
    if not message:
        message = '%s is already in use.' % column.title()

    def validator(_, field):
        filter = {column: field.data}
        if User.query.filter_by(**filter).first():
            raise ValidationError(message)

    return validator


def ValidUsername():
    return Regexp('^[A-Za-z][A-Za-z0-9_\.]*$',
                  message='Usernames must have only letter, numbers, dots, or underscores.')
