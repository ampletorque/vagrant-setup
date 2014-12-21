from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from pyramid.request import Request as BaseRequest
from pyramid.decorator import reify

from .model import Session, User


class Request(BaseRequest):
    @reify
    def user(self):
        user = None
        session = self.session

        if 'user_id' in session:
            user = Session.query(User).get(session['user_id'])

        return user

    def current_path_with_params(self, **kwargs):
        query = self.GET.copy()
        for k, v in kwargs.items():
            if v is None:
                query.pop(k, None)
            else:
                query[k] = v
        return self.current_route_path(_query=query)

    def flash(self, msg, category='info'):
        return self.session.flash((msg, category))
