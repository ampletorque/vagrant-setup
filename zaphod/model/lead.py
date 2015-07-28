from datetime import timedelta
from operator import attrgetter

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
        'unqu': ('Unqualified', 'info'),
        'eval': ('Evaluation', 'default'),
        'qual': ('Qualified', 'important'),
        'nego': ('Negotiation', 'default'),
        'prel': ('Live Pre-launch Page', 'success'),
        'dead': ('Dead', 'inverse'),
        'live': ('Launched', 'success'),
    }

    @property
    def stage_description_with_color(self):
        return self.stages_with_color[self.stage]

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

    def gather_transitions(self):
        transitions = []
        stages = [stage for stage, label in self.available_stages]
        overlapped = zip(stages, stages[1:])
        for from_stage, to_stage in overlapped:
            ts = getattr(self, to_stage + '_time')
            if ts:
                transitions.append(Transition(
                    from_stage=from_stage,
                    to_stage=to_stage,
                    created_time=ts))
        return transitions

    @property
    def events(self):
        """
        Return a list of objects which are either Comment or Transition
        instances, sorted by timestamp.
        """
        events = self.gather_transitions() + self.comments
        events.sort(key=attrgetter('created_time'))
        return events


class Transition(object):
    def __init__(self, from_stage, to_stage, created_time):
        self.from_stage = from_stage
        self.to_stage = to_stage
        self.created_time = created_time

    @property
    def from_stage_description(self):
        return dict(Lead.available_stages)[self.from_stage]

    @property
    def to_stage_description(self):
        return dict(Lead.available_stages)[self.to_stage]
