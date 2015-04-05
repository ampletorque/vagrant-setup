from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import Column, types

from . import utils
from .base import Base

__all__ = ['NewsletterEmail']


class NewsletterEmail(Base):
    """
    An email newsletter signup. If an address signs up in multiple ways, just
    track the first one as source. Notably distinct from ``ProjectEmail``.
    """
    __tablename__ = 'newsletter_emails'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    email = Column(types.String(255), nullable=False, unique=True)
    source = Column(types.String(8), nullable=False, default='')
    created_time = Column(types.DateTime, nullable=False,
                          default=utils.utcnow)

    available_sources = (('signup', 'Direct Mailing List Sign-Up'),
                         ('stock', 'In-Stock Notification'),
                         ('order', 'Placed Order'),
                         ('interact', 'User Interaction'),
                         ('account', 'Created Account'),
                         ('import', 'Admin Import'))

    @property
    def source_description(self):
        """
        A human readable description of the originating source of this email
        address record.
        """
        return dict(self.available_sources).get(self.source)
