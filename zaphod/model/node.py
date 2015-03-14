from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy import Column, ForeignKey, orm, types
from sqlalchemy.orm.exc import NoResultFound

from . import utils
from .base import Base, Session
from .image import ImageMixin
from .user_mixin import UserMixin
from .comment import CommentMixin

__all__ = ['Alias', 'Node']


class Alias(Base):
    """
    Represents a URL path where a Node will be served up. A .canonical flag
    indicates that this is the canonical address--other addresses should 301 to
    the canonical alias.
    """
    __tablename__ = 'aliases'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    path = Column(types.String(255), primary_key=True)
    node_id = Column(None, ForeignKey('nodes.id'), nullable=False)
    canonical = Column(types.Boolean, nullable=False, default=True)
    node = orm.relationship('Node')

    @orm.validates('path')
    def validate_path(self, k, v):
        assert utils.is_url_name(v)
        return v


class Node(Base, ImageMixin, UserMixin, CommentMixin):
    """
    The Node class is the superclass of all pieces of content which are served
    up at a URL. It provides an easy way to make a flat URL namespace (combined
    with Alias) and a few other helpful features.
    """
    __tablename__ = 'nodes'
    __table_args__ = {'mysql_engine': 'InnoDB'}
    id = Column(types.Integer, primary_key=True)
    discriminator = Column(types.String(32), nullable=False)
    name = Column(types.Unicode(255), nullable=False, default=u'')

    keywords = Column(types.UnicodeText, nullable=False, default=u'')
    teaser = Column(types.UnicodeText, nullable=False, default=u'')
    body = Column(types.UnicodeText, nullable=False, default=u'')

    published = Column(types.Boolean, nullable=False, default=False)
    use_custom_paths = Column(types.Boolean, nullable=False, default=False)
    listed = Column(types.Boolean, nullable=False, default=True)
    __mapper_args__ = {'polymorphic_on': discriminator,
                       'polymorphic_identity': 'Node'}

    aliases = orm.relationship('Alias', cascade='all, delete, delete-orphan')

    def __init__(self, *args, **kwargs):
        override_path = kwargs.pop('override_path', None)
        Base.__init__(self, *args, **kwargs)
        self.override_path = override_path

    def generate_path(self):
        """
        Generate the recommended path for this node. This may be overridden in
        subclasses to customize automatically generated paths.
        """
        name = self.name or u'node-%s' % self.id
        return utils.to_url_name(name)

    def canonical_path(self, suffix=None):
        """
        Get the canonical path for this node.
        """
        path = None
        for alias in self.aliases:
            if alias.canonical:
                path = alias.path

        assert path, "node has no canonical alias"

        if suffix:
            path = path + '/' + ('/'.join(suffix))

        return path

    def update_path(self, path):
        """
        Update the canonical path for this node. This will leave behind
        redirect aliases from previous paths, although those redirects may be
        overridden if other nodes are updated to the previous paths.
        """
        # Make all existing aliases for this node non-canonical.
        for aa in self.aliases:
            aa.canonical = False

        try:
            alias = Session.query(Alias).filter_by(path=path).one()
        except NoResultFound:
            alias = Alias(path=path, node=self, canonical=True)
            self.aliases.append(alias)
        else:
            if alias.node == self:
                alias.canonical = True
            elif not alias.canonical:
                # If it's not canonical and pointing to another node, we can
                # replace it.
                alias.node = self
                alias.canonical = True
            else:
                # If it is canonical and pointing to another node, we can't
                # replace it, so fail.
                raise ValueError("Provided path is not unique.")

    @property
    def override_path(self):
        """
        A property to simplify building interfaces that manage node paths.
        Getting the property will return None unless the path has been manually
        overridden, in which case the override path will be returned.
        Similarly, setting the property to None will make the node use an
        automatically generated path, setting a non-None path will override it.
        """
        if self.use_custom_paths:
            return self.canonical_path()

    @override_path.setter
    def override_path(self, path):
        if path:
            self.use_custom_paths = True
            self.update_path(path)
        else:
            self.use_custom_paths = False
            self.update_path(self.generate_path())
