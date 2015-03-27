from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyramid.view import view_defaults, view_config
from venusian import lift
from sqlalchemy.sql import func, not_
from formencode import Schema, NestedVariables, ForEach, validators
from pyramid.httpexceptions import HTTPFound

from pyramid_uniform import Form, FormRenderer, crud_update

from ... import model

from ...admin import (NodeEditView, NodeListView, NodeUpdateForm,
                      NodeCreateView, NodeCreateForm)


class ProductCreateForm(Schema):
    allow_extra_fields = False
    name = validators.UnicodeString(not_empty=True)


class OwnerSchema(Schema):
    allow_extra_fields = False
    user_id = validators.Int(not_empty=True)
    title = validators.UnicodeString()
    gravity = validators.Int(if_empty=0)
    can_change_content = validators.Bool()
    can_post_updates = validators.Bool()
    can_receive_questions = validators.Bool()
    can_manage_payments = validators.Bool()
    can_manage_owners = validators.Bool()
    show_on_campaign = validators.Bool()


class OwnersForm(Schema):
    allow_extra_fields = False
    pre_validators = [NestedVariables()]
    owners = ForEach(OwnerSchema)


class OwnerCreateForm(Schema):
    allow_extra_fields = False
    user_id = validators.Int(not_empty=True)


@view_defaults(route_name='admin:projects', renderer='admin/projects.html',
               permission='admin')
@lift()
class ProjectListView(NodeListView):
    cls = model.Project


@view_defaults(route_name='admin:project', renderer='admin/project.html',
               permission='admin')
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
        start_time = validators.DateConverter(month_style='yyyy/mm/dd')
        # XXX FIXME Remember we probably want to add a day to this value.
        end_time = validators.DateConverter(month_style='yyyy/mm/dd')
        gravity = validators.Int(not_empty=True)

        accepts_preorders = validators.Bool()
        pledged_elsewhere_count = validators.Int()
        pledged_elsewhere_amount = validators.Number()
        include_in_launch_stats = validators.Bool()

    def _update_object(self, form, obj):
        NodeEditView._update_object(self, form, obj)
        self.request.theme.invalidate_project(obj.id)

    @view_config(route_name='admin:project:products',
                 renderer='admin/project_products.html')
    def products(self):
        project = self._get_object()
        return {'obj': project}

    @view_config(route_name='admin:project:products:new',
                 renderer='admin/project_products_new.html')
    def create_product(self):
        request = self.request
        project = self._get_object()

        form = Form(request, schema=ProductCreateForm)
        if form.validate():
            product = model.Product(project=project)
            form.bind(product)
            model.Session.flush()
            request.flash("Product created.", 'success')
            request.theme.invalidate_project(project.id)
            self._touch_object(project)
            return HTTPFound(location=request.route_url('admin:product',
                                                        id=product.id))

        return {'obj': project, 'renderer': FormRenderer(form)}

    @view_config(route_name='admin:project:owners',
                 renderer='admin/project_owners.html')
    def owners(self):
        request = self.request
        project = self._get_object()

        form = Form(request, schema=OwnersForm)
        if form.validate():
            for owner_params in form.data['owners']:
                po = model.Session.query(model.ProjectOwner).\
                    filter_by(project_id=project.id,
                              user_id=owner_params['user_id']).\
                    one()
                crud_update(po, owner_params)
            request.flash("Updated owners.", 'success')
            request.theme.invalidate_project(project.id)
            self._touch_object(project)
            return HTTPFound(location=request.current_route_url())

        return {'obj': project, 'renderer': FormRenderer(form)}

    @view_config(route_name='admin:project:owners:new',
                 renderer='admin/project_owners_new.html')
    def create_owner(self):
        request = self.request
        project = self._get_object()

        form = Form(request, schema=OwnerCreateForm)
        if form.validate():
            po = model.ProjectOwner(project=project)
            form.bind(po)
            request.flash("Project owner added.", 'success')
            request.theme.invalidate_project(project.id)
            self._touch_object(project)
            return HTTPFound(
                location=request.route_url('admin:project:owners',
                                           id=project.id))

        return {'obj': project, 'renderer': FormRenderer(form)}

    @view_config(route_name='admin:project:updates',
                 renderer='admin/project_updates.html')
    def updates(self):
        project = self._get_object()
        return {'obj': project}

    @view_config(route_name='admin:project:updates:new',
                 renderer='admin/project_updates_new.html')
    def create_update(self):
        request = self.request
        project = self._get_object()

        form = Form(request, schema=NodeCreateForm)
        if form.validate():
            update = model.ProjectUpdate(project=project)
            form.bind(update)
            model.Session.flush()
            request.flash("Project update created.", 'success')
            request.theme.invalidate_project(project.id)
            self._touch_object(project)
            return HTTPFound(location=request.route_url('admin:update',
                                                        id=update.id))

        return {'obj': project, 'renderer': FormRenderer(form)}

    @view_config(route_name='admin:project:emails',
                 renderer='admin/project_emails.html')
    def emails(self):
        project = self._get_object()

        q = model.Session.query(model.ProjectEmail.source,
                                func.count('*')).\
            filter(model.ProjectEmail.project == project).\
            group_by(model.ProjectEmail.source)
        counts = dict(q.all())

        emails = model.Session.query(model.ProjectEmail).\
            filter(model.ProjectEmail.project == project).\
            order_by(model.ProjectEmail.id.desc())

        return {
            'obj': project,
            'counts': counts,
            'emails': emails,
        }

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
        utcnow = model.utcnow()

        orders_q = model.Session.query(model.Order).\
            join(model.Order.cart).\
            join(model.Cart.items).\
            join(model.CartItem.product).\
            filter(model.Product.project == project)

        # - # of orders that are open
        open_orders_q = orders_q.\
            filter(not_(model.CartItem.status.in_(['failed', 'cancelled',
                                                   'shipped', 'abandoned'])))
        open_orders_count = open_orders_q.count()

        # - # of orders that are currently late
        late_orders_q = open_orders_q.\
            filter(model.CartItem.expected_ship_time < utcnow)
        late_orders_count = late_orders_q.count()

        # - earliest open delivery date
        earliest_open_ship_time = open_orders_q.with_entities(
            func.min(model.CartItem.expected_ship_time)).\
            scalar()

        # - age of latest project update
        last_update_time = \
            model.Session.query(model.ProjectUpdate.created_time).\
            filter(model.ProjectUpdate.project == project).\
            order_by(model.ProjectUpdate.id.desc()).\
            scalar()

        # - warn if an update is "needed"

        return {
            'obj': project,
            'open_orders_count': open_orders_count,
            'late_orders_count': late_orders_count,
            'earliest_open_ship_time': earliest_open_ship_time,
            'last_update_time': last_update_time,
        }

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
                ['cancelled', 'abandoned'])))
        qty_ordered = dict(ordered_q.all())

        delivered_q = base_q.\
            filter(model.CartItem.status == 'shipped')
        qty_delivered = dict(delivered_q.all())

        due_q = model.Session.query(
            model.SKU,
            func.min(model.CartItem.expected_ship_time)).\
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

    @view_config(route_name='admin:project:ship',
                 renderer='admin/project_ship.html')
    def ship(self):
        project = self._get_object()
        # self._touch_object(project)

        return {
            'obj': project,
        }


@view_defaults(route_name='admin:projects:new',
               renderer='admin/projects_new.html', permission='admin')
@lift()
class ProjectCreateView(NodeCreateView):
    cls = model.Project
    obj_route_name = 'admin:project'
