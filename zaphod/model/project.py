from sqlalchemy import Column, ForeignKey, types

from . import utils
from .node import Node


class Project(Node):
    __tablename__ = 'projects'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    node_id = Column(None, ForeignKey('nodes.id'), primary_key=True)

    creator_id = Column(None, ForeignKey('creators.node_id'), nullable=False)
    vimeo_id = Column(types.Integer, nullable=True)

    __mapper_args__ = {'polymorphic_identity': 'Project'}

    def generate_path(self):
        creator_path = self.creator.canonical_path()
        name = self.name or u'project-%s' % self.id
        project_path = utils.to_url_name(name)
        return creator_path + '/' + project_path

    def is_live(self):
        return True
