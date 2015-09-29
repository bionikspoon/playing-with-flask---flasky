#!/usr/bin/env python
# coding=utf-8

from flask import (redirect, render_template, url_for, flash, request, current_app)
from flask.ext.login import login_required, current_user

from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from .. import db
from ..decorators import admin_required, permission_required
from ..models import User, Permission, Role, Post


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        # noinspection PyProtectedMember
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config[
        'FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    name = 'Stranger' if not current_user.is_authenticated else (current_user.name or current_user.username)
    return render_template('index.html', form=form, posts=posts, name=name, pagination=pagination)


@main.route('/user/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()

    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config[
        'FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items

    return render_template('user_profile.html', user=user, posts=posts, pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
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
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(user_id):
    user = User.query.get_or_404(user_id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


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
