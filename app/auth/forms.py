#!/usr/bin/env python
# coding=utf-8

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo

from app.models import User


class LoginForm(Form):
    email = EmailField('Email', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


username_regexp = Regexp('^[A-Za-z][A-Za-z0-9_\.]*$',
                         message='Usernames must have only letter, numbers, dots, or underscores.')
password_equals_confirm = EqualTo('password_confirm', message='Passwords must match.')


class RegistrationForm(Form):
    email = EmailField('Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField('Username', validators=[Required(), Length(1, 64), username_regexp])
    password = PasswordField('Password', validators=[Required(), password_equals_confirm])
    password_confirm = PasswordField('Confirm Password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
