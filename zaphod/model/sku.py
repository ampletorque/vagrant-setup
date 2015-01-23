from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import Table, Column, ForeignKey, types, orm

from .base import Base


sku_option_values = Table(
    'sku_option_values',
    Base.metadata,
    Column('sku_id', None, ForeignKey('skus.id'), primary_key=True),
    Column('option_value_id', None, ForeignKey('option_values.id'),
           primary_key=True),
    mysql_engine='InnoDB')


class SKU(Base):
    __tablename__ = 'skus'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    pledge_level_id = Column(None, ForeignKey('pledge_levels.id'),
                             nullable=False)

    option_values = orm.relationship('OptionValue',
                                     collection_class=set,
                                     secondary=sku_option_values)
