#!/usr/bin/env python
# coding=utf-8

from flask import (redirect, render_template, url_for, flash, request, current_app, abort)
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
    per_page = current_app.config['FLASKY_POSTS_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page, error_out=False)
    posts = pagination.items
    name = 'Stranger' if not current_user.is_authenticated else (current_user.name or current_user.username)
    return render_template('index.html', form=form, posts=posts, name=name, pagination=pagination)


@main.route('/user/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['FLASKY_POSTS_PER_PAGE']
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page, per_page, error_out=False)
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


@main.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', posts=[post])


@main.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', post_id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user_profile', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user_profile', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user_profile', username=username))
    current_user.unfollow(user)
    flash('You are no longer following %s.' % username)
    return redirect(url_for('.user_profile', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['FLASKY_FOLLOWERS_PER_PAGE']
    pagination = user.follower.paginate(page, per_page, error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('follower.html', user=user, title='Followers of', endpoint='.followers',
                           pagination=pagination, follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['FLASKY_FOLLOWERS_PER_PAGE']
    pagination = user.followed.paginate(page, per_page, error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('follower.html', user=user, title='Followed by', endpoint='.followers',
                           pagination=pagination, follows=follows)
