from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.request import Request as BaseRequest
from pyramid.decorator import reify

from .model import Session, User
from .content import render_markdown


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

    def node_path(self, obj, suffix=None, **kw):
        """
        Generate a path for a Node instance.
        """
        path = obj.canonical_path(suffix=suffix)
        return self.route_path('node', path=path, **kw)

    def node_url(self, obj, suffix=None, **kw):
        """
        Generate a fully-qualified URL for a Node instance.
        """
        path = obj.canonical_path(suffix=suffix)
        return self.route_url('node', path=path, **kw)

    def render_content(self, obj, body):
        return render_markdown(self, obj, body)
