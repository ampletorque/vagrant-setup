from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_config, view_defaults
from sqlalchemy.sql import func

from .... import model

from .base import BaseReportsView


@view_defaults(permission='admin')
class PerformanceReportsView(BaseReportsView):
    @view_config(route_name='admin:reports:sales',
                 renderer='admin/reports/sales.html')
    def sales(self):
        utcnow, start_date, end_date, start, end = self._range()
        # over time range

        base_q = model.Session.query(
            func.sum(model.CartItem.price_each * model.CartItem.qty_desired),
            func.sum(model.CartItem.shipping_price)).\
            join(model.CartItem.cart).\
            join(model.Cart.order).\
            filter(model.Order.created_time >= start,
                   model.Order.created_time < end)

        def scalars(q):
            value = q.first()
            if value:
                return (value[0] or 0, value[1] or 0)
            else:
                return 0, 0

        preorder = scalars(base_q.
                           filter(model.CartItem.stage == model.PREORDER))

        stock = scalars(base_q.
                        filter(model.CartItem.stage == model.STOCK))

        crowdfunding_q = base_q.\
            filter(model.CartItem.stage == model.CROWDFUNDING).\
            join(model.CartItem.product).\
            join(model.Product.project)

        funded = scalars(crowdfunding_q.
                         filter(model.Project.successful == True))

        pending = scalars(crowdfunding_q.
                          filter(model.Project.successful == False,
                                 model.Project.end_time >= utcnow))

        failed = scalars(crowdfunding_q.
                         filter(model.Project.successful == False,
                                model.Project.end_time < utcnow))

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
            'start_date': start_date,
            'end_date': end_date,
        }

    @view_config(route_name='admin:reports:project-launches',
                 renderer='admin/reports/project_launches.html')
    def project_launches(self):
        utcnow, start_date, end_date, start, end = self._range()

        # over time range
        # ideally show a graph
        # show breakdown by tag?

        q = model.Session.query(model.Project).\
            filter(model.Project.include_in_launch_stats == True,
                   model.Project.start_time >= start,
                   model.Project.start_time < end)

        num_projects_launched = q.count()

        return {
            'num_projects_launched': num_projects_launched,
            'start_date': start_date,
            'end_date': end_date,
        }

    @view_config(route_name='admin:reports:user-behavior',
                 renderer='admin/reports/user_behavior.html')
    def user_behavior(self):
        # 'up to now', not time range or time specific

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
        num_cross_project_users = model.Session.query(user_subq).\
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

        # XXX for performance it would be good to grab a 'total backers by
        # project' list here.

        return {
            'num_cross_project_users': num_cross_project_users,
            'top_users': top_user_q.all(),
            'top_projects': top_projects_q.all(),
        }

    @view_config(route_name='admin:reports:funding-success',
                 renderer='admin/reports/funding_success.html')
    def funding_success(self):
        utcnow, start_date, end_date, start, end = self._range()

        q = model.Session.query(model.Project).\
            filter(model.Project.include_in_launch_stats == True,
                   model.Project.start_time >= start,
                   model.Project.start_time < end)

        # actual_projects_launched = q.with_entities(model.Project.id,
        #                                            model.Project.name).\
        #     order_by(model.Project.name).\
        #     all()

        num_projects_launched = q.count()

        pending_q = q.filter(model.Project.end_time > utcnow,
                             model.Project.successful == False)
        num_projects_pending = pending_q.count()

        suspended_q = q.filter(model.Project.suspended_time != None)
        num_projects_suspended = suspended_q.count()

        successful_q = q.filter(model.Project.successful == True)
        num_projects_successful = successful_q.count()

        num_projects_completed = (num_projects_launched -
                                  (num_projects_pending +
                                   num_projects_suspended))

        return {
            # 'actual_projects_launched': actual_projects_launched,
            'num_projects_launched': num_projects_launched,
            'num_projects_pending': num_projects_pending,
            'num_projects_suspended': num_projects_suspended,
            'num_projects_completed': num_projects_completed,
            'num_projects_successful': num_projects_successful,
            'start_date': start_date,
            'end_date': end_date,
        }

    @view_config(route_name='admin:reports:delays',
                 renderer='admin/reports/delays.html')
    def delays(self):
        utcnow, start_date, end_date, start, end = self._range()

        delay_bucket = func.round(func.datediff(
            model.CartItem.shipped_time,
            model.CartItem.expected_ship_time), -1).label('delay')
        q = model.Session.query(
            delay_bucket,
            func.count(model.CartItem.id.distinct())).\
            filter(model.CartItem.expected_ship_time != None,
                   model.CartItem.shipped_time >= start,
                   model.CartItem.shipped_time < end).\
            group_by(delay_bucket)
        delay_count = q.all()
        total_count = sum(count for delay, count in delay_count)

        return {
            'start_date': start_date,
            'end_date': end_date,
            'delay_count': delay_count,
            'total_count': total_count,
        }

    @view_config(route_name='admin:reports:project-delays',
                 renderer='admin/reports/project_delays.html')
    def project_delays(self):
        utcnow, start_date, end_date, start, end = self._range()

        delay = func.datediff(
            func.ifnull(model.CartItem.shipped_time, utcnow),
            model.CartItem.expected_ship_time)
        max_delay = func.max(delay).label('worst')
        avg_delay = func.avg(delay).label('average')
        q = model.Session.query(model.Project, max_delay, avg_delay).\
            filter(model.CartItem.expected_ship_time != None,
                   model.CartItem.expected_ship_time < utcnow).\
            join(model.CartItem.product).\
            join(model.Product.project).\
            filter(model.CartItem.status.in_(['shipped', 'in process',
                                              'waiting'])).\
            filter(model.CartItem.stage == model.CartItem.CROWDFUNDING).\
            group_by(model.Project.id).\
            order_by(avg_delay.desc())
        projects = q.all()

        return {
            'projects': projects,
        }

    # XXX consider also a 'problem project' report that shows the worst
    # currently overdue projects and projects that are in need of an update
