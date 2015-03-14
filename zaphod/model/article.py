from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import Column, ForeignKey, types

from .node import Node

__all__ = ['Article']


class Article(Node):
    """
    Represents a single-page chunk of arbitrary content on the site.
    """
    __tablename__ = 'articles'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    node_id = Column(None, ForeignKey('nodes.id'), primary_key=True)
    show_heading = Column(types.Boolean, nullable=False, default=True)
    show_article_list = Column(types.Boolean, nullable=False, default=True)

    # This allows articles to be easily grouped into arbitrary categories.
    category = Column(types.Unicode(255), nullable=False, default=u'',
                      index=True, unique=False)

    __mapper_args__ = {'polymorphic_identity': 'Article'}
