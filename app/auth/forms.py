#!/usr/bin/env python
# coding=utf-8

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from app.models import User


def Unique(column, message=None):
    if not message:
        message = '%s is already in use.' % column.title()

    def validator(form, field):
        filter = {column: field.data}
        if User.query.filter_by(**filter).first():
            raise ValidationError(message)

    return validator


class LoginForm(Form):
    email = EmailField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


username_regexp = Regexp('^[A-Za-z][A-Za-z0-9_\.]*$',
                         message='Usernames must have only letter, numbers, dots, or underscores.')
password_equals_confirm = EqualTo('password_confirm', message='Passwords must match.')


class RegistrationForm(Form):
    email = EmailField('Email', validators=[DataRequired(), Length(1, 64), Email(), Unique('email')])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), username_regexp, Unique('username')])
    password = PasswordField('Password', validators=[DataRequired(), password_equals_confirm])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')


class ChangePasswordForm(Form):
    password_old = PasswordField('Old Password', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), password_equals_confirm])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_password(self, field):
        if field.data == self.password_old.data:
            raise ValidationError('New password must not equal old password.')
