#!/usr/bin/env python
# coding=utf-8
from flask.ext.pagedown.fields import PageDownField
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email

from ..models import Role
from ..validators import ValidUsername, Unique


class NameForm(Form):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About Me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email(), Unique('email')])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), ValidUsername(), Unique('username')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About Me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user


class PostForm(Form):
    body = PageDownField('What\'s on your mind?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class CommentForm(Form):
    body = PageDownField('', validators=[DataRequired()])
    submit = SubmitField('Submit')
