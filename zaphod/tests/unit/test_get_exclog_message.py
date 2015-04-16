from unittest import TestCase

import six

from ...logging import get_exclog_message
from ...request import Request


class MockUser(object):
    id = 42
    name = 'Beeblebrox'
    email = 'president@whatever.galaxy'


class TestGetExclogMessage(TestCase):
    maxDiff = 2000

    def test_basic(self):
        request = Request.blank('/')
        request.user = MockUser()
        msg = get_exclog_message(request)
        self.assertIsInstance(msg, six.string_types)

    def test_sensitive_field_masking(self):
        request = Request.blank('/', method='POST')
        request.POST['hello'] = 'world'
        request.POST['cc.code'] = '1234'
        request.POST['cc.expires_month'] = '09'
        request.POST['cc.expires_year'] = '2025'
        request.POST['cc.number'] = '4111111111111111'
        request.POST['password'] = 'secret'
        request.POST['password2'] = 'secret'
        request.user = MockUser()
        msg = get_exclog_message(request)

        self.assertIn('hello', msg)
        self.assertIn('world', msg)
        self.assertIn('cc.code', msg)
        self.assertNotIn('1234', msg)
        self.assertNotIn('2025', msg)
        self.assertNotIn('4111111111111111', msg)
        self.assertNotIn('secret', msg)
