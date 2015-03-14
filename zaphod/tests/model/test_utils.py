from unittest import TestCase
from datetime import datetime

from sqlalchemy import MetaData, Column, types, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import transaction

from ... import model
from ...model import utils

from .base import ModelTest
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
        self.orig_metadata = model.Base.metadata
        self.orig_session = model.Session
        model.Base.metadata = MetaData('sqlite://')
        Base = declarative_base(metadata=model.Base.metadata,
                                cls=model.base._Base)

        class Foo(Base):
            __tablename__ = 'test_dedupe'
            id = Column(types.Integer, primary_key=True)
            blah = Column(types.String(10), unique=True)

        model.Base.metadata.drop_all()
        model.Base.metadata.create_all()
        sm = sessionmaker(bind=model.Base.metadata.bind)
        model.Session = scoped_session(sm)
        self.Foo = Foo

    def tearDown(self):
        model.Base.metadata = self.orig_metadata
        model.Session = self.orig_session

    def test_dedupe_nodupes(self):
        self.assertEquals(utils.dedupe_name(self.Foo, 'blah', u'no-such-node'),
                          u'no-such-node')

    def test_dedupe_onedupe(self):
        model.Session.add(self.Foo(blah=u'zyzzx'))
        model.Session.commit()
        self.assertEquals(utils.dedupe_name(self.Foo, 'blah', u'zyzzx'),
                          u'zyzzx-1')

    def test_dedupe_lots(self):
        model.Session.add(self.Foo(blah=u'sup'))
        for ii in range(20):
            model.Session.add(self.Foo(blah=u'sup-%d' % ii))
        model.Session.commit()
        self.assertEquals(utils.dedupe_name(self.Foo, 'blah', u'sup'),
                          u'sup-20')

    def test_dedupe_toomany(self):
        model.Session.add(self.Foo(blah=u'ugh'))
        for ii in range(120):
            model.Session.add(self.Foo(blah=u'ugh-%d' % ii))
        model.Session.commit()
        with self.assertRaisesRegexp(ValueError,
                                     'Failed to find non-duplicate'):
            utils.dedupe_name(self.Foo, 'blah', 'ugh')
