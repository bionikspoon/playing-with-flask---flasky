#!/usr/bin/env python
# coding=utf-8

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo

from ..models import User
from ..validators import Unique, ValidUsername

password_equals_confirm = EqualTo('password_confirm', message='Passwords must match.')


class LoginForm(Form):
    email = EmailField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(Form):
    email = EmailField('Email', validators=[DataRequired(), Length(1, 64), Email(), Unique('email')])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), ValidUsername(), Unique('username')])
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


class PasswordResetRequestForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(Form):
    email = EmailField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired(), password_equals_confirm])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Update Password')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('Unknown email address.')


class ChangeEmailForm(Form):
    email = EmailField('New Email', validators=[DataRequired(), Length(1, 64), Email(), Unique('email')])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update Email Address')
