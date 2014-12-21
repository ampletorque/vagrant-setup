from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

from pyramid.security import Authenticated, Everyone

from sqlalchemy.orm.exc import NoResultFound

from .model import Session, User


log = logging.getLogger(__name__)


class AuthenticationPolicy(object):

    def authenticated_userid(self, request):
        """Return user ID if user (still) exists in database."""
        userid = self.unauthenticated_userid(request)
        if userid is not None:
            q = Session.query(User.id)
            q = q.filter_by(id=userid)
            q = q.filter_by(enabled=True)
            try:
                q.one()
            except NoResultFound:
                return None
            else:
                return userid
        return None

    def unauthenticated_userid(self, request):
        """Return user ID from session."""
        if 'user_id' in request.session:
            return request.session['user_id']

    def effective_principals(self, request):
        """Get principals for user.

        Principals are strings that identify a user or group.

        The list will always include the built-in principal ``Everyone``. If
        there's a logged in user, it will also include ``Authenticated`` and
        the user ID.

        The values returned from this function are passed to the
        authorization policy when a view is configured with a
        ``permission``.

        """
        principals = [Everyone]
        user_id = self.unauthenticated_userid(request)
        if user_id is not None:
            if self.authenticated_userid(request) is not None:
                principals += [Authenticated, user_id]
        return principals

    def remember(self, request, user_id, user, remember=False):
        """Called by the login view to "remember" the user.

        Remembering the user means setting some keys in the session.

        """
        session = request.session
        session.set('user_id', user_id, clientside=True, permanent=remember)
        log.info(
            'login %d/%s remember:%s', user.id, user.email, remember)

    def forget(self, request):
        id = request.session.pop('user_id', None)
        email = request.user and request.user.email
        log.info('logout %s/%s', id, email)


class AuthorizationPolicy(object):

    def permits(self, context, principals, permission):
        if Authenticated not in principals:
            return False

        request = context.request
        assert request.user

        if permission == 'authenticated':
            return True

        return getattr(request.user, permission, False)

    def principals_allowed_by_permission(self, context, permission):
        raise NotImplementedError


def includeme(config):
    config.set_authentication_policy(AuthenticationPolicy())
    config.set_authorization_policy(AuthorizationPolicy())
