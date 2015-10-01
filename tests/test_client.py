#!/usr/bin/env python
# coding=utf-8

import unittest

from flask import url_for

from app import create_app, db
from app.models import Role, User


class FlaskClientTestCase(unittest.TestCase):
    """
    :type self.app: flask.Flask
    :type self.app_context: flask.ctx.AppContext
    :type self.client: flask.testing.FlaskClient
    """

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))
        self.assertIn('Stranger', response.get_data(as_text=True))

    def test_register_and_login(self):
        # register a new account
        response = self.client.post(url_for('auth.register'), data={
            'email': 'test@test.com',
            'username': 'test',
            'password': 'secret',
            'password_confirm': 'secret'
        })
        self.assertEqual(response.status_code, 302)

        # login with new account
        response = self.client.post(url_for('auth.login'), data={'email': 'test@test.com', 'password': 'secret'},
                                    follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertRegex(data, 'Hello,\s+test!')
        self.assertIn('You have not confirmed your account', data)

        # send a confirmation token
        user = User.query.filter_by(email='test@test.com').first()
        token = user.generate_confirmation_token()

        response = self.client.get(url_for('auth.confirm', token=token), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('You have confirmed your account', data)

        # log out
        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('You have been logged out', data)

        if __name__ == '__main__':
            unittest.main()
