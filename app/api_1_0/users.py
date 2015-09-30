#!/usr/bin/env python
# coding=utf-8
from flask import jsonify

from . import api
from ..models import User, Post


@api.route('/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.json)


@api.route('/users/<int:user_id>/posts/')
def get_user_posts(user_id):
    user = User.query.get_or_404(user_id)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return jsonify({'posts': [post.json for post in posts]})


@api.route('/users/<int:user_id>/timeline/')
def get_user_followed_posts(user_id):
    user = User.query.get_or_404(user_id)
    posts = user.followed_posts.order_by(Post.timestamp.desc()).all()
    return jsonify({'posts': [post.json for post in posts]})
