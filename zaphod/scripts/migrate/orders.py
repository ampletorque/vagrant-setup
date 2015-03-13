from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from decimal import Decimal

try:
    from scrappy import model as scrappy_model
    from crowdsupply import model as cs_model
    from scrappy.model import meta as scrappy_meta
except ImportError:
    scrappy_meta = scrappy_model = cs_model = None

from ... import model

from . import utils


def migrate_payment_gateways():
    for old_gateway in \
            scrappy_meta.Session.query(scrappy_model.PaymentGateway):
        print("  gateway %s" % old_gateway.comment)
        gateway = model.PaymentGateway(
            id=old_gateway.id,
            dev=old_gateway.dev,
            enabled=old_gateway.enabled,
            comment=old_gateway.comment,
            interface=old_gateway.interface,
            credentials=old_gateway.credentials,
            parent_id=old_gateway.parent_id,
        )
        model.Session.add(gateway)


def migrate_payment_methods():
    for old_method in scrappy_meta.Session.query(scrappy_model.PaymentMethod):
        print("  method %s" % old_method.id)
        method = model.PaymentMethod(
            id=old_method.id,
            user_id=old_method.account_id,
            payment_gateway_id=old_method.payment_gateway_id,
            save=old_method.save,
            reference=old_method.reference,
            billing=utils.convert_address(old_method.billing),
        )
        model.Session.add(method)


def get_bundled_surcharge(item):
    pl = item.product
    if pl.international_surcharge_bundled is None:
        return pl.international_surcharge
    else:
        return pl.international_surcharge_bundled


def item_shipping_prices(old_order):
    old_shipping_price = old_order.shipping_price
    if not old_shipping_price:
        return
    # assert old_order.shipping.country != 'us'
    projects_seen = set()
    item_prices = []
    for ci in old_order.cart.items:
        project = ci.product.project
        if project in projects_seen:
            item_prices.append([ci, get_bundled_surcharge(ci)])
        else:
            item_prices.append([ci, ci.product.international_surcharge])
            projects_seen.add(project)
    item_price_total = sum(fee for ci, fee in item_prices)
    diff = old_shipping_price - item_price_total
    if diff > 0:
        item_prices[-1][1] += diff
    return dict(item_prices)


def migrate_payment(payment_map, old_payment):
    if isinstance(old_payment, scrappy_model.CreditCardRefund):
        return model.CreditCardRefund(
            credit_card_payment=payment_map[old_payment.credit_card_payment],
            processed_time=old_payment.processed_time,
            processed_by_id=old_payment.processed_by_id,
            transaction_error_time=old_payment.transaction_error_time,
            transaction_error=old_payment.transaction_error,
            refund_amount=old_payment.refund_amount,
            created_by_id=old_payment.created_by_id,
            amount=old_payment.amount,
            created_time=old_payment.created_time,
            voided_time=old_payment.voided_time,
            voided_by_id=old_payment.voided_by_id,
            pending_action_time=old_payment.pending_action_time,
            pending_action_by_id=old_payment.pending_action_by_id,
            pending_action=old_payment.pending_action,
            comments=old_payment.comments,
        )
    elif isinstance(old_payment, scrappy_model.CheckRefund):
        return model.CheckRefund(
            reference=old_payment.reference,
            refund_amount=old_payment.refund_amount,
            created_by_id=old_payment.created_by_id,
            amount=old_payment.amount,
            created_time=old_payment.created_time,
            voided_time=old_payment.voided_time,
            voided_by_id=old_payment.voided_by_id,
            pending_action_time=old_payment.pending_action_time,
            pending_action_by_id=old_payment.pending_action_by_id,
            pending_action=old_payment.pending_action,
            comments=old_payment.comments,
        )
    elif isinstance(old_payment, scrappy_model.CashRefund):
        return model.CashRefund(
            refund_amount=old_payment.refund_amount,
            created_by_id=old_payment.created_by_id,
            amount=old_payment.amount,
            created_time=old_payment.created_time,
            voided_time=old_payment.voided_time,
            voided_by_id=old_payment.voided_by_id,
            pending_action_time=old_payment.pending_action_time,
            pending_action_by_id=old_payment.pending_action_by_id,
            pending_action=old_payment.pending_action,
            comments=old_payment.comments,
        )
    elif isinstance(old_payment, scrappy_model.CreditCardPayment):
        fee = (old_payment.amount * Decimal('0.029')) + Decimal('0.30')
        return model.CreditCardPayment(
            payment_method_id=old_payment.payment_method_id,
            transaction_id=old_payment.transaction_id,
            invoice_number=old_payment.invoice_number,
            authorized_amount=old_payment.authorized_amount,
            avs_result=old_payment.avs_result,
            ccv_result=old_payment.ccv_result,
            captured_time=old_payment.captured_time,
            captured_state=old_payment.captured_state,
            transaction_error_time=old_payment.transaction_error_time,
            transaction_error=old_payment.transaction_error,
            chargeback_time=old_payment.chargeback_time,
            chargeback_by_id=old_payment.chargeback_by_id,
            card_type_code=old_payment.card_type_code,
            expired=old_payment.expired,
            chargeback_state=old_payment.chargeback_state,
            created_by_id=old_payment.created_by_id,
            amount=old_payment.amount,
            transaction_fee=fee,
            created_time=old_payment.created_time,
            voided_time=old_payment.voided_time,
            voided_by_id=old_payment.voided_by_id,
            pending_action_time=old_payment.pending_action_time,
            pending_action_by_id=old_payment.pending_action_by_id,
            pending_action=old_payment.pending_action,
            comments=old_payment.comments,
        )
    elif isinstance(old_payment, scrappy_model.CheckPayment):
        return model.CheckPayment(
            reference=old_payment.reference,
            check_date=old_payment.check_date,
            bounced_time=old_payment.bounced_time,
            bounced_by_id=old_payment.bounced_by_id,
            created_by_id=old_payment.created_by_id,
            amount=old_payment.amount,
            created_time=old_payment.created_time,
            voided_time=old_payment.voided_time,
            voided_by_id=old_payment.voided_by_id,
            pending_action_time=old_payment.pending_action_time,
            pending_action_by_id=old_payment.pending_action_by_id,
            pending_action=old_payment.pending_action,
            comments=old_payment.comments,
        )
    elif isinstance(old_payment, scrappy_model.CashPayment):
        return model.CashPayment(
            created_by_id=old_payment.created_by_id,
            amount=old_payment.amount,
            created_time=old_payment.created_time,
            voided_time=old_payment.voided_time,
            voided_by_id=old_payment.voided_by_id,
            pending_action_time=old_payment.pending_action_time,
            pending_action_by_id=old_payment.pending_action_by_id,
            pending_action=old_payment.pending_action,
            comments=old_payment.comments,
        )


def status_for_item(utcnow, product_map, old_order, old_ci):
    if old_ci.shipped_date:
        return 'shipped'
    if old_order.status in ('canc', 'frau'):
        return 'cancelled'
    product = product_map[old_ci.product]
    project = product.project
    if not project.successful:
        if project.end_time < utcnow:
            return 'failed'
        else:
            return 'unfunded'

    if hasattr(old_ci, 'payment_status'):
        if old_ci.payment_status == 'failed':
            return 'payment failed'
        if old_ci.payment_status == 'dead':
            return 'abandoned'
        if old_ci.payment_status == 'paid':
            return 'waiting'

    if project.successful:
        return 'payment pending'

    if old_ci.status == 'bpak':
        return 'being packed'

    return 'init'


def migrate_orders(settings, product_map, option_value_map,
                   batch_map):
    utcnow = model.utcnow()
    for old_order in scrappy_meta.Session.query(scrappy_model.Order):
        print("  order %s" % old_order.id)
        order = model.Order(
            id=old_order.id,
            user_id=old_order.account_id,
            created_by_id=old_order.created_by_id,
            created_time=old_order.created_time,
            updated_by_id=old_order.updated_by_id,
            updated_time=old_order.updated_time,
            shipping=utils.convert_address(old_order.shipping),
            customer_comments=old_order.customer_comments,
        )
        model.Session.add(order)
        utils.migrate_comments(old_order, order)
        cart = model.Cart(order=order)
        model.Session.add(cart)
        shipping_prices = item_shipping_prices(old_order)
        item_map = {}
        for old_ci in old_order.cart.items:
            ship_date = None
            old_batch = getattr(old_ci, 'batch', None)
            if old_batch:
                ship_date = old_ci.batch.delivery_date
            product = product_map[old_ci.product]
            sku = model.sku_for_option_value_ids_sloppy(
                product,
                set(option_value_map[old_ov].id
                    for old_ov in old_ci.option_values))
            ci = model.CartItem(
                id=old_ci.id,
                cart=order.cart,
                product=product,
                price_each=old_ci.price_each,
                qty_desired=old_ci.qty_desired,
                stage=['P', 'E', 'C'].index(old_ci.discriminator),
                status=status_for_item(utcnow, product_map, old_order, old_ci),
                sku=sku,
                shipping_price=(shipping_prices[old_ci]
                                if shipping_prices else 0),
                shipped_date=old_ci.shipped_date,
                expected_ship_date=ship_date,
            )
            item_map[old_ci] = ci
            if old_batch:
                ci.batch = batch_map[old_batch]
            order.cart.items.append(ci)
            model.Session.flush()
        for old_shipment in old_order.shipments:
            shipment = model.Shipment(
                order=order,
                tracking_number=','.join(list(old_shipment.tracking_num)),
                cost=old_shipment.cost,
                shipped_by_creator=False,
            )
            for old_ci in old_shipment.items:
                shipment.items.append(item_map[old_ci])
            model.Session.add(shipment)
        payment_map = {}
        for old_payment in old_order.payments:
            payment = migrate_payment(payment_map, old_payment)
            payment_map[old_payment] = payment
            order.payments.append(payment)
        model.Session.flush()
        order.update_status()
