from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from decimal import Decimal

from pyramid.view import view_defaults, view_config
from venusian import lift
from sqlalchemy.sql import func, not_
from formencode import Schema, NestedVariables, ForEach, validators
from pyramid.httpexceptions import HTTPFound

from pyramid_uniform import Form, FormRenderer, crud_update
from pyramid_es import get_client

from ... import model, funds

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


class SuspendForm(Schema):
    allow_extra_fields = False
    reason = validators.UnicodeString()


class TransferCreateForm(Schema):
    allow_extra_fields = False
    amount = validators.Number(not_empty=True)
    fee = validators.Number(if_empty=0)
    method = validators.String(not_empty=True)
    reference = validators.UnicodeString()


@view_defaults(route_name='admin:projects', renderer='admin/projects.html',
               permission='admin')
@lift()
class ProjectListView(NodeListView):
    cls = model.Project

    @view_config(route_name='admin:projects:search', renderer='json', xhr=True)
    def search(self):
        request = self.request
        q = request.params.get('q')

        client = get_client(request)
        results = client.query(model.Project, q=q).limit(40).execute()

        return {
            'total': results.total,
            'projects': [
                {
                    'id': project._id,
                    'name': project.name,
                }
                for project in results
            ]
        }


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
        crowdfunding_fee_percent = validators.Number()
        preorder_fee_percent = validators.Number()

        homepage_url = validators.URL(max=255)
        open_source_url = validators.URL(max=255)

        tag_ids = ForEach(validators.Int)
        related_project_ids = ForEach(validators.Int)

    def _update_object(self, form, obj):
        obj.tags.clear()
        for tag_id in form.data.pop('tag_ids'):
            obj.tags.add(model.Tag.get(tag_id))

        obj.related_projects.clear()
        for project_id in form.data.pop('related_project_ids'):
            obj.related_projects.add(model.Project.get(project_id))

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
            limit(1).\
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

        # This hardcodes Stripe's pricing.
        def stripe_fees(count, amount):
            return (count * Decimal('0.30')) + (amount * Decimal('0.029'))

        include_statuses = ['waiting', 'shipped', 'in process', 'being packed']
        sales_q = model.Session.query(func.sum(model.CartItem.qty_desired *
                                               model.CartItem.price_each)).\
            join(model.CartItem.product).\
            filter(model.CartItem.status.in_(include_statuses)).\
            filter(model.Product.project == project)

        shipping_q = model.Session.query(
            func.sum(model.CartItem.shipping_price)).\
            join(model.CartItem.product).\
            filter(model.CartItem.status.in_(include_statuses)).\
            filter(model.Product.project == project)

        order_count_q = model.Session.query(
            func.count(model.Order.id.distinct())).\
            join(model.Order.cart).\
            join(model.Cart.items).\
            join(model.CartItem.product).\
            filter(model.CartItem.status.in_(include_statuses)).\
            filter(model.Product.project == project)

        item_count_q = model.Session.query(
            func.count(model.CartItem.id.distinct())).\
            join(model.CartItem.product).\
            filter(model.CartItem.status.in_(include_statuses)).\
            filter(model.Product.project == project)

        cf_item_count = item_count_q.\
            filter(model.CartItem.stage == model.CartItem.CROWDFUNDING).\
            scalar() or 0
        # sum of crowdfunding pledges
        cf_sales = sales_q.\
            filter(model.CartItem.stage == model.CartItem.CROWDFUNDING).\
            scalar() or 0
        # sum of crowdfunding pledge shipping collected
        cf_shipping = shipping_q.\
            filter(model.CartItem.stage == model.CartItem.CROWDFUNDING).\
            scalar() or 0
        # sum of crowdfunding payment fees
        cf_order_count = order_count_q.\
            filter(model.CartItem.stage == model.CartItem.CROWDFUNDING).\
            scalar() or 0
        # NOTE: This gets pretty rocky, since it isn't really possible to
        # attribute payments to a single project. So we just assume that each
        # order incurs a $0.30 transaction fee.

        cf_transaction_fees = stripe_fees(cf_order_count,
                                          cf_sales + cf_shipping)
        # sum of crowdfunding crowd supply fees
        cf_crowd_supply_fees = ((cf_sales + cf_shipping) *
                                (project.crowdfunding_fee_percent / 100))

        po_item_count = item_count_q.\
            filter(model.CartItem.stage == model.CartItem.PREORDER).\
            scalar() or 0
        # sum of pre-order commitments
        po_sales = sales_q.\
            filter(model.CartItem.stage == model.CartItem.PREORDER).\
            scalar() or 0
        # sum of pre-order shipping collected
        po_shipping = shipping_q.\
            filter(model.CartItem.stage == model.CartItem.PREORDER).\
            scalar() or 0
        # sum of pre-order payment fees
        po_order_count = order_count_q.\
            filter(model.CartItem.stage == model.CartItem.PREORDER).\
            scalar() or 0
        po_transaction_fees = stripe_fees(po_order_count,
                                          po_sales + po_shipping)

        # sum of pre-order crowd supply fees
        po_crowd_supply_fees = ((po_sales + po_shipping) *
                                (project.preorder_fee_percent / 100))

        # fulfillment fees incurred so far
        fulfillment_q = model.Session.query(
            func.sum(model.Product.fulfillment_fee)).\
            join(model.CartItem.product).\
            filter(model.CartItem.status == 'shipped').\
            filter(model.Product.project == project)
        incurred_fulfillment_fees = fulfillment_q.scalar() or 0

        # freight costs incurred so far
        shipment_cost_q = model.Session.query(func.sum(model.Shipment.cost)).\
            join(model.Shipment.items).\
            join(model.CartItem.product).\
            filter(model.Product.project == project)
        freight_cost = shipment_cost_q.scalar() or 0

        # total owed to project
        total_owed = ((cf_sales + po_sales) -
                      (cf_shipping + cf_transaction_fees +
                       cf_crowd_supply_fees + po_shipping + po_transaction_fees
                       + po_crowd_supply_fees + incurred_fulfillment_fees +
                       freight_cost))

        return {
            'obj': project,

            'cf_item_count': cf_item_count,
            'cf_sales': cf_sales,
            'cf_shipping': cf_shipping,
            'cf_order_count': cf_order_count,
            'cf_transaction_fees': cf_transaction_fees,
            'cf_crowd_supply_fees': cf_crowd_supply_fees,

            'po_item_count': po_item_count,
            'po_sales': po_sales,
            'po_shipping': po_shipping,
            'po_order_count': po_order_count,
            'po_transaction_fees': po_transaction_fees,
            'po_crowd_supply_fees': po_crowd_supply_fees,

            'incurred_fulfillment_fees': incurred_fulfillment_fees,
            'freight_cost': freight_cost,

            'total_owed': total_owed,
        }

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

    @view_config(route_name='admin:project:mark-successful',
                 request_method='POST')
    def mark_successful(self):
        request = self.request
        project = self._get_object()

        form = Form(request, Schema)
        if form.validate():
            self._touch_object(project)
            assert project.pledged_amount >= project.target
            project.successful = True

            q = model.Session.query(model.CartItem).\
                join(model.Order.cart).\
                join(model.Cart.items).\
                join(model.CartItem.product).\
                filter(model.Product.project == project).\
                filter(model.CartItem.status == 'unfunded')

            for item in q:
                item.status = 'payment pending'

            request.flash("Marked project as successful.", 'success')
            return HTTPFound(
                location=request.route_url('admin:project:capture-funds',
                                           id=project.id))

        return {
        }

    @view_config(route_name='admin:project:capture-funds',
                 renderer='admin/project_capture_funds.html')
    def capture_funds(self):
        request = self.request
        project = self._get_object()

        form = Form(request, Schema)
        if form.validate():
            self._touch_object(project)
            count = funds.capture_funds(request, project)
            request.flash("Processed %d orders." % count, 'success')
            return HTTPFound(location=request.current_route_url())
        else:
            pending_q = model.Session.query(model.Order).\
                join(model.Order.cart).\
                join(model.Cart.items).\
                join(model.CartItem.product).\
                filter(model.Product.project == project).\
                filter(model.CartItem.status == 'payment pending')
            pending_count = pending_q.count()

        return {
            'obj': project,
            'pending_count': pending_count,
        }

    @view_config(route_name='admin:project:suspend',
                 renderer='admin/project_suspend.html')
    def suspend(self):
        request = self.request
        project = self._get_object()
        form = Form(request, SuspendForm)
        if form.validate():
            self._touch_object(project)
            project.suspended_time = model.utcnow()
            comment_body = 'Project suspended. '
            if form.data['reason']:
                comment_body += 'Details: %s' % form.data['reason']
            else:
                comment_body += 'No details specified.'
            project.add_comment(request.user, comment_body)
            request.flash("Suspended project %d." % project.id, 'success')
            return HTTPFound(location=request.route_url('admin:project',
                                                        id=project.id))

        return {
            'obj': project,
            'renderer': FormRenderer(form),
        }

    @view_config(route_name='admin:project:transfers',
                 renderer='admin/project_transfers.html')
    def transfers(self):
        project = self._get_object()
        return {'obj': project}

    @view_config(route_name='admin:project:transfers:new',
                 renderer='admin/project_transfers_new.html')
    def create_transfer(self):
        request = self.request
        project = self._get_object()

        form = Form(request, schema=TransferCreateForm)
        if form.validate():
            transfer = model.ProjectTransfer(project=project)
            form.bind(transfer)
            model.Session.flush()
            request.flash("Project transfer created.", 'success')
            self._touch_object(project)
            return HTTPFound(location=request.route_url('admin:transfer',
                                                        id=transfer.id))

        methods_for_select = model.ProjectTransfer.available_methods

        return {
            'obj': project,
            'methods_for_select': methods_for_select,
            'renderer': FormRenderer(form),
        }


@view_defaults(route_name='admin:projects:new',
               renderer='admin/projects_new.html', permission='admin')
@lift()
class ProjectCreateView(NodeCreateView):
    cls = model.Project
    obj_route_name = 'admin:project'

    class CreateForm(NodeCreateForm):
        allow_extra_fields = False
        creator_id = validators.Int(not_empty=True)
