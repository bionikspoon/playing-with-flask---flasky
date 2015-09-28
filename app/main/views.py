#!/usr/bin/env python
# coding=utf-8

from datetime import datetime

from flask import (request, redirect, render_template, session, url_for, current_app, abort, flash)
from flask.ext.login import login_required, current_user

from . import main
from .forms import NameForm, EditProfileForm
from .. import db
from ..decorators import admin_required, permission_required
from ..email import send_email
from ..models import User, Permission


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if not user:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if current_app.config['FLASKY_ADMIN']:
                send_email(current_app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True

        session['name'], form.name.data = form.name.data, ''

        return redirect(url_for('.index'))
    user_agent = request.headers.get('User-Agent')
    name = 'Stranger' if not current_user.is_authenticated else current_user.username
    context = dict(user_agent=user_agent, current_time=datetime.utcnow(), form=form, name=name,
                   known=session.get('known', False))
    return render_template('index.html', **context)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)

    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return  render_template('edit_profile.html', form=form)


@main.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'


@main.route('/admin')
@login_required
@admin_required
def admin():
    return 'Only admins.'


@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderator():
    return 'Only moderators'
