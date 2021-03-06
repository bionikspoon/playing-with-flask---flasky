#!/usr/bin/env python
# coding=utf-8

import hashlib
from datetime import datetime
from random import randint

import bleach
from flask import current_app, request, url_for
from flask.ext.login import UserMixin, AnonymousUserMixin
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature)
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash

from .exceptions import ValidationError
from . import db, login_manager


class Permission(object):
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMIN = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True),
            'Moderator': (
                Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS,
                False),
            'Administrator': (0xff, False)
        }
        for role_name, role_data in roles.items():
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name)
            role.permissions, role.default = role_data
            db.session.add(role)
        db.session.commit()
        # print('Roles inserted.')


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_fake(count=20):
        from random import seed, random, randrange, sample
        before = Follow.query.count()
        seed()
        users = User.query.all()
        for user in users:
            if not random() > .2:
                continue

            sample_size = randrange(0, count)
            follow_sample = sample(users, sample_size)
            for followee in follow_sample:
                user.follow(followee)
            db.session.commit()
        after = Follow.query.count()
        participants = Follow.query.group_by('follower_id').having(db.func.count('follower_id') > 1).count()
        print('%s new follows. %s total follows with %s participants.' % (after - before, after, participants))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))

    posts = db.relationship('Post', backref='author', lazy='dynamic')

    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'), lazy='dynamic',
                               cascade='all, delete-orphan')
    follower = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed', lazy='joined'), lazy='dynamic',
                               cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    @property
    def json(self):
        return {
            'url': url_for('api.get_user', user_id=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', user_id=self.id, _external=True),
            'followed_posts': url_for('api.get_user_followed_posts', user_id=self.id, _external=True),
            'post_count': self.posts.count()
        }

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, **kwargs):
        # noinspection PyArgumentList
        super().__init__(**kwargs)

        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN_EMAIL']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email and not self.avatar_hash:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        self.followed.append(Follow(followed=self))

    @property
    def password(self):
        raise AttributeError('`password` is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (SignatureExpired, BadSignature):
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (SignatureExpired, BadSignature):
            return False

        if data.get('reset') != self.id:
            return False

        self.password = new_password
        db.session.add(self)

        return True

    def generate_email_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (SignatureExpired, BadSignature):
            return False

        if data.get('change_email') != self.id:
            return False

        new_email = data.get('new_email')

        if not new_email:
            return False

        if self.query.filter_by(email=new_email).first():
            return False

        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

        db.session.add(self)

        return True

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    @property
    def is_admin(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='monsterid', rating='g'):
        prefix = 'https://secure.' if request.is_secure else 'http://www.'
        url = 'gravatar.com/avatar'
        email_hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        template = '{prefix}{url}/{email_hash}?s={size}&d={default}&r={rating}'
        return template.format(prefix=prefix, url=url, email_hash=email_hash, size=size, default=default, rating=rating)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py as forgery

        seed()
        before = User.query.count()
        for i in range(count):
            user = User(email=forgery.internet.email_address(), username=forgery.internet.user_name(with_num=True),
                        password='secret', confirmed=True, name=forgery.name.full_name(),
                        location=forgery.address.city(), about_me=forgery.lorem_ipsum.sentence(),
                        member_since=forgery.date.date(past=True))
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
        after = User.query.count()
        print('%s users created. %s users total' % (after - before, after))

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower=self, followed=user)
            db.session.add(follow)

    def unfollow(self, user):
        follow = self.followed.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.follower.filter_by(follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def generate_auth_token(self, expiration):
        serializer = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return serializer.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        serializer = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token)
        except (SignatureExpired, BadSignature):
            return False
        return User.query.get_or_404(data['id'])


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @property
    def json(self):
        return {
            'url': url_for('api.get_post', post_id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', user_id=self.author_id, _external=True),
            'comments': url_for('api.get_post_comments', post_id=self.id, _external=True),
            'comment_count': self.comments.count()
        }

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if not body:
            raise ValidationError('post does not have a body')
        return Post(body=body)

    @staticmethod
    def on_changed_body(target, value, *_):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(
            bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))

    @staticmethod
    def generate_fake(count=100):
        from random import seed
        import forgery_py as forgery

        seed()
        before = Post.query.count()
        user_count = User.query.count()
        for i in range(count):
            user = User.query.offset(randint(0, user_count - 1)).first()
            post = Post(body=forgery.lorem_ipsum.sentences(quantity=randint(1, 5)),
                        timestamp=forgery.date.date(past=True), author=user)
            db.session.add(post)
            db.session.commit()

        after = Post.query.count()
        participants = Post.query.group_by('author_id').count()
        print('%s posts created.  %s posts total with %s participants.' % (after - before, after, participants))


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @property
    def json(self):
        return {
            'url': url_for('api.get_comment', comment_id=self.id, _external=True),
            'post': url_for('api.get_post', post_id=self.post_id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', user_id=self.author_id, _external=True)
        }

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if not body:
            raise ValidationError('comment does not have a body')
        return Comment(body=body)

    @staticmethod
    def on_changed_body(target, value, *_):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong']
        target.body_html = bleach.linkify(
            bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))

    @staticmethod
    def generate_fake(count=50):
        from random import seed, random, randrange, choice
        import forgery_py as forgery

        seed()
        before = Comment.query.count()
        users = User.query.all()
        posts = Post.query.all()
        for user in users:
            if not random() > .5:
                continue

            sample_size = randrange(1, count)
            for _ in range(sample_size):
                disabled = random() < .1
                post = choice(posts)
                comment = Comment(post=post, author=user, body=forgery.lorem_ipsum.sentences(randint(1, 3)),
                                  timestamp=forgery.date.date(past=True), disabled=disabled)
                db.session.add(comment)
        after = Comment.query.count()
        participants = Comment.query.group_by('author_id').count()
        print('%s new comments.  %s comments total with %s participants.' % (after - before, after, participants))


class AnonymousUser(AnonymousUserMixin):
    is_admin = False

    # noinspection PyMethodMayBeStatic
    def can(self, _):
        return False


login_manager.anonymous_user = AnonymousUser

db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Comment.body, 'set', Comment.on_changed_body)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
