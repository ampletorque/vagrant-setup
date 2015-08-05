from sqlalchemy import Table, Column, ForeignKey, types, orm

from . import utils
from .base import Base
from .node import Node
from .address import make_address_columns


provider_type_assoc = Table(
    'providers_provider_types',
    Base.metadata,
    Column('provider_id', None, ForeignKey('providers.node_id'),
           primary_key=True),
    Column('provider_type_id', None, ForeignKey('provider_types.node_id'),
           primary_key=True),
    mysql_engine='InnoDB')


class ProviderType(Node):
    """
    A type of service provider.
    """
    __tablename__ = 'provider_types'
    node_id = Column(None, ForeignKey('nodes.id'), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'ProviderType'}

    def generate_path(self):
        return 'providers/' + utils.to_url_name(self.name)

    @property
    def plural_name(self):
        # XXX
        return self.name


class Provider(Node):
    """
    A service provider in the 'provider database'.
    """
    __tablename__ = 'providers'
    node_id = Column(None, ForeignKey('nodes.id'), primary_key=True)
    email = Column(types.Unicode(255), nullable=False, default=u'')
    home_url = Column(types.String(255), nullable=True)
    mailing = make_address_columns('mailing')

    lat = Column(types.Numeric(9, 6), nullable=True)
    lon = Column(types.Numeric(9, 6), nullable=True)

    __mapper_args__ = {'polymorphic_identity': 'Provider'}

    types = orm.relationship('ProviderType',
                             secondary=provider_type_assoc,
                             collection_class=set,
                             backref='providers')

    def generate_path(self):
        name = self.name or u'provider-%s' % self.id
        provider_path = utils.to_url_name(name)

        types = list(self.types)
        if types:
            first_type = types[0]
            type_path = first_type.canonical_path()
        else:
            type_path = 'providers'

        return type_path + '/' + provider_path
