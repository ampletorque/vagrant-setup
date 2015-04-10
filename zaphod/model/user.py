from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import hashlib

from datetime import timedelta

from cryptacular.bcrypt import BCRYPTPasswordManager
from sqlalchemy import Column, types, orm

from pyramid_es.mixin import ElasticMixin, ESMapping, ESField, ESString

from . import utils
from .base import Base
from .image import ImageMixin
from .user_mixin import UserMixin
from .comment import CommentMixin

__all__ = ['User']


class User(Base, ImageMixin, UserMixin, CommentMixin, ElasticMixin):
    """
    A user account.
    """
    __tablename__ = 'users'
    id = Column(types.Integer, primary_key=True)
    name = Column(types.Unicode(255), nullable=False)
    email = Column(types.String(255), nullable=False, unique=True)
    hashed_password = Column(types.String(60), nullable=True)
    password_reset_token = Column(types.String(64), nullable=False, default='')
    password_reset_time = Column(types.DateTime, nullable=False,
                                 default=utils.utcnow)

    enabled = Column(types.Boolean, nullable=False, default=True)
    admin = Column(types.Boolean, nullable=False, default=False)
    show_admin_bars = Column(types.Boolean, nullable=False, default=False)

    url_path = Column(types.String(255), nullable=True, unique=True)
    timezone = Column(types.String(255), nullable=False,
                      default='America/Los_Angeles')

    twitter_username = Column(types.String(255), nullable=True)

    show_in_backers = Column(types.Boolean, nullable=False, default=True)
    show_location = Column(types.Unicode(255), nullable=False, default=u'')
    show_name = Column(types.Unicode(255), nullable=False, default=u'')

    # It's necessary to use post_update=True on these relationships so that
    # they do not get populated until after rows are created, in case of a
    # self-referential relationship. E.g. the root User is also going to be
    # created by itself.
    created_by = orm.relationship(
        'User',
        foreign_keys='User.created_by_id',
        remote_side='User.id',
        post_update=True)

    updated_by = orm.relationship(
        'User',
        foreign_keys='User.updated_by_id',
        remote_side='User.id',
        post_update=True)

    @staticmethod
    def hash_password(password):
        """
        Hash a password to store it in the database or verify against a
        database.

        The default bcrypt work factor is 12, but that makes logins a bit
        slow, so we use 11.

        :param password:
          Plaintext password, as a unicode string.

        :return:
          Bcrypt-hashed password. If provided password is ``None``, returns
          ``None``.
        """
        if password is None:
            return None
        else:
            assert len(password) < 255, \
                "passwords > 255 characters not allowed"
            manager = BCRYPTPasswordManager()
            return manager.encode(password, rounds=11)

    @staticmethod
    def generate_token():
        """
        Generate a password reset token.

        :return:
          Return a nonce to be used in URLs for validating password resets.
        """
        s = os.urandom(256) + str(id({})).encode('utf8')
        return hashlib.sha256(s).hexdigest()

    def set_reset_password_token(self):
        """
        Generate a password reset token, set it, and return it. If there is an
        existing reset token that was generated in the last 60 seconds, don't
        generate a new one, and just return the existing one.

        :return:
          Nonce as created by generate_token().
        """
        utcnow = utils.utcnow()
        # Check to make sure the password token wasn't just generated: if it
        # was, return the same one. If it doesn't exist, force generation.
        if (not self.password_reset_token or
                self.password_reset_time < utcnow - timedelta(hours=6)):
            self.password_reset_time = utcnow
            self.password_reset_token = User.generate_token()
        return self.password_reset_token

    def clear_reset_password_token(self):
        """
        Clear any previously set password reset token.
        """
        self.password_reset_token = ''
        self.password_reset_time = utils.utcnow()

    def update_password(self, value):
        """
        Given a new plaintext password, hash it and update the password field.
        Passing ``None`` for the plaintext password will clear the hashed
        password field, and make it impossible for that user to login.

        :param value:
          Plaintext password, as a unicode string.
        """
        if value is None:
            self.hashed_password = None
        else:
            self.hashed_password = User.hash_password(value)

    @property
    def password(self):
        return ''

    @password.setter
    def password(self, value):
        self.update_password(value)

    def check_password(self, password):
        """
        Check a plaintext password against our hashed password.

        :param password:
          Plaintext password, as a unicode string.

        :return:
          True if the password is correct, False otherwise.
        """
        assert len(password) < 255, "passwords > 255 characters not allowed"
        hsh = self.hashed_password
        manager = BCRYPTPasswordManager()
        return hsh and manager.check(hsh, password)

    @classmethod
    def elastic_mapping(cls):
        return ESMapping(
            analyzer='content',
            properties=ESMapping(
                ESField('id'),
                ESString('name'),
                ESString('email'),
            ))
