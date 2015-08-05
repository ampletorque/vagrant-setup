from sqlalchemy import Table, Column, ForeignKey, types, orm

from .base import Base
from .user_mixin import UserMixin


discount_products = Table(
    'discount_products',
    Base.metadata,
    Column('discount_id', None, ForeignKey('discounts.id'), primary_key=True),
    Column('product_id', None, ForeignKey('products.id'), primary_key=True),
    mysql_engine='InnoDB')


discount_users = Table(
    'discount_users',
    Base.metadata,
    Column('discount_id', None, ForeignKey('discounts.id'), primary_key=True),
    Column('user_id', None, ForeignKey('users.id'), primary_key=True),
    mysql_engine='InnoDB')


class Discount(Base, UserMixin):
    """
    A discount that applies to some set of products and (optionally) some set
    of users.
    """
    __tablename__ = 'discounts'
    id = Column(types.Integer, primary_key=True)
    creator_id = Column(None, ForeignKey('creators.node_id'), nullable=False)

    rate = Column(types.Numeric(6, 4), nullable=False, default=0)
    description = Column(types.Unicode(255), nullable=False)
    published = Column(types.Boolean, nullable=False, default=False)
    enabled = Column(types.Boolean, nullable=False, default=False)

    creator = orm.relationship('Creator', backref='discounts')
    products = orm.relationship('Product', secondary=discount_products)
    users = orm.relationship('User', secondary=discount_users)
