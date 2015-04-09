from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

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
    """
    A 'campaign' presented on a single page. May be a crowdfunding campaign,
    but could also be pre-order or in-stock only. Has a set of products
    associated with it, comparable to 'pledge levels'.
    """
    __tablename__ = 'projects'
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
        order_by='ProjectUpdate.id',
    )
    published_updates = orm.relationship(
        'ProjectUpdate',
        viewonly=True,
        primaryjoin=('and_(ProjectUpdate.project_id == Project.node_id,'
                     'ProjectUpdate.published == True)'),
        order_by='ProjectUpdate.id',
    )

    products = orm.relationship(
        'Product',
        backref='project',
        cascade='all, delete, delete-orphan',
    )
    published_products = orm.relationship(
        'Product',
        viewonly=True,
        primaryjoin=('and_(Product.project_id == Project.node_id,'
                     'Product.published == True)'),
        order_by='Product.gravity',
    )

    ownerships = orm.relationship('ProjectOwner', backref='project',
                                  cascade='all, delete, delete-orphan')
    published_ownerships = orm.relationship(
        'ProjectOwner',
        viewonly=True,
        primaryjoin=('and_(ProjectOwner.project_id == Project.node_id,'
                     'ProjectOwner.show_on_campaign == True)'),
    )

    # XXX Might be able to clean this up with the new SQLAlchemy relationship
    # APIs and/or annotations.
    related_projects = orm.relationship(
        'Project',
        secondary=related_projects,
        collection_class=set,
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
        if self.start_time and (utcnow < self.start_time):
            return 'prelaunch'
        elif self.suspended_time:
            return 'suspended'
        elif self.start_time and (self.start_time <= utcnow <= self.end_time):
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
    def current_vimeo_id(self):
        if self.status == 'prelaunch':
            return self.prelaunch_vimeo_id
        elif self.status == 'available':
            return self.available_vimeo_id
        else:
            return self.crowdfunding_vimeo_id

    @property
    def current_body(self):
        if self.status == 'prelaunch':
            return self.prelaunch_body
        elif self.status == 'available':
            return self.available_body
        else:
            return self.crowdfunding_body

    @property
    def current_teaser(self):
        if self.status == 'prelaunch':
            return self.prelaunch_teaser
        elif self.status == 'available':
            return self.available_teaser
        else:
            return self.crowdfunding_teaser

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
        base = Session.query(func.sum(CartItem.qty_desired *
                                      CartItem.price_each)).\
            join(CartItem.cart).\
            join(Cart.order).\
            join(CartItem.product).\
            filter(Product.project == self).\
            filter(CartItem.status != 'cancelled').\
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
        if (self.status != 'fundraising' and
                self.pledged_elsewhere_count > 0):
            return self.pledged_elsewhere_count
        return Session.query(func.sum(CartItem.qty_desired)).\
            join(CartItem.cart).\
            join(Cart.order).\
            join(CartItem.product).\
            filter(Product.project == self).\
            filter(CartItem.status != 'cancelled').\
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
    def price_range_low(self):
        return min(pl.price for pl in self.products
                   if pl.published and not pl.non_physical)

    @property
    def price_range_high(self):
        return max(pl.price for pl in self.products
                   if pl.published and not pl.non_physical)

    def check_owner(self, user):
        return any(user == po.user for po in self.ownerships)

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
                ESString('products',
                         filter=lambda products: [pl.name for pl in products]),
                creator=ESMapping(
                    properties=ESMapping(
                        ESString('name', boost=8),
                    ),
                ),
            ))


class ProjectUpdate(Node):
    """
    A status update article associated with a given project.
    """
    __tablename__ = 'project_updates'
    node_id = Column(None, ForeignKey('nodes.id'), primary_key=True)
    project_id = Column(None, ForeignKey('projects.node_id'), nullable=False)

    __mapper_args__ = {'polymorphic_identity': 'ProjectUpdate'}

    def generate_path(self):
        project_path = self.project.canonical_path()
        return '%s/updates/%d' % (project_path, self.id)


class ProjectOwner(Base):
    """
    An association between a project and a user which represents an "owner".
    Includes additional metadata about how the project owner should be
    displayed and what permissions they should have.
    """
    __tablename__ = 'project_owners'
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


class ProjectEmail(Base):
    """
    An e-mail signup that has expressed interest in a project.
    """
    __tablename__ = 'project_emails'
    id = Column(types.Integer, primary_key=True)
    project_id = Column(None, ForeignKey('projects.node_id'), nullable=False)
    email = Column(types.String(255), nullable=False)
    source = Column(types.String(8), nullable=False, default='')
    subscribed_time = Column(types.DateTime, nullable=False,
                             default=utils.utcnow)

    project = orm.relationship('Project', backref='emails')
