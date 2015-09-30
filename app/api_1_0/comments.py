#!/usr/bin/env python
# coding=utf-8

from flask import jsonify, request, g, url_for

from app import db
from app.api_1_0 import api
from app.api_1_0.decorators import permission_required
from app.models import Comment, Post, Permission


@api.route('/comments/')
def get_comments():
    comments = Comment.query.order_by(Comment.timestamp.desc()).all()
    return jsonify({'comments': [comment.json for comment in comments]})


@api.route('/comments/<int:comment_id>')
def get_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return jsonify(comment.json)


@api.route('/posts/<int:post_id>/comments/')
def get_post_comments(post_id):
    post = Post.query.get_or_404(post_id)
    comments = post.comments.order_by(Comment.timestamp.asc())
    return jsonify({'comments': [comment.json for comment in comments]})


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
