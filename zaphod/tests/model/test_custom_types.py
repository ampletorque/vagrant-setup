from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from unittest import TestCase
from decimal import Decimal

from sqlalchemy import MetaData, Column, types
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from ...model import custom_types


class TestCustomTypes(TestCase):

    def test_money_with_precision(self):
        with self.assertRaises(TypeError):
            custom_types.Money(precision=4)

    def test_money_with_scale(self):
        with self.assertRaises(TypeError):
            custom_types.Money(scale=4)


becomes_sentinel = object()


class TestTypeAbstract(TestCase):

    def setUp(self):
        metadata = MetaData('sqlite://')
        Base = declarative_base(metadata=metadata)

        class Foo(Base):
            __tablename__ = 'test_dedupe'
            id = Column(types.Integer, primary_key=True)
            val = Column(self.custom_type)

        metadata.create_all()
        sm = sessionmaker(bind=metadata.bind)
        self.sess = scoped_session(sm)
        self.klass = Foo

    def store(self, val):
        inst = self.klass(val=val)
        self.sess.add(inst)
        self.sess.commit()
        return inst.id

    def check(self, val, becomes=becomes_sentinel):
        pk = self.store(val)
        if becomes == becomes_sentinel:
            becomes = val
        got = self.sess.query(self.klass).get(pk).val
        self.assertEquals(got, becomes)


class TestJSONType(TestTypeAbstract):
    custom_type = custom_types.JSON

    def test_bool(self):
        self.check(False)
        self.check(True)

    def test_dict(self):
        self.check({'foo': 123,
                    'a': True,
                    'bar': 'blah'})

    def test_list(self):
        self.check([456, 'quux', False])


class TestMoneyType(TestTypeAbstract):
    custom_type = custom_types.Money

    def test_none(self):
        self.check(None)

    def test_normal(self):
        self.check(Decimal('123.45'))

    def test_precision_discarded(self):
        self.check(Decimal('123.4567'), Decimal('123.46'))
