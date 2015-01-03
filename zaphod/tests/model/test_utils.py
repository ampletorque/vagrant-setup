from unittest import TestCase
from datetime import datetime

from ...model import utils

from .mocks import patch_utcnow


class TestUtils(TestCase):
    def test_to_url_name_1(self):
        self.assertEquals(utils.to_url_name(u'The Quick Brown Fox'),
                          'the-quick-brown-fox')

    def test_to_url_name_2(self):
        self.assertEquals(
            utils.to_url_name(u'HEllo $!millionaires... Wassup?'),
            'hello-millionaires-wassup')

    def test_to_url_name_3(self):
        self.assertEquals(utils.to_url_name(u'hello-this-is-already'),
                          'hello-this-is-already')

    def test_to_url_name_bad(self):
        with self.assertRaisesRegexp(ValueError, 'unicode'):
            utils.to_url_name('hello')

    def test_to_url_name_unicode(self):
        # unicode snowman!
        self.assertEquals(utils.to_url_name(u'snowman \u2603 melts'),
                          'snowman-melts')

    def test_is_url_name_good(self):
        self.assertTrue(utils.is_url_name(u'this-is-good'))

    def test_is_url_name_bad(self):
        self.assertFalse(utils.is_url_name(u'This Is Bad'))


class TestUTCNow(TestCase):
    def test_basic(self):
        one = utils.utcnow()
        two = datetime.utcnow()
        self.assertLess((two - one).total_seconds(), 4)

    def test_mockable(self):
        with patch_utcnow(2012, 4, 1):
            self.assertEqual(utils.utcnow(), datetime(2012, 4, 1))
