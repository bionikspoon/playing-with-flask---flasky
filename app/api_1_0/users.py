#!/usr/bin/env python
# coding=utf-8

from flask import jsonify, request, current_app, url_for

from . import api
from ..models import User, Post


@api.route('/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.json)


@api.route('/users/<int:user_id>/posts/')
def get_user_posts(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['FLASKY_POSTS_PER_PAGE']

    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page, per_page, error_out=False)
    posts = pagination.items
    _prev = None if not pagination.has_prev else url_for('api.get_posts', page=page - 1, _external=True)
    _next = None if not pagination.has_next else url_for('api.get_posts', page=page + 1, _external=True)

    return jsonify({'posts': [post.json for post in posts], 'prev': _prev, 'next': _next, 'count': pagination.total})


@api.route('/users/<int:user_id>/timeline/')
def get_user_followed_posts(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['FLASKY_POSTS_PER_PAGE']

    pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(page, per_page, error_out=False)
    posts = pagination.items
    _prev = None if not pagination.has_prev else url_for('api.get_posts', page=page - 1, _external=True)
    _next = None if not pagination.has_next else url_for('api.get_posts', page=page + 1, _external=True)

    return jsonify({'posts': [post.json for post in posts], 'prev': _prev, 'next': _next, 'count': pagination.total})
