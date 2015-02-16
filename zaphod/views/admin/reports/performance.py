from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config
from sqlalchemy.sql import func

from .... import model


class SalesView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='admin:reports:sales',
                 renderer='admin/reports/sales.html',
                 permission='authenticated')
    def sales(self):
        utcnow = model.utcnow()

        base_q = model.Session.query(
            func.sum(model.CartItem.price_each * model.CartItem.qty_desired),
            func.sum(model.CartItem.shipping_price))

        preorder = base_q.\
            filter(model.CartItem.stage == model.PREORDER).\
            first() or (0, 0)

        stock = base_q.\
            filter(model.CartItem.stage == model.STOCK).\
            first() or (0, 0)

        crowdfunding_q = base_q.\
            filter(model.CartItem.stage == model.CROWDFUNDING).\
            join(model.CartItem.product).\
            join(model.Product.project)

        funded = crowdfunding_q.\
            filter(model.Project.successful == True).\
            first() or (0, 0)

        pending = crowdfunding_q.\
            filter(model.Project.successful == False,
                   model.Project.end_time >= utcnow).\
            first() or (0, 0)

        failed = crowdfunding_q.\
            filter(model.Project.successful == False,
                   model.Project.end_time < utcnow).\
            first() or (0, 0)

        total = (
            (stock[0] +
             preorder[0] +
             pending[0] +
             funded[0]),
            (stock[1] +
             preorder[1] +
             pending[1] +
             funded[1])
        )

        return {
            'stock': stock,
            'preorder': preorder,
            'pending': pending,
            'failed': failed,
            'funded': funded,
            'total': total,
        }


class UserBehaviorView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='admin:reports:user-behavior',
                 renderer='admin/reports/user_behavior.html',
                 permission='authenticated')
    def user_behavior(self):
        user_q = model.Session.query(
            model.User.id,
            func.count(model.Project.id.distinct()).label('num_projects')).\
            join(model.User.orders).\
            join(model.Order.cart).\
            join(model.Cart.items).\
            join(model.CartItem.product).\
            join(model.Product.project).\
            filter(model.User.admin == False).\
            group_by(model.User.id)
        user_subq = user_q.subquery()

        # number of users that have backed multiple projects.
        cross_project_user_count = model.Session.query(user_subq).\
            filter(user_subq.c.num_projects > 1).\
            count()

        # top 20 users ranked by number of projects they have backed
        top_user_q = model.Session.query(model.User,
                                         user_subq.c.num_projects).\
            join(user_subq,
                 (model.User.id == user_subq.c.id)).\
            filter(user_subq.c.num_projects > 1).\
            order_by(user_subq.c.num_projects.desc()).\
            limit(20)

        # projects ranked by number of multi-project users that backed them
        num_users_col = func.count(user_subq.c.id.distinct())
        top_projects_q = model.Session.query(model.Project, num_users_col).\
            join(model.Order.cart).\
            join(model.Cart.items).\
            join(model.CartItem.product).\
            join(model.Product.project).\
            join(user_subq,
                 (user_subq.c.id == model.Order.user_id)).\
            filter(user_subq.c.num_projects > 1).\
            group_by(model.Project.id).\
            order_by(num_users_col.desc())

        return {
            'cross_project_user_count': cross_project_user_count,
            'top_users': top_user_q.all(),
            'top_projects': top_projects_q.all(),
        }
