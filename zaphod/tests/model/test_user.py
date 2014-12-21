from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from datetime import datetime, timedelta

from unittest import TestCase

from ...model import User


class TestUser(TestCase):
    def test_hash_password(self):
        self.assertIsNone(User.hash_password(None))
        s = User.hash_password('insecurepass')
        self.assertEquals(len(s), 60)
        self.assertTrue(s.startswith('$2a'))

    def test_hash_unicode_password(self):
        s = User.hash_password(u'moresecure\xe9')
        self.assertEquals(len(s), 60)
        self.assertTrue(s.startswith('$2a'))

    def test_generate_token(self):
        s = User.generate_token()
        self.assertEquals(len(s), 64)

    def test_reset_password(self):
        a = User()
        a.set_reset_password_token()
        orig_reset_time = a.password_reset_time
        diff = orig_reset_time - datetime.utcnow()
        self.assertLess(diff, timedelta(seconds=2))
        self.assertTrue(a.password_reset_token)

        a.clear_reset_password_token()
        self.assertFalse(a.password_reset_token)

        diff = a.password_reset_time - datetime.utcnow()
        self.assertLess(diff, timedelta(seconds=2))
        self.assertNotEqual(a.password_reset_time, orig_reset_time)

    def test_reset_password_twice(self):
        a = User()
        first = a.set_reset_password_token()
        second = a.set_reset_password_token()
        self.assertEqual(first, second)

    def test_update_password(self):
        a = User()
        a.update_password(u'insecurepass')
        self.assertTrue(a.check_password(u'insecurepass'))

    def test_check_null_password(self):
        self.assertFalse(User().check_password(u'anything'))
