from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import Column, ForeignKey, types, orm
from sqlalchemy.sql import and_

from pyramid_es.mixin import ElasticMixin, ESMapping, ESField, ESString

from . import utils
from .node import Node


class Project(Node, ElasticMixin):
    __tablename__ = 'projects'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    node_id = Column(None, ForeignKey('nodes.id'), primary_key=True)

    creator_id = Column(None, ForeignKey('creators.node_id'), nullable=False)
    vimeo_id = Column(types.Integer, nullable=True)

    gravity = Column(types.Integer, nullable=False, default=0)

    # TO ADD:
    # - homepage_url
    # - open_source_url

    updates = orm.relationship(
        'ProjectUpdate',
        backref='project',
        primaryjoin='ProjectUpdate.project_id == Project.node_id',
    )

    __mapper_args__ = {'polymorphic_identity': 'Project'}

    def generate_path(self):
        creator_path = self.creator.canonical_path()
        name = self.name or u'project-%s' % self.id
        project_path = utils.to_url_name(name)
        return creator_path + '/' + project_path

    def is_live(self):
        return True

    def is_failed(self):
        return False

    @property
    def published_updates(self):
        return [pu for pu in self.updates if pu.published]

    @classmethod
    def elastic_mapping(cls):
        return ESMapping(
            analyzer='content',
            properties=ESMapping(
                ESString('name', boost=5),
                ESString('teaser', boost=3),
                ESString('keywords'),
                # XXX For simplicity we're just passing the non-rendered
                # markdown string to elasticsearch. We're just using it for
                # keyword indexing, so that should work ok for now.
                ESString('body'),
                ESField('published'),
                ESField('listed'),
                # ESField('target'),
                # ESField('start_time'),
                # ESField('end_time'),
                # ESString('levels',
                #          filter=lambda levels: [pl.name for pl in levels]),
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
