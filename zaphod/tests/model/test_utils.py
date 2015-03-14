from unittest import TestCase
from datetime import datetime

from sqlalchemy import MetaData, Column, types
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

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


class TestDedupe(TestCase):
    def setUp(self):
        metadata = MetaData('sqlite://')
        Base = declarative_base(metadata=metadata)

        class Foo(Base):
            __tablename__ = 'test_dedupe'
            id = Column(types.Integer, primary_key=True)
            blah = Column(types.String(10), unique=True)

        Base.metadata.create_all()
        sm = sessionmaker(bind=metadata.bind)
        self.Session = scoped_session(sm)
        self.Foo = Foo

    def test_dedupe_nodupes(self):
        self.assertEquals(utils.dedupe_name(self.Foo, 'blah', u'no-such-node',
                                            session=self.Session),
                          u'no-such-node')

    def test_dedupe_onedupe(self):
        self.Session.add(self.Foo(blah=u'zyzzx'))
        self.Session.commit()
        self.assertEquals(utils.dedupe_name(self.Foo, 'blah', u'zyzzx',
                                            session=self.Session),
                          u'zyzzx-1')

    def test_dedupe_lots(self):
        self.Session.add(self.Foo(blah=u'sup'))
        for ii in range(20):
            self.Session.add(self.Foo(blah=u'sup-%d' % ii))
        self.Session.commit()
        self.assertEquals(utils.dedupe_name(self.Foo, 'blah', u'sup',
                                            session=self.Session),
                          u'sup-20')

    def test_dedupe_toomany(self):
        self.Session.add(self.Foo(blah=u'ugh'))
        for ii in range(120):
            self.Session.add(self.Foo(blah=u'ugh-%d' % ii))
        self.Session.commit()
        with self.assertRaisesRegexp(ValueError,
                                     'Failed to find non-duplicate'):
            utils.dedupe_name(self.Foo, 'blah', 'ugh', session=self.Session)
