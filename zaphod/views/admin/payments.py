from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config
from formencode import Schema, validators

from pyramid_uniform import Form, FormRenderer

from ... import model, payment, custom_validators, helpers as h


class CaptureForm(Schema):
    allow_extra_fields = False
    amount = custom_validators.Money(not_empty=True, min=0)


class RefundForm(Schema):
    allow_extra_fields = False
    amount = custom_validators.Money(not_empty=True, min=0)


class MarkChargebackForm(Schema):
    allow_extra_fields = False
    reason = validators.String()


class PaymentView(object):
    def __init__(self, request):
        self.request = request

    def _get_object(self):
        request = self.request
        pp = model.CreditCardPayment.get(request.matchdict['id'])
        if not pp:
            raise HTTPNotFound
        return pp

    def _touch_object(self, obj):
        BaseEditView._touch_object(self, obj)
        obj.order.update_payment_status()

    def _get_profile(self, pp):
        method = pp.method
        registry = self.request.registry
        iface = payment.get_payment_interface(registry, method.gateway.id)
        return iface.get_profile(method.reference)

    @view_config(route_name='admin:payment:void', permission='admin')
    def void(self):
        request = self.request
        pp = self._get_object()
        assert pp.can_be_voided()
        profile = self._get_profile(pp)
        profile.void(pp.transaction_id)
        pp.mark_as_void(request.user)
        self._touch_object(pp)

        request.flash("Voided payment %s." % pp.transaction_id, 'success')
        return HTTPFound(location=request.route_url('admin:order',
                                                    id=pp.order_id))

    @view_config(route_name='admin:payment:capture', permission='admin',
                 renderer='admin/payment_capture.html')
    def capture(self):
        request = self.request
        pp = self._get_object()
        assert pp.can_be_captured()

        form = Form(request, CaptureForm)
        if form.validate():
            amount = form.data['amount']

            profile = self._get_profile(pp)
            profile.prior_auth_capture(amount=amount,
                                       transaction_id=pp.transaction_id)

            pp.mark_as_captured(request.user, amount)
            self._touch_object(pp)
            request.flash("Captured %s for %s." % (pp.transaction_id,
                                                   h.currency(amount)),
                          'success')
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=pp.order_id))

        return {
            'payment': pp,
            'renderer': FormRenderer(form),
        }

    @view_config(route_name='admin:payment:refund', permission='admin',
                 renderer='admin/payment_refund.html')
    def refund(self):
        request = self.request
        pp = self._get_object()
        assert pp.refundable_amount > 0

        form = Form(request, RefundForm)
        if form.validate():
            amount = form.data['amount']
            assert amount <= pp.refundable_amount, \
                "trying to refund %r, which is more than allowed %r" % (
                    amount, pp.refundable_amount)

            profile = self._get_profile(pp)
            profile.refund(amount=amount,
                           transaction_id=pp.transaction_id)
            refund = model.CreditCardRefund(
                order=pp.order,
                created_by=request.user,
                credit_card_payment=pp,
                refund_amount=-amount,
            )
            model.Session.add(refund)
            self._touch_object(pp)
            refund.mark_as_processed(request.user, -amount)
            request.flash("Refunded %s for %s." % (pp.transaction_id,
                                                   h.currency(amount)),
                          'success')
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=pp.order_id))

        return {
            'payment': pp,
            'renderer': FormRenderer(form),
        }

    @view_config(route_name='admin:payment:mark-chargeback',
                 permission='admin',
                 renderer='admin/payment_mark_chargeback.html')
    def mark_chargeback(self):
        request = self.request
        pp = self._get_object()

        form = Form(request, MarkChargebackForm)
        if form.validate():
            pp.mark_as_chargeback(request.user)
            self._touch_object(pp)
            request.flash("Marked payment %s as a chargeback." %
                          pp.transaction_id, 'success')
            return HTTPFound(location=request.route_url('admin:order',
                                                        id=pp.order_id))

        return {
            'payment': pp,
            'renderer': FormRenderer(form),
        }

    @view_config(route_name='admin:payment:mark-chargeback-lost',
                 permission='admin')
    def mark_chargeback_lost(self):
        request = self.request
        pp = self._get_object()
        pp.chargeback_state = 'lost'
        self._touch_object(pp)
        request.flash("Marked chargeback as resolved in customer's favor.",
                      'success')
        return HTTPFound(location=request.route_url('admin:order',
                                                    id=pp.order_id))

    @view_config(route_name='admin:payment:mark-chargeback-won',
                 permission='admin')
    def mark_chargeback_won(self):
        request = self.request
        pp = self._get_object()
        pp.chargeback_state = 'won'
        self._touch_object(pp)
        request.flash("Marked chargeback as resolved in merchant's favor.",
                      'success')
        return HTTPFound(location=request.route_url('admin:order',
                                                    id=pp.order_id))

    @view_config(route_name='admin:payment:mark-expired',
                 permission='admin')
    def mark_expired(self):
        request = self.request
        pp = self._get_object()
        pp.expired = True
        self._touch_object(pp)
        request.flash("Marked payment %s as expired." % pp.transaction_id,
                      'success')
        return HTTPFound(location=request.route_url('admin:order',
                                                    id=pp.order_id))
