#!/usr/bin/env python
# coding=utf-8

from flask import jsonify, request, g, url_for, current_app

from . import api
from .. import db
from ..decorators import permission_required
from ..models import Comment, Post, Permission


@api.route('/comments/')
def get_comments():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['FLASKY_POSTS_PER_PAGE']

    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page, per_page, error_out=False)
    comments = pagination.items
    _prev = None if not pagination.has_prev else url_for('api.get_posts', page=page - 1, _external=True)
    _next = None if not pagination.has_next else url_for('api.get_posts', page=page + 1, _external=True)
    response = {
        'comments': [comment.json for comment in comments],
        'prev': _prev,
        'next': _next,
        'count': pagination.total
    }
    return jsonify(response)


@api.route('/comments/<int:comment_id>')
def get_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return jsonify(comment.json)


@api.route('/posts/<int:post_id>/comments/')
def get_post_comments(post_id):
    post = Post.query.get_or_404(post_id)

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['FLASKY_POSTS_PER_PAGE']

    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page, error_out=False)
    comments = pagination.items
    _prev = None if not pagination.has_prev else url_for('api.get_posts', page=page - 1, _external=True)
    _next = None if not pagination.has_next else url_for('api.get_posts', page=page + 1, _external=True)
    response = {
        'comments': [comment.json for comment in comments],
        'prev': _prev,
        'next': _next,
        'count': pagination.total
    }
    return jsonify(response)


@api.route('/posts/<int:post_id>/comments/', methods=['POST'])
@permission_required(Permission.COMMENT)
def new_post_comment(post_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment.from_json(request.json)
    comment.author = g.current_user
    comment.post = post
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.json), 201, {'Location': url_for('api.get_comment', comment_id=comment.id, _external=True)}
