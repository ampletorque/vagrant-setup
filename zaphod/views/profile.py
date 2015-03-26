from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from sqlalchemy.orm.exc import NoResultFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from .. import model


class ProfileView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='profile', renderer='profile.html')
    def profile(self):
        request = self.request
        path = request.matchdict['path']

        try:
            user = model.Session.query(model.User).\
                filter_by(url_path=path).\
                one()
        except NoResultFound:
            raise HTTPNotFound

        # XXX This includes non-crowdfunding orders, should it?
        projects_backed = set()
        for order in user.orders:
            for ci in order.cart.items:
                projects_backed.add(ci.product.project.id)

        return {
            'user': user,
            'projects_backed': projects_backed,
        }
