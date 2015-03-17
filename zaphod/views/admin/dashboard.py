from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytz
from datetime import datetime, time
from sqlalchemy.sql import func

from pyramid.view import view_config

from ... import model


class DashboardView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='admin:dashboard', renderer='admin/dashboard.html',
                 permission='authenticated')
    def index(self):
        assert request.user.has_permission('admin'), \
            "non-admin has admin interface access"

        utcnow = datetime.utcnow()

        active_crowdfunding_q = model.Session.query(model.Project).\
            filter(model.Project.start_time < utcnow,
                   model.Project.end_time >= utcnow,
                   model.Project.published == True,
                   model.Project.listed == True)

        available_q = model.Session.query(model.Project).\
            filter(model.Project.published == True,
                   model.Project.listed == True,
                   model.Project.accepts_preorders == True)

        order_q = model.Session.query(model.Order)

        user_q = model.Session.query(model.User)

        utcnow = datetime.utcnow()
        report_tz = pytz.timezone('America/Los_Angeles')
        now_local = pytz.utc.localize(utcnow).astimezone(report_tz)
        today_start_local = datetime.combine(now_local.date(), time())
        today_start_utc = report_tz.localize(today_start_local).\
            astimezone(pytz.utc).replace(tzinfo=None)

        sales_today_total = model.Session.query(
            func.sum((model.CartItem.price_each * model.CartItem.qty_desired) +
                     model.CartItem.shipping_price)).\
            join(model.CartItem.cart).\
            join(model.Cart.order).\
            filter(model.Order.created_time >= today_start_utc).\
            scalar() or 0

        orders_today_q = model.Session.query(model.Order).\
            filter(model.Order.created_time >= today_start_utc)

        return {
            'crowdfunding_project_count': active_crowdfunding_q.count(),
            'available_project_count': available_q.count(),
            'order_count': order_q.count(),
            'user_count': user_q.count(),
            'sales_today_total': sales_today_total,
            'orders_today_count': orders_today_q.count(),
        }
