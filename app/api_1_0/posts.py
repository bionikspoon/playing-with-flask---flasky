#!/usr/bin/env python
# coding=utf-8
from flask import jsonify, request, g, url_for

from . import api
from .errors import forbidden
from .. import db
from ..decorators import permission_required
from ..models import Post, Permission


@api.route('/posts/')
def get_posts():
    posts = Post.query.all()
    return jsonify({'posts': [post.json for post in posts]})


@api.route('/posts/<int:post_id>')
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify(post.json)


@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.json), 201, {'Location': url_for('api.get_post', post_id=post.id, _external=True)}


@api.route('/posts/<int:post_id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if g.current_user != post.author and not g.current_user.is_admin:
        return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    return jsonify(post.json)
