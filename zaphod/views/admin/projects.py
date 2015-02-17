from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults, view_config
from venusian import lift
from sqlalchemy.sql import func, not_
from formencode import validators

from ... import model

from .base import NodeEditView, NodeListView, NodeUpdateForm


@view_defaults(route_name='admin:projects', renderer='admin/projects.html')
@lift()
class ProjectListView(NodeListView):
    cls = model.Project


@view_defaults(route_name='admin:project', renderer='admin/project.html')
@lift()
class ProjectEditView(NodeEditView):
    cls = model.Project

    class UpdateForm(NodeUpdateForm):
        "Schema for validating project update form."
        prelaunch_vimeo_id = validators.Int()
        prelaunch_teaser = validators.UnicodeString()
        prelaunch_body = validators.UnicodeString()

        crowdfunding_vimeo_id = validators.Int()
        # Crowdfunding teaser and body are handled by the base node schema

        available_vimeo_id = validators.Int()
        available_teaser = validators.UnicodeString()
        available_body = validators.UnicodeString()

        target = validators.Number()
        start_time = validators.DateConverter()
        # Remember we probably want to add a day to this value.
        end_time = validators.DateConverter()
        gravity = validators.Int(not_empty=True)

        accepts_preorders = validators.Bool()
        pledged_elsewhere_count = validators.Int()
        pledged_elsewhere_amount = validators.Number()
        launched_elsewhere = validators.Bool()

    @view_config(route_name='admin:project:products',
                 renderer='admin/project_products.html')
    def products(self):
        project = self._get_object()
        return {'obj': project}

    @view_config(route_name='admin:project:owners',
                 renderer='admin/project_owners.html')
    def owners(self):
        project = self._get_object()
        return {'obj': project}

    @view_config(route_name='admin:project:updates',
                 renderer='admin/project_updates.html')
    def updates(self):
        project = self._get_object()
        return {'obj': project}

    @view_config(route_name='admin:project:reports',
                 renderer='admin/project_reports.html')
    def reports(self):
        project = self._get_object()
        return {'obj': project}

    @view_config(route_name='admin:project:reports:funding',
                 renderer='admin/project_funding.html')
    def funding(self):
        project = self._get_object()
        return {'obj': project}

    @view_config(route_name='admin:project:reports:status',
                 renderer='admin/project_status.html')
    def status(self):
        project = self._get_object()
        return {'obj': project}

    @view_config(route_name='admin:project:reports:balance',
                 renderer='admin/project_balance.html')
    def balance(self):
        project = self._get_object()
        return {'obj': project}

    @view_config(route_name='admin:project:reports:skus',
                 renderer='admin/project_skus.html')
    def skus(self):
        project = self._get_object()

        base_q = model.Session.query(model.SKU,
                                     func.count('*')).\
            join(model.SKU.cart_items).\
            join(model.CartItem.cart).\
            join(model.Cart.order).\
            join(model.SKU.product).\
            filter(model.Product.project_id == project.id).\
            group_by(model.SKU.id)

        ordered_q = base_q.\
            filter(not_(model.CartItem.status.in_(
                ['cancelled', 'shipped', 'abandoned'])))
        qty_ordered = dict(ordered_q.all())

        delivered_q = base_q.\
            filter(model.CartItem.status == 'shipped')
        qty_delivered = dict(delivered_q.all())

        due_q = model.Session.query(
            model.SKU,
            func.min(model.CartItem.expected_delivery_date)).\
            join(model.SKU.cart_items).\
            join(model.CartItem.cart).\
            join(model.Cart.order).\
            join(model.SKU.product).\
            filter(model.Product.project_id == project.id).\
            group_by(model.SKU.id)
        earliest_due_date = dict(due_q.all())

        return {
            'obj': project,
            'qty_ordered': qty_ordered,
            'qty_delivered': qty_delivered,
            'earliest_due_date': earliest_due_date,
        }
