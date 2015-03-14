from __future__ import (absolute_import, print_function, division,
                        unicode_literals)

from datetime import timedelta

from sqlalchemy import Column, ForeignKey, types, orm

from . import utils
from .base import Base
from .user_mixin import UserMixin
from .comment import CommentMixin


__all__ = ['LeadSource', 'Lead']


class LeadSource(Base):
    """
    A tracked source of leads.
    """
    __tablename__ = 'lead_sources'
    id = Column(types.Integer, primary_key=True)
    name = Column(types.Unicode(255), nullable=False)


def next_contact_default():
    return utils.utcnow() + timedelta(days=5)


class Lead(Base, UserMixin, CommentMixin):
    """
    A potential lead for a project, which may or may not have 'converted' to a
    launched project.
    """
    __tablename__ = 'leads'
    id = Column(types.Integer, primary_key=True)
    name = Column(types.Unicode(255), nullable=False)
    description = Column(types.UnicodeText, nullable=False, default=u'')
    notes = Column(types.UnicodeText, nullable=False, default=u'')
    discount = Column(types.Unicode(255), nullable=False, default=u'')

    status = Column(types.String(4), nullable=False, default='prec')
    opp_time = Column(types.DateTime, nullable=True)
    cred_time = Column(types.DateTime, nullable=True)
    prel_time = Column(types.DateTime, nullable=True)
    dead_time = Column(types.DateTime, nullable=True)
    live_time = Column(types.DateTime, nullable=True)

    assigned_to_id = Column(None, ForeignKey('users.id'), nullable=True)
    referred_by_id = Column(None, ForeignKey('users.id'), nullable=True)

    source_id = Column(None, ForeignKey('lead_sources.id'), nullable=False,
                       default=1)
    contact_point = Column(types.String(6), nullable=False, default='')

    last_contact_time = Column(types.DateTime, nullable=True)
    next_contact_time = Column(types.DateTime, nullable=False,
                               default=next_contact_default)

    estimated_launch_time = Column(types.DateTime, nullable=True)
    campaign_duration_days = Column(types.Integer, nullable=True)

    email = Column(types.Unicode(255), nullable=False, default=u'')
    phone = Column(types.Unicode(255), nullable=False, default=u'')
    person = Column(types.Unicode(255), nullable=False, default=u'')

    available_statuses = [('prec', 'Pre-Contact'),
                          ('opp', 'Opportunity'),
                          ('cred', 'Credible'),
                          ('prel', 'Prelaunch'),
                          ('dead', 'Dead'),
                          ('live', 'Launched')]

    statuses_with_color = {
        'prec': ('Pre-Contact', 'label-info'),
        'opp': ('Opportunity', ''),
        'cred': ('Credible', 'label-important'),
        'prel': ('Prelaunch', 'label-success'),
        'dead': ('Dead', 'label-inverse'),
        'live': ('Launched', 'label-success'),
    }

    available_contact_points = [('', 'Unknown'),
                                ('phone', 'Phone'),
                                ('chat', 'In-Person'),
                                ('other', 'Other CF Site'),
                                ('email', 'Email'),
                                ('form', 'Web Form'),
                                ('out', 'Outbound')]

    source = orm.relationship('LeadSource', backref='leads')

    assigned_to = orm.relationship('User', foreign_keys=assigned_to_id)
    referred_by = orm.relationship('User', foreign_keys=referred_by_id)

    @property
    def new_source(self):
        return u''

    @new_source.setter
    def new_source(self, value):
        self.source = LeadSource(name=value)
