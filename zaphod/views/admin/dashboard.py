from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime

from pyramid.view import view_config

from ... import model


class DashboardView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='admin:dashboard', renderer='admin/dashboard.html',
                 permission='authenticated')
    def index(self):
        utcnow = datetime.utcnow()

        active_crowdfunding_q = model.Session.query(model.Project).\
            filter(model.Project.start_time < utcnow,
                   model.Project.end_time >= utcnow,
                   model.Project.published == True)

        available_q = model.Session.query(model.Project).\
            filter(model.Project.published == True,
                   model.Project.accepts_preorders == True)

        order_q = model.Session.query(model.Order)

        user_q = model.Session.query(model.User)

        return {
            'crowdfunding_project_count': active_crowdfunding_q.count(),
            'available_project_count': available_q.count(),
            'order_count': order_q.count(),
            'user_count': user_q.count(),
        }
