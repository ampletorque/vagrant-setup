from __future__ import (absolute_import, print_function, division,
                        unicode_literals)

from sqlalchemy import Column, ForeignKey, types, orm
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.orderinglist import ordering_list

import six

from . import utils
from .base import Base
from .user_mixin import UserMixin

__all__ = ['ImageMixin', 'ImageMeta']


class ImageMixin(object):
    """
    Mixin class to add associated images to an object.
    """
    @declared_attr
    def image_associations(cls):
        if not issubclass(cls, Base):
            return

        table_name = cls.__tablename__
        if six.PY3:
            type_name = cls.__name__ + 'ImageAssociation'
        else:
            type_name = cls.__name__ + b'ImageAssociation'

        ImageAssociation = type(
            type_name,
            (Base,),
            dict(__tablename__='%s_image_metas' % table_name,
                 source_id=Column("source_id", None,
                                  ForeignKey('%s.id' % table_name),
                                  primary_key=True),
                 image_meta_id=Column("image_meta_id", None,
                                      ForeignKey('image_metas.id'),
                                      primary_key=True),
                 gravity=Column("gravity", types.Integer, nullable=False,
                                default=0),

                 source=orm.relationship(cls),
                 image_meta=orm.relationship('ImageMeta', innerjoin=True,
                                             lazy="joined"),
                 published=Column(types.Boolean, nullable=False, default=True),
                 caption=Column(types.Unicode(255), nullable=False,
                                default=u'')))

        def creator(image_meta):
            return ImageAssociation(image_meta=image_meta)

        cls.ImageAssociation = ImageAssociation

        cls.image_metas = association_proxy('image_associations',
                                            'image_meta',
                                            creator=creator)

        return orm.relationship(ImageAssociation,
                                collection_class=ordering_list('gravity'),
                                order_by=ImageAssociation.gravity,
                                cascade='all, delete-orphan')

    def img(self, request, chain=None, class_=None, id=None, qualified=False):
        # XXX Improve this for performance...
        if self.image_metas:
            im = self.image_metas[0]
            return request.image_tag(im.name, im.original_ext, chain,
                                     title=im.title, alt=im.alt,
                                     class_=class_, id=id, qualified=qualified)

    def img_url(self, request, chain=None, qualified=False):
        # XXX Improve this for performance...
        if self.image_metas:
            im = self.image_metas[0]
            return request.image_url(im.name, im.original_ext, chain,
                                     qualified=qualified)


class ImageMeta(Base, UserMixin):
    """
    A record of an image associated with any content or used independently.
    Note that the actual image data is stored on disk as a normal image file,
    so only the image metadata and the associations to other objects are stored
    in the DB.
    """
    __tablename__ = 'image_metas'
    admin_handler = 'images'

    id = Column(types.Integer, primary_key=True)
    # Combined with the filter suffix to generate the filename.
    name = Column(types.String(255), nullable=False, unique=True)
    # This text is shown as the alt attribute when embedded.
    alt = Column(types.Unicode(255), nullable=False, default=u'')
    # This text is shown as the title attribute when embedded.
    title = Column(types.Unicode(255), nullable=False, default=u'')
    # Original file extension (jpg | gif | png | tif | bmp | ico | psd)
    original_ext = Column(types.String(3), nullable=False)
    width = Column(types.Integer, nullable=False, default=0)
    height = Column(types.Integer, nullable=False, default=0)

    @orm.validates('name')
    def validate_name(self, k, v):
        assert utils.is_url_name(v)
        return v
