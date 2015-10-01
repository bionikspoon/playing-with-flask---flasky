# #!/usr/bin/env python
# # coding=utf-8
#
# import time
# import unittest
# from datetime import datetime
# from app import create_app, db
# from app.models import User, Role, Permission, AnonymousUser, Follow
#
#
# class BaseTestCase(unittest.TestCase):
#     def setUp(self):
#         self.app = create_app('testing')
#         self.app_context = self.app.app_context()
#         self.app_context.push()
#         db.create_all()
#
#     def tearDown(self):
#         db.session.remove()
#         db.drop_all()
#         self.app_context.pop()
#
#
# class UserModelTestCase(BaseTestCase):
#     def setUp(self):
#         super().setUp()
#         self.user = User(password='secret')
#
#     def test_password_setter(self):
#         self.assertTrue(self.user.password_hash is not None)
#
#     def test_no_password_getter(self):
#         with self.assertRaises(AttributeError):
#             # noinspection PyStatementEffect
#             self.user.password
#
#     def test_password_verification(self):
#         self.assertTrue(self.user.verify_password('secret'))
#         self.assertFalse(self.user.verify_password('not_secret'))
#
#     def test_password_salts_are_random(self):
#         user1 = User(password='secret')
#         user2 = User(password='secret')
#         self.assertNotEqual(user1.password_hash, user2.password_hash)
#
#     def test_gravatar(self):
#         self.user.email = 'test@test.com'
#
#         with self.app.test_request_context('/'):
#             gravatar = self.user.gravatar()
#             gravatar_256 = self.user.gravatar(size=256)
#             gravatar_pg = self.user.gravatar(rating='pg')
#             gravatar_retro = self.user.gravatar(default='retro')
#
#         with self.app.test_request_context('/', base_url='https://example.com'):
#             gravatar_ssl = self.user.gravatar()
#
#         hashed_email = 'b642b4217b34b1e8d3bd915fc65c4452'
#         self.assertIn('http://www.gravatar.com/avatar/%s' % hashed_email, gravatar)
#         self.assertIn('s=256', gravatar_256)
#         self.assertIn('r=pg', gravatar_pg)
#         self.assertIn('d=retro', gravatar_retro)
#         self.assertIn('https://secure.gravatar.com/avatar/%s' % hashed_email, gravatar_ssl)
#
#
# class UserProfileEditingTestCase(BaseTestCase):
#     def setUp(self):
#         super().setUp()
#         self.user = User(password='secret')
#
#     def test_valid_confirmation_token(self):
#         db.session.add(self.user)
#         db.session.commit()
#         token = self.user.generate_confirmation_token()
#         self.assertTrue(self.user.confirm(token))
#
#     def test_invalid_confirmation_token(self):
#         user1 = User(password='secret')
#         user2 = User(password='secret')
#         db.session.add_all([user1, user2])
#         db.session.commit()
#
#         token = user1.generate_confirmation_token()
#         self.assertFalse(user2.confirm(token))
#
#     def test_expired_confirmation_token(self):
#         db.session.add(self.user)
#         db.session.commit()
#         token = self.user.generate_confirmation_token(1)
#         time.sleep(2)
#         self.assertFalse(self.user.confirm(token))
#
#     def test_valid_reset_token(self):
#         db.session.add(self.user)
#         db.session.commit()
#
#         token = self.user.generate_reset_token()
#         self.assertTrue(self.user.reset_password(token, 'new secret'))
#         self.assertTrue(self.user.verify_password('new secret'))
#
#     def test_invalid_reset_token(self):
#         user1 = User(password='secret')
#         user2 = User(password='secret')
#         db.session.add_all([user1, user2])
#         db.session.commit()
#
#         token = user1.generate_reset_token()
#         self.assertFalse(user2.reset_password(token, 'new secret'))
#         self.assertTrue(user2.verify_password('secret'))
#
#     def test_valid_email_change_token(self):
#         db.session.add(self.user)
#         db.session.commit()
#
#         token = self.user.generate_email_token('test@test.com')
#         self.assertTrue(self.user.change_email(token))
#         self.assertEqual(self.user.email, 'test@test.com')
#
#     def test_invalid_email_change_token(self):
#         user1 = User(email='user1@test.com', password='secret')
#         user2 = User(email='user2@test.com', password='secret')
#         db.session.add_all([user1, user2])
#         db.session.commit()
#
#         token = user1.generate_email_token('new@test.com')
#         self.assertFalse(user2.change_email(token))
#         self.assertEqual(user2.email, 'user2@test.com')
#
#     def test_duplicate_email_change_token(self):
#         user1 = User(email='user1@test.com', password='secret')
#         user2 = User(email='user2@test.com', password='secret')
#         db.session.add_all([user1, user2])
#         db.session.commit()
#
#         token = user2.generate_email_token('user1@test.com')
#         self.assertFalse(user2.change_email(token))
#         self.assertEqual(user2.email, 'user2@test.com')
#
#
# class UserPermissionsTestCase(BaseTestCase):
#     def setUp(self):
#         super().setUp()
#         Role.insert_roles()
#
#         self.user = User()
#
#     def test_roles_and_permissions(self):
#         self.assertTrue(self.user.can(Permission.WRITE_ARTICLES))
#         self.assertFalse(self.user.can(Permission.MODERATE_COMMENTS))
#
#     def test_anonymous_user(self):
#         user = AnonymousUser()
#         self.assertFalse(user.can(Permission.FOLLOW))
#         self.assertFalse(user.can(Permission.ADMIN))
#
#     def test_admin_user_can_admin(self):
#         admin_role = Role.query.filter_by(permissions=0xff).first()
#         self.user.role = admin_role
#
#         self.assertTrue(self.user.can(Permission.ADMIN))
#         self.assertTrue(self.user.is_admin)
#
#
# class UserFollowsTestCase(BaseTestCase):
#     def setUp(self):
#         super().setUp()
#         self.user1, self.user2 = User(), User()
#         db.session.add_all([self.user1, self.user2])
#         db.session.commit()
#
#     def user1_follows_user2(self):
#         self.user1.follow(self.user2)
#         db.session.add(self.user1)
#         db.session.commit()
#
#     def user1_unfollows_user2(self):
#         self.user1.unfollow(self.user2)
#         db.session.add(self.user1)
#         db.session.commit()
#
#     def test_new_users_are_follower_blank_slate(self):
#         self.assertFalse(self.user1.is_following(self.user2))
#         self.assertFalse(self.user1.is_followed_by(self.user2))
#         self.assertEqual(self.user1.followed.count(), 1)
#         self.assertEqual(self.user1.follower.count(), 1)
#         self.assertEqual(self.user2.followed.count(), 1)
#         self.assertEqual(self.user2.follower.count(), 1)
#
#     def test_user_can_follow_other_users(self):
#         self.user1_follows_user2()
#
#         self.assertTrue(self.user1.is_following(self.user2))
#         self.assertTrue(self.user2.is_followed_by(self.user1))
#
#     def test_follow_semantic_methods(self):
#         self.user1_follows_user2()
#
#         self.assertFalse(self.user2.is_following(self.user1))
#         self.assertFalse(self.user1.is_followed_by(self.user2))
#
#         self.assertEqual(self.user1.followed.count(), 2)
#         self.assertEqual(self.user1.follower.count(), 1)
#         self.assertEqual(self.user2.followed.count(), 1)
#         self.assertEqual(self.user2.follower.count(), 2)
#
#     def test_follower_entry_timestamp_is_now(self):
#         timestamp_before = datetime.utcnow()
#
#         self.user1_follows_user2()
#
#         timestamp_after = datetime.utcnow()
#
#         follow_entry = self.user1.followed.all()[-1]
#         self.assertTrue(timestamp_before <= follow_entry.timestamp <= timestamp_after)
#
#     def test_pivot_table(self):
#         self.user1_follows_user2()
#
#         follow_entry = self.user1.followed.all()[-1]
#         self.assertEqual(follow_entry.followed, self.user2)
#
#         follow_entry = self.user2.follower.all()[-1]
#         self.assertEqual(follow_entry.follower, self.user1)
#
#         self.assertEqual(Follow.query.count(), 3)
#
#     def test_user_can_unfollow_a_user(self):
#         self.user1_follows_user2()
#         # Check for good measure before continuing
#         assert self.user1.is_following(self.user2)
#         self.user1_unfollows_user2()
#
#         self.assertFalse(self.user1.is_following(self.user2))
#         self.assertEqual(self.user1.followed.count(), 1)
#         self.assertEqual(self.user2.follower.count(), 1)
#
#         self.assertEqual(Follow.query.count(), 2)
#
#     def test_deletion_removes_orphans(self):
#         self.user1.follow(self.user2)
#         self.user2.follow(self.user1)
#         db.session.add_all([self.user1, self.user2])
#         db.session.commit()
#         db.session.delete(self.user2)
#         db.session.commit()
#         self.assertEqual(Follow.query.count(), 1)
#
#
# if __name__ == '__main__':
#     unittest.main()
