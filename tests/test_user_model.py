#!/usr/bin/env python
# coding=utf-8

import time
import unittest
from app import create_app, db
from app.models import User, Role, Permission, AnonymousUser


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.user = User(password='secret')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        self.assertTrue(self.user.password_hash is not None)

    def test_no_password_getter(self):
        with self.assertRaises(AttributeError):
            # noinspection PyStatementEffect
            self.user.password

    def test_password_verification(self):
        self.assertTrue(self.user.verify_password('secret'))
        self.assertFalse(self.user.verify_password('not_secret'))

    def test_password_salts_are_random(self):
        user1 = User(password='secret')
        user2 = User(password='secret')
        self.assertNotEqual(user1.password_hash, user2.password_hash)

    def test_valid_confirmation_token(self):
        db.session.add(self.user)
        db.session.commit()
        token = self.user.generate_confirmation_token()
        self.assertTrue(self.user.confirm(token))

    def test_invalid_confirmation_token(self):
        user1 = User(password='secret')
        user2 = User(password='secret')
        db.session.add_all([user1, user2])
        db.session.commit()

        token = user1.generate_confirmation_token()
        self.assertFalse(user2.confirm(token))

    def test_expired_confirmation_token(self):
        db.session.add(self.user)
        db.session.commit()
        token = self.user.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(self.user.confirm(token))

    def test_valid_reset_token(self):
        db.session.add(self.user)
        db.session.commit()

        token = self.user.generate_reset_token()
        self.assertTrue(self.user.reset_password(token, 'new secret'))
        self.assertTrue(self.user.verify_password('new secret'))

    def test_invalid_reset_token(self):
        user1 = User(password='secret')
        user2 = User(password='secret')
        db.session.add_all([user1, user2])
        db.session.commit()

        token = user1.generate_reset_token()
        self.assertFalse(user2.reset_password(token, 'new secret'))
        self.assertTrue(user2.verify_password('secret'))

    def test_valid_email_change_token(self):
        db.session.add(self.user)
        db.session.commit()

        token = self.user.generate_email_token('test@test.com')
        self.assertTrue(self.user.change_email(token))
        self.assertEqual(self.user.email, 'test@test.com')

    def test_invalid_email_change_token(self):
        user1 = User(email='user1@test.com', password='secret')
        user2 = User(email='user2@test.com', password='secret')
        db.session.add_all([user1, user2])
        db.session.commit()

        token = user1.generate_email_token('new@test.com')
        self.assertFalse(user2.change_email(token))
        self.assertEqual(user2.email, 'user2@test.com')

    def test_duplicate_email_change_token(self):
        user1 = User(email='user1@test.com', password='secret')
        user2 = User(email='user2@test.com', password='secret')
        db.session.add_all([user1, user2])
        db.session.commit()

        token = user2.generate_email_token('user1@test.com')
        self.assertFalse(user2.change_email(token))
        self.assertEqual(user2.email, 'user2@test.com')

    def test_roles_and_permissions(self):
        self.assertTrue(self.user.can(Permission.WRITE_ARTICLES))
        self.assertFalse(self.user.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user(self):
        user = AnonymousUser()
        self.assertFalse(user.can(Permission.FOLLOW))
        self.assertFalse(user.can(Permission.ADMIN))

    def test_admin_user_can_admin(self):
        admin_role = Role.query.filter_by(permissions=0xff).first()
        self.user.role = admin_role

        self.assertTrue(self.user.can(Permission.ADMIN))
        self.assertTrue(self.user.is_admin)

    def test_gravatar(self):
        self.user.email = 'test@test.com'

        with self.app.test_request_context('/'):
            gravatar = self.user.gravatar()
            gravatar_256 = self.user.gravatar(size=256)
            gravatar_pg = self.user.gravatar(rating='pg')
            gravatar_retro = self.user.gravatar(default='retro')

        with self.app.test_request_context('/', base_url='https://example.com'):
            gravatar_ssl = self.user.gravatar()

        hashed_email = 'b642b4217b34b1e8d3bd915fc65c4452'
        self.assertIn('http://www.gravatar.com/avatar/%s' % hashed_email, gravatar)
        self.assertIn('s=256', gravatar_256)
        self.assertIn('r=pg', gravatar_pg)
        self.assertIn('d=retro', gravatar_retro)
        self.assertIn('https://secure.gravatar.com/avatar/%s' % hashed_email, gravatar_ssl)


if __name__ == '__main__':
    unittest.main()
