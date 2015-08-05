from sqlalchemy import Column, ForeignKey, types, orm

from .node import Node


class Creator(Node):
    """
    A project creator.
    """
    __tablename__ = 'creators'
    node_id = Column(None, ForeignKey('nodes.id'), primary_key=True)
    home_url = Column(types.String(255), nullable=True)
    location = Column(types.Unicode(255), nullable=False, default=u'')

    __mapper_args__ = {'polymorphic_identity': 'Creator'}

    projects = orm.relationship(
        'Project',
        backref='creator',
        primaryjoin='Creator.node_id == Project.creator_id',
        cascade='all, delete, delete-orphan')

    @property
    def display_url(self):
        """
        Format the ``home_url`` for more friendly display.
        """
        if not self.home_url:
            return
        # Strip off http:// or https://
        url = self.home_url.split('//', 1)[-1]
        # Strip off www also
        if url.startswith('www.'):
            url = url[4:]
        # Strip off trailing slash
        url = url.rstrip('/')
        return url
