#!/usr/bin/env python
# coding=utf-8

import time
import unittest

from app import create_app, db
from app.models import User


# noinspection PyArgumentList
class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
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

        # token = self.user.generate_confirmation_token()
        # self.assertTrue(self.user.confirm(token))

    def test_invalid_reset_token(self):
        user1 = User(password='secret')
        user2 = User(password='secret')
        db.session.add_all([user1, user2])
        db.session.commit()

        # token = user1.generate_confirmation_token()
        # self.assertFalse(user2.confirm(token))

    def test_valid_email_change_token(self):
        db.session.add(self.user)
        db.session.commit()

        # token = self.user.generate_confirmation_token()
        # self.assertTrue(self.user.confirm(token))

    def test_invalid_email_change_token(self):
        user1 = User(password='secret')
        user2 = User(password='secret')
        db.session.add_all([user1, user2])
        db.session.commit()

        # token = user1.generate_confirmation_token()
        # self.assertFalse(user2.confirm(token))

    def test_duplicate_email_change_token(self):
        pass


if __name__ == '__main__':
    unittest.main()
