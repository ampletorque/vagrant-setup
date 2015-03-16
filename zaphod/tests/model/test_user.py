from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from datetime import datetime, timedelta

from ... import model

from .base import ModelTest


class TestAccounts(ModelTest):
    @classmethod
    def _setup_once_data(cls):
        # cls.admin_role = model.Role(name=u'admin', rank=10)
        # model.Session.add(cls.admin_role)

        cls.user = model.User(name='Test User', email=u'admin@example.com')
        model.Session.add(cls.user)

        # cls.edit_accounts_permission = \
        #   model.Permission(name=u'edit_accounts')
        # model.Session.add(cls.edit_accounts_permission)
        # cls.edit_orders_permission = model.Permission(name=u'edit_orders')
        # model.Session.add(cls.edit_orders_permission)

        # cls.admin_role.permissions.add(cls.edit_accounts_permission)
        # cls.admin_role.permissions.add(cls.edit_orders_permission)
        # cls.user.roles.add(cls.admin_role)

    def test_hash_password(self):
        self.assertIsNone(model.User.hash_password(None))
        s = model.User.hash_password('insecurepass')
        self.assertEquals(len(s), 60)
        self.assertTrue(s.startswith('$2a'))

    def test_hash_unicode_password(self):
        s = model.User.hash_password(u'moresecure\xe9')
        self.assertEquals(len(s), 60)
        self.assertTrue(s.startswith('$2a'))

    def test_generate_token(self):
        s = model.User.generate_token()
        self.assertEquals(len(s), 64)

    def test_reset_password(self):
        u = model.User()
        u.set_reset_password_token()
        orig_reset_time = u.password_reset_time
        diff = orig_reset_time - datetime.utcnow()
        self.assertLess(diff, timedelta(seconds=2))
        self.assertTrue(u.password_reset_token)

        u.clear_reset_password_token()
        self.assertFalse(u.password_reset_token)

        diff = u.password_reset_time - datetime.utcnow()
        self.assertLess(diff, timedelta(seconds=2))
        self.assertNotEqual(u.password_reset_time, orig_reset_time)

    def test_reset_password_twice(self):
        u = model.User()
        first = u.set_reset_password_token()
        second = u.set_reset_password_token()
        self.assertEqual(first, second)

    def test_update_password(self):
        u = model.User()
        u.update_password(u'insecurepass')
        self.assertTrue(u.check_password(u'insecurepass'))

    def test_check_null_password(self):
        self.assertFalse(model.User().check_password(u'anything'))
