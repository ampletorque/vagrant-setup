from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from operator import attrgetter
from datetime import datetime
from decimal import Decimal

import pytz

from sqlalchemy import Table, Column, ForeignKey, types, orm
from sqlalchemy.sql import func

from pyramid_es.mixin import ElasticMixin, ESMapping, ESField, ESString

from . import utils, custom_types
from .base import Base, Session
from .user import User
from .order import Order
from .cart import Cart, CartItem
from .product import Product
from .node import Node


related_projects = Table(
    'related_projects',
    Base.metadata,
    Column('source_id', None, ForeignKey('projects.node_id'),
           primary_key=True),
    Column('dest_id', None, ForeignKey('projects.node_id'),
           primary_key=True),
    mysql_engine='InnoDB')


class Project(Node, ElasticMixin):
    __tablename__ = 'projects'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    node_id = Column(None, ForeignKey('nodes.id'), primary_key=True)

    creator_id = Column(None, ForeignKey('creators.node_id'), nullable=False)
    target = Column(custom_types.Money, nullable=False, default=0)
    accepts_preorders = Column(types.Boolean, nullable=False, default=False)
    successful = Column(types.Boolean, nullable=False, default=False)

    include_in_launch_stats = Column(types.Boolean, nullable=False,
                                     default=True)
    pledged_elsewhere_amount = Column(custom_types.Money, nullable=False,
                                      default=0)
    pledged_elsewhere_count = Column(types.Integer, nullable=False, default=0)

    start_time = Column(types.DateTime, nullable=True)
    end_time = Column(types.DateTime, nullable=True)
    suspended_time = Column(types.DateTime, nullable=True)

    prelaunch_vimeo_id = Column(types.Integer, nullable=True)
    prelaunch_teaser = Column(types.UnicodeText, nullable=False, default=u'')
    prelaunch_body = Column(types.UnicodeText, nullable=False, default=u'')

    crowdfunding_vimeo_id = Column(types.Integer, nullable=True)
    crowdfunding_teaser = Node.teaser
    crowdfunding_body = Node.body

    available_vimeo_id = Column(types.Integer, nullable=True)
    available_teaser = Column(types.UnicodeText, nullable=False, default=u'')
    available_body = Column(types.UnicodeText, nullable=False, default=u'')

    gravity = Column(types.Integer, nullable=False, default=0)

    homepage_url = Column(types.String(255), nullable=False, default=u'')
    open_source_url = Column(types.String(255), nullable=False, default=u'')

    direct_transactions = Column(types.Boolean, nullable=False, default=False)
    crowdfunding_fee_percent = Column(types.Numeric(6, 4), nullable=False,
                                      default=Decimal('5.0000'))
    preorder_fee_percent = Column(types.Numeric(6, 4), nullable=False,
                                  default=Decimal('10.0000'))

    updates = orm.relationship(
        'ProjectUpdate',
        backref='project',
        primaryjoin='ProjectUpdate.project_id == Project.node_id',
    )

    levels = orm.relationship(
        'Product',
        backref='project',
        cascade='all, delete, delete-orphan',
    )

    ownerships = orm.relationship('ProjectOwner', backref='project',
                                  cascade='all, delete, delete-orphan')

    # XXX Might be able to clean this up with the new SQLAlchemy relationship
    # APIs and/or annotations.
    related_projects = orm.relationship(
        'Project',
        secondary=related_projects,
        primaryjoin='related_projects.c.source_id == Project.node_id',
        secondaryjoin='related_projects.c.dest_id == Project.node_id')

    __mapper_args__ = {'polymorphic_identity': 'Project'}

    def generate_path(self):
        creator_path = self.creator.canonical_path()
        name = self.name or u'project-%s' % self.id
        project_path = utils.to_url_name(name)
        return creator_path + '/' + project_path

    def is_live(self):
        """
        Return True if the project should be available for the public to view
        (e.g. it's not pre-release).
        """
        utcnow = utils.utcnow()
        return (utcnow > self.start_time) or self.listed

    def is_failed(self):
        utcnow = utils.utcnow()
        return (self.pledged_amount < self.target) and (utcnow > self.end_time)

    def update_successful(self):
        self.successful = self.pledged_amount >= self.target

    @property
    def status(self):
        # returns one of:
        # - prelaunch
        # - crowdfunding
        # - suspended
        # - failed
        # - available (some mixture of preorder and stock)
        # - funded (no longer available)
        utcnow = utils.utcnow()
        if utcnow < self.start_time:
            return 'prelaunch'
        elif self.suspended_time:
            return 'suspended'
        elif self.start_time <= utcnow <= self.end_time:
            return 'crowdfunding'
        elif self.pledged_amount < self.target:
            return 'failed'
        elif self.accepts_preorders and self.target:
            return 'available'
        elif self.accepts_preorders:
            return 'stock-only'
        else:
            return 'funded'

    @property
    def progress_percent(self):
        if self.target:
            return self.pledged_amount * 100 / self.target
        return 0

    @property
    def pledged_amount(self):
        """
        Amount raised in crowdfunding and preorder stages.
        """
        # XXX FIXME Filter out cancelled orders.
        base = Session.query(func.sum(CartItem.qty_desired *
                                      CartItem.price_each)).\
            join(CartItem.cart).\
            join(Cart.order).\
            join(CartItem.product).\
            filter(Product.project == self).\
            scalar() or 0
        elsewhere_amount = self.pledged_elsewhere_amount or 0
        return base + elsewhere_amount

    @property
    def num_backers(self):
        q = Session.query(func.count(User.id.distinct())).\
            join(User.orders).\
            join(Order.cart).\
            join(Cart.items).\
            join(CartItem.product).\
            filter(Product.project == self)
        return q.scalar() or 0

    @property
    def num_pledges(self):
        # XXX Performance
        if (self.status != 'fundraising' and
                self.pledged_elsewhere_count > 0):
            return self.pledged_elsewhere_count
        # XXX FIXME Filter out cancelled orders.
        return Session.query(func.sum(CartItem.qty_desired)).\
            join(CartItem.cart).\
            join(Cart.order).\
            join(CartItem.product).\
            filter(Product.project == self).\
            scalar() or 0

    @property
    def final_day(self):
        end = pytz.utc.localize(self.end_time)
        pst = pytz.timezone('America/Los_Angeles')
        return end.astimezone(pst).replace(tzinfo=None)

    @property
    def remaining(self):
        utcnow = datetime.utcnow()
        if self.start_time <= utcnow:
            diff = self.end_time - utcnow
        else:
            diff = self.end_time - self.start_time

        if diff.days >= 2:
            return diff.days, 'days'
        else:
            hours = int(round((diff.seconds / 3600) + (diff.days * 24)))
            return hours, 'hours'

    @property
    def published_updates(self):
        # XXX FIXME turn into a relationship
        return [pu for pu in self.updates if pu.published]

    @property
    def published_levels(self):
        # XXX FIXME turn into a relationship
        levels = [pl for pl in self.levels if pl.published]
        levels.sort(key=attrgetter('gravity'))
        return levels

    @property
    def published_ownerships(self):
        # XXX FIXME turn into a relationship
        return [owner for owner in self.ownerships if owner.show_on_campaign]

    @property
    def price_range_low(self):
        return min(pl.price for pl in self.levels
                   if pl.published and not pl.non_physical)

    @property
    def price_range_high(self):
        return max(pl.price for pl in self.levels
                   if pl.published and not pl.non_physical)

    @classmethod
    def elastic_mapping(cls):
        return ESMapping(
            analyzer='content',
            properties=ESMapping(
                ESString('name', boost=5),
                ESString('keywords'),
                # XXX For simplicity we're just passing the non-rendered
                # markdown string to elasticsearch. We're just using it for
                # keyword indexing, so that should work ok for now.
                ESString('prelaunch_teaser', boost=3),
                ESString('prelaunch_body'),
                ESString('crowdfunding_teaser', boost=3),
                ESString('crowdfunding_body'),
                ESString('available_teaser', boost=3),
                ESString('available_body'),
                ESField('published'),
                ESField('listed'),
                ESField('target'),
                ESField('start_time'),
                ESField('end_time'),
                ESString('levels',
                         filter=lambda levels: [pl.name for pl in levels]),
                creator=ESMapping(
                    properties=ESMapping(
                        ESString('name', boost=8),
                    ),
                ),
            ))


class ProjectUpdate(Node):
    __tablename__ = 'project_updates'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    node_id = Column(None, ForeignKey('nodes.id'), primary_key=True)
    project_id = Column(None, ForeignKey('projects.node_id'), nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'ProjectUpdate'}

    def generate_path(self):
        project_path = self.project.canonical_path()
        return '%s/updates/%d' % (project_path, self.id)


class ProjectOwner(Base):
    __tablename__ = 'project_owners'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    project_id = Column(None, ForeignKey('projects.node_id'), primary_key=True)
    user_id = Column(None, ForeignKey('users.id'), primary_key=True)
    title = Column(types.Unicode(255), nullable=False, default=u'')
    gravity = Column(types.Integer, nullable=False, default=0)
    can_change_content = Column(types.Boolean, nullable=False, default=False)
    can_post_updates = Column(types.Boolean, nullable=False, default=False)
    can_receive_questions = Column(types.Boolean, nullable=False,
                                   default=False)
    can_manage_payments = Column(types.Boolean, nullable=False, default=False)
    can_manage_owners = Column(types.Boolean, nullable=False, default=False)
    show_on_campaign = Column(types.Boolean, nullable=False, default=False)

    user = orm.relationship('User', backref='project_ownerships')
