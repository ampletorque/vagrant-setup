from sqlalchemy import Table, Column, ForeignKey, orm

from .base import Base
from .node import Node


project_tags = Table(
    'project_tags',
    Base.metadata,
    Column('project_id', None, ForeignKey('projects.node_id'),
           primary_key=True),
    Column('tag_id', None, ForeignKey('tags.node_id'), primary_key=True),
    mysql_engine='InnoDB')


class Tag(Node):
    """
    A tag that can be associated with projets to group similar projects
    together for browsing and searching.
    """
    __tablename__ = 'tags'
    node_id = Column(None, ForeignKey('nodes.id'), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'Tag'}

    projects = orm.relationship('Project',
                                secondary=project_tags,
                                collection_class=set,
                                backref=orm.backref('tags',
                                                    collection_class=set))
