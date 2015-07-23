from datetime import timedelta

from sqlalchemy import Column, ForeignKey, types, orm

from . import utils
from .base import Base
from .user_mixin import UserMixin
from .comment import CommentMixin


__all__ = ['LeadSource', 'Lead']


class LeadSource(Base, UserMixin):
    """
    A tracked source of leads.
    """
    __tablename__ = 'lead_sources'
    id = Column(types.Integer, primary_key=True)
    name = Column(types.Unicode(255), nullable=False)
    category = Column(types.String(6), nullable=False, default='')

    available_categories = [('', 'Unknown'),
                            ('person', 'Person'),
                            ('event', 'Event'),
                            ('web', 'Website'),
                            ('media', 'Media Placement'),
                            ('advert', 'Advertisement'),
                            ('other', 'Other')]

    @property
    def category_description(self):
        return dict(self.available_categories)[self.category]


def next_contact_default():
    return utils.utcnow() + timedelta(days=7)


class Lead(Base, UserMixin, CommentMixin):
    """
    A potential lead for a project, which may or may not have 'converted' to a
    launched project.
    """
    __tablename__ = 'leads'
    id = Column(types.Integer, primary_key=True)

    # Summary
    name = Column(types.Unicode(255), nullable=False)
    description = Column(types.UnicodeText, nullable=False, default=u'')
    contact = Column(types.Unicode(255), nullable=False, default=u'')
    assigned_to_id = Column(None, ForeignKey('users.id'), nullable=True)
    last_contact_time = Column(types.DateTime, nullable=True)
    next_contact_time = Column(types.DateTime, nullable=False,
                               default=next_contact_default)

    # Status
    stage = Column(types.String(4), nullable=False, default='unqu')
    eval_time = Column(types.DateTime, nullable=True)
    qual_time = Column(types.DateTime, nullable=True)
    nego_time = Column(types.DateTime, nullable=True)
    prel_time = Column(types.DateTime, nullable=True)
    dead_time = Column(types.DateTime, nullable=True)
    live_time = Column(types.DateTime, nullable=True)

    available_stages = [('unqu', 'Unqualified'),
                        ('eval', 'Evaluation'),
                        ('qual', 'Qualified'),
                        ('nego', 'Negotiation'),
                        ('prel', 'Pre-launch'),
                        ('dead', 'Dead'),
                        ('live', 'Launched')]

    stages_with_color = {
        'unqu': ('Unqualified', 'label-info'),
        'eval': ('Evaluation', ''),
        'qual': ('Qualified', 'label-important'),
        'nego': ('Negotiation', ''),
        'prel': ('Live Pre-launch Page', 'label-success'),
        'dead': ('Dead', 'label-inverse'),
        'live': ('Launched', 'label-success'),
    }

    dead_reason = Column(types.String(7), nullable=True, default='')
    available_dead_reasons = [('cs-rej', 'Rejected by CS'),
                              ('cre-rej', 'Rejected by Creator'),
                              ('unrespo', 'Unresponsive'),
                              ('stalled', 'Indefinitely Stalled')]

    # Discovery
    source_id = Column(None, ForeignKey('lead_sources.id'), nullable=False,
                       default=1)
    is_inbound = Column(types.Boolean(), nullable=False, default=True)
    contact_channel = Column(types.String(6), nullable=False, default='')

    available_contact_channels = [('', 'Unknown'),
                                  ('webfor', 'Web Form'),
                                  ('email', 'Email'),
                                  ('social', 'Social Media'),
                                  ('phone', 'Phone'),
                                  ('person', 'In-person')]

    # Estimates
    initial_est_launch_time = Column(types.DateTime, nullable=True)
    initial_est_tier = Column(types.String(4), nullable=False, default='garb')
    initial_est_six_month_sales = Column(types.Integer(), nullable=False,
                                         default=0)
    initial_est_six_month_percentage = Column(types.Integer(), nullable=False,
                                              default=5)
    refined_est_launch_time = Column(types.DateTime, nullable=True)
    refined_est_tier = Column(types.String(4), nullable=False, default='garb')
    refined_est_six_month_sales = Column(types.Integer(), nullable=False,
                                         default=0)
    refined_est_six_month_percentage = Column(types.Integer(), nullable=False,
                                              default=5)

    available_tiers = [('star', 'Superstar'),
                       ('good', 'Good'),
                       ('fill', 'Filler'),
                       ('garb', 'Garbage')]

    source = orm.relationship('LeadSource', backref='leads')
    assigned_to = orm.relationship('User', foreign_keys=assigned_to_id)
