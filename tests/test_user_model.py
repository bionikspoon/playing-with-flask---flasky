#!/usr/bin/env python
# coding=utf-8

import unittest
from app.models import User


class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        user = User(password='secret')
        self.assertTrue(user.password_hash is not None)

    def test_no_password_getter(self):
        user = User(password='secret')
        with self.assertRaises(AttributeError):
            # noinspection PyStatementEffect
            user.password

    def test_password_verification(self):
        user = User(password='secret')
        self.assertTrue(user.verify_password('secret'))
        self.assertFalse(user.verify_password('not_secret'))

    def test_password_salts_are_random(self):
        user1 = User(password='secret')
        user2 = User(password='secret')
        self.assertNotEqual(user1.password_hash, user2.password_hash)


if __name__ == '__main__':
    unittest.main()
