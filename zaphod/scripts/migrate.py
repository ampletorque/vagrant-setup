from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os.path
import sys

import transaction

from sqlalchemy import create_engine, engine_from_config
from pyramid.paster import get_appsettings, setup_logging

try:
    from scrappy import model as scrappy_model
    from crowdsupply import model as cs_model
    from scrappy.model import meta as scrappy_meta
except ImportError:
    scrappy_meta = scrappy_model = cs_model = None

from .. import model, helpers as h


old_url = 'mysql+pymysql://crowdsupply:quux@localhost/crowdsupply?charset=utf8'


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def migrate_aliases(settings, old_node, new_node):
    canonical_path = None
    for alias in old_node.aliases:
        print("  path: %r" % alias.path)
        if alias.canonical:
            canonical_path = alias.path
        new_node.update_path(alias.path)
    if canonical_path:
        new_node.update_path(canonical_path)


def migrate_comments(old_obj, new_obj):
    for old_comment in old_obj.comments:
        new_obj.comments.append(new_obj.Comment(
            created_time=old_comment.created_time,
            created_by_id=old_comment.created_by_id,
            body=old_comment.body,
        ))


def migrate_images(settings):
    image_map = {}
    for old_im in scrappy_meta.Session.query(scrappy_model.ImageMeta):
        print("image %s" % old_im.name)
        new_im = model.ImageMeta(
            id=old_im.id,
            name=old_im.name,
            alt=old_im.alt,
            title=old_im.title,
            original_ext=old_im.original_ext,
            width=old_im.width,
            height=old_im.height,
            created_time=old_im.created_time,
            updated_time=old_im.updated_time,
        )
        model.Session.add(new_im)
        # XXX Copy the actual image path!
        # XXX Copy image type?
        image_map[old_im] = new_im
    return image_map


def migrate_image_associations(settings, image_map, old_obj, new_obj):
    for old_im in old_obj.image_metas:
        print("  image assoc %s" % old_im.name)
        new_obj.image_metas.append(image_map[old_im])


def migrate_articles(settings, user_map, image_map):
    for old_article in scrappy_meta.Session.query(scrappy_model.Article):
        print("article %s" % old_article.name)
        article = model.Article(
            id=old_article.id,
            name=old_article.name,
            teaser=old_article.teaser,
            body=old_article.body.text,
            published=old_article.published,
            listed=old_article.listed,
            show_heading=old_article.show_heading,
            show_article_list=old_article.show_article_list,
            category=old_article.category,
            created_by=user_map[old_article.created_by],
            created_time=old_article.created_time,
            updated_by=user_map[old_article.updated_by],
            updated_time=old_article.updated_time,
        )
        model.Session.add(article)
        migrate_aliases(settings, old_article, article)
        migrate_image_associations(settings, image_map, old_article, article)
        model.Session.flush()


def migrate_tags(settings, user_map):
    tag_map = {}
    for old_tag in scrappy_meta.Session.query(cs_model.Tag):
        print("tag %s" % old_tag.name)
        tag = model.Tag(
            id=old_tag.id,
            name=old_tag.name,
            teaser=old_tag.name,
            body=old_tag.body.text,
            published=old_tag.published,
            listed=old_tag.listed,
            created_by=user_map[old_tag.created_by],
            created_time=old_tag.created_time,
            updated_by=user_map[old_tag.updated_by],
            updated_time=old_tag.updated_time,
        )
        model.Session.add(tag)
        migrate_aliases(settings, old_tag, tag)
        tag_map[old_tag] = tag
        model.Session.flush()
    return tag_map


def migrate_creators(settings, user_map, image_map):
    creator_map = {}
    for old_creator in scrappy_meta.Session.query(cs_model.Creator):
        print("creator %s" % old_creator.name)
        creator = model.Creator(
            id=old_creator.id,
            name=old_creator.name,
            teaser=old_creator.teaser,
            location=old_creator.location,
            home_url=old_creator.home_url,
            body=old_creator.body.text,
            published=old_creator.published,
            listed=old_creator.listed,
            created_by=user_map[old_creator.created_by],
            created_time=old_creator.created_time,
            updated_by=user_map[old_creator.updated_by],
            updated_time=old_creator.updated_time,
        )
        model.Session.add(creator)
        migrate_aliases(settings, old_creator, creator)
        migrate_image_associations(settings, image_map, old_creator, creator)
        creator_map[old_creator] = creator
        model.Session.flush()
    return creator_map


def launched_on_crowd_supply(old_project):
    whitelist_ids = [
        610,  # Essential System
        365,  # PF Solution Insole
    ]
    if old_project.id in whitelist_ids:
        return True
    q = scrappy_meta.Session.query(cs_model.PledgeLevel).\
        join(cs_model.PledgeLevel.cart_items.of_type(
            cs_model.PledgeCartItem)).\
        filter(cs_model.PledgeLevel.project_id == old_project.id)
    return bool(q.first())


def migrate_projects(settings, user_map, creator_map, tag_map, image_map):
    project_map = {}
    product_map = {}
    option_value_map = {}
    batch_map = {}
    for old_project in scrappy_meta.Session.query(cs_model.Project):
        print("  project %s" % old_project.name)
        project = model.Project(
            id=old_project.id,
            creator=creator_map[old_project.creator],
            name=old_project.name,

            prelaunch_vimeo_id=None,
            prelaunch_teaser=old_project.teaser,
            prelaunch_body=u'',

            crowdfunding_vimeo_id=old_project.vimeo_id,
            crowdfunding_teaser=old_project.teaser,
            crowdfunding_body=old_project.body.text,

            available_vimeo_id=old_project.vimeo_id,
            available_teaser=old_project.teaser,
            available_body=old_project.body.text,

            published=old_project.published,
            listed=old_project.listed,
            gravity=old_project.gravity,
            target=old_project.target,
            start_time=old_project.start_time,
            end_time=old_project.end_time,
            suspended_time=old_project.suspended_time,
            created_by=user_map[old_project.created_by],
            created_time=old_project.created_time,
            updated_by=user_map[old_project.updated_by],
            updated_time=old_project.updated_time,

            accepts_preorders=(old_project.stage in (2, 3)),
            include_in_launch_stats=launched_on_crowd_supply(old_project),
            pledged_elsewhere_amount=old_project.pledged_elsewhere_amount,
            pledged_elsewhere_count=old_project.pledged_elsewhere_count,

            direct_transactions=old_project.direct_transactions,
            crowdfunding_fee_percent=old_project.fee_percent,
            successful=old_project.pledged_amount > old_project.target,
        )
        model.Session.add(project)
        migrate_aliases(settings, old_project, project)
        migrate_image_associations(settings, image_map, old_project, project)
        project_map[old_project] = project
        for old_tag in old_project.tags:
            print("    assoc tag %s" % old_tag.name)
            project.tags.add(tag_map[old_tag])
        for old_update in old_project.updates:
            print("    update %s" % old_update.name)
            update = model.ProjectUpdate(
                id=old_update.id,
                project=project,
                name=old_update.name,
                teaser=old_update.teaser,
                body=old_update.body.text,
                published=old_update.published,
                listed=old_update.listed,
                created_by=user_map[old_update.created_by],
                created_time=old_update.created_time,
                updated_by=user_map[old_update.updated_by],
                updated_time=old_update.updated_time,
            )
            model.Session.add(update)
            migrate_aliases(settings, old_update, update)
            migrate_image_associations(settings, image_map, old_update, update)
        for old_pledge_level in old_project.levels:
            print("    pledge level %s" % old_pledge_level.name)
            intl_available = old_pledge_level.international_available
            intl_surcharge = old_pledge_level.international_surcharge
            product = model.Product(
                id=old_pledge_level.id,
                project=project,
                name=old_pledge_level.name,
                international_available=intl_available,
                international_surcharge=intl_surcharge,
                non_physical=old_pledge_level.non_physical,
                gravity=old_pledge_level.gravity,
                published=old_pledge_level.published,
                price=old_pledge_level.price,
                accepts_preorders=(old_project.stage in (2, 3)),
            )
            model.Session.add(product)
            migrate_image_associations(settings, image_map,
                                       old_pledge_level, product)
            product_map[old_pledge_level] = product
            for old_option in old_pledge_level.all_options:
                print("      option %s" % old_option.name)
                option = model.Option(
                    name=old_option.name,
                    gravity=old_option.gravity,
                    published=old_option.enabled,
                )
                product.options.append(option)
                for old_value in old_option.all_values:
                    print("        value %s" % old_value.description)
                    value = model.OptionValue(
                        description=old_value.description,
                        gravity=old_value.gravity,
                        published=old_value.enabled,
                    )
                    option.values.append(value)
                    option_value_map[old_value] = value
            for old_batch in old_pledge_level.batches:
                print("      batch %s" % old_batch.id)
                batch = model.Batch(
                    qty=old_batch.qty,
                    delivery_date=old_batch.delivery_date
                )
                batch_map[old_batch] = batch
                product.batches.append(batch)
        for old_owner in old_project.ownerships:
            print("    ownership %s" % old_owner.account.email)
            new_owner = model.ProjectOwner(
                project=project,
                user=user_map[old_owner.account],
                title=old_owner.title,
                can_change_content=old_owner.can_change_content,
                can_post_updates=old_owner.can_post_updates,
                can_receive_questions=old_owner.can_receive_questions,
                can_manage_payments=old_owner.can_manage_stripe,
                can_manage_owners=old_owner.can_manage_owners,
                show_on_campaign=old_owner.show_on_campaign,
            )
            model.Session.add(new_owner)
        model.Session.flush()
    return project_map, product_map, option_value_map, batch_map


def lookup_location(old_user):
    q = scrappy_meta.Session.query(scrappy_model.Order).\
        filter_by(account=old_user).\
        order_by(scrappy_model.Order.id.desc())
    order = q.first()
    if order and not order.cart.non_physical:
        if order.shipping.country == 'us':
            return '%s, %s' % (order.shipping.city,
                               order.shipping.state)
        else:
            return '%s, %s' % (order.shipping.city,
                               order.shipping.country_name)
    return ''


def migrate_users(settings, image_map):
    user_map = {}
    user_emails = set()
    for old_user in scrappy_meta.Session.query(scrappy_model.Account).\
            order_by(scrappy_model.Account.id.desc()):
        print("  user %s" % old_user.email)

        if old_user.id == 1:
            user_map[old_user] = model.User.get(1)
            continue

        if old_user.email in user_emails:
            email = old_user.email + '.' + str(old_user.id)
        else:
            email = old_user.email

        user_emails.add(old_user.email)
        is_admin = old_user.has_permission('admin')

        user = model.User(
            id=old_user.id,
            name=old_user.name,
            email=email,
            hashed_password=old_user.hashed_password,
            enabled=old_user.enabled,
            created_time=old_user.created_time,
            updated_time=old_user.updated_time,
            admin=is_admin,
            show_admin_bars=is_admin,
            show_name=h.abbreviate_name(old_user.name),
            show_location=lookup_location(old_user),
        )
        model.Session.add(user)
        migrate_image_associations(settings, image_map, old_user, user)
        user_map[old_user] = user
        model.Session.flush()

    # Take a second pass through to set the updated by / created by.
    for old_user in scrappy_meta.Session.query(scrappy_model.Account).\
            order_by(scrappy_model.Account.id.desc()):
        new_user = user_map[old_user]
        new_user.updated_by = user_map[old_user.updated_by]
        new_user.created_by = user_map[old_user.created_by]
        migrate_comments(old_user, new_user)

    # Set image updated by / created by.
    for old_image, new_image in image_map.items():
        new_image.updated_by = user_map[old_image.updated_by]
        new_image.created_by = user_map[old_image.created_by]

    return user_map


def migrate_provider_types(settings, user_map, image_map):
    provider_type_map = {}
    for old_provider_type in \
            scrappy_meta.Session.query(cs_model.ProviderType):
        print("  provider type %s" % old_provider_type.name)
        provider_type = model.ProviderType(
            id=old_provider_type.id,
            name=old_provider_type.name,
            teaser=old_provider_type.teaser,
            body=old_provider_type.body.text,
            published=old_provider_type.published,
            listed=old_provider_type.listed,
            created_by=user_map[old_provider_type.created_by],
            created_time=old_provider_type.created_time,
            updated_by=user_map[old_provider_type.updated_by],
            updated_time=old_provider_type.updated_time,
        )
        model.Session.add(provider_type)
        migrate_aliases(settings, old_provider_type, provider_type)
        migrate_image_associations(settings, image_map,
                                   old_provider_type, provider_type)
        provider_type_map[old_provider_type] = provider_type
        model.Session.flush()
    return provider_type_map


def convert_address(old):
    return model.Address(first_name=old.first_name,
                         last_name=old.last_name,
                         company=old.company,
                         phone=old.phone,
                         address1=old.address1,
                         address2=old.address2,
                         city=old.city,
                         state=old.state,
                         postal_code=old.postal_code,
                         country_code=old.country)


def migrate_providers(settings, user_map, image_map, provider_type_map):
    for old_provider in scrappy_meta.Session.query(cs_model.Provider):
        print("  provider %s" % old_provider.name)
        provider = model.Provider(
            id=old_provider.id,
            name=old_provider.name,
            teaser=old_provider.teaser,
            body=old_provider.body.text,
            published=old_provider.published,
            listed=old_provider.listed,
            mailing=convert_address(old_provider.mailing),
            home_url=old_provider.home_url,
            created_by=user_map[old_provider.created_by],
            created_time=old_provider.created_time,
            updated_by=user_map[old_provider.updated_by],
            updated_time=old_provider.updated_time,
        )
        model.Session.add(provider)
        for old_type in old_provider.types:
            provider.types.add(provider_type_map[old_type])
        migrate_aliases(settings, old_provider, provider)
        migrate_image_associations(settings, image_map, old_provider, provider)
        model.Session.flush()


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
            billing=convert_address(old_method.billing),
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


def migrate_orders(settings, user_map, product_map, option_value_map,
                   batch_map):
    utcnow = model.utcnow()
    for old_order in scrappy_meta.Session.query(scrappy_model.Order):
        print("  order %s" % old_order.id)
        if old_order.account:
            user = user_map[old_order.account]
        else:
            user = None
        order = model.Order(
            id=old_order.id,
            user=user,
            created_by=user_map[old_order.created_by],
            created_time=old_order.created_time,
            updated_by=user_map[old_order.updated_by],
            updated_time=old_order.updated_time,
            shipping=convert_address(old_order.shipping),
            customer_comments=old_order.customer_comments,
        )
        model.Session.add(order)
        migrate_comments(old_order, order)
        cart = model.Cart(order=order)
        model.Session.add(cart)
        shipping_prices = item_shipping_prices(old_order)
        item_map = {}
        for old_ci in old_order.cart.items:
            delivery_date = None
            old_batch = getattr(old_ci, 'batch', None)
            if old_batch:
                delivery_date = old_ci.batch.delivery_date
            product = product_map[old_ci.product]
            sku = model.sku_for_option_value_ids_sloppy(
                product,
                set(option_value_map[old_ov].id
                    for old_ov in old_ci.option_values))
            ci = model.CartItem(
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
                expected_delivery_date=delivery_date,
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
                source=old_shipment.source,
                cost=old_shipment.cost,
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


def migrate_related_projects(settings, project_map):
    for old_project, new_project in project_map.items():
        new_project.related_projects[:] = [project_map[old_rel] for old_rel in
                                           old_project.related_projects]


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    engine = engine_from_config(settings, 'sqlalchemy.')
    model.Session.configure(bind=engine)
    model.Base.metadata.drop_all(engine)
    model.Base.metadata.create_all(engine)

    old_engine = create_engine(old_url)
    scrappy_model.init_model(old_engine, site_map={}, default_site_id=701)

    with transaction.manager:
        root_user = model.User(
            name=u'Root User',
            email='root@crowdsupply.com',
        )
        root_user.update_password('root')
        model.Session.add(root_user)
        model.Session.flush()

        image_map = migrate_images(settings)
        user_map = migrate_users(settings, image_map)

        provider_type_map = migrate_provider_types(settings, user_map,
                                                   image_map)
        migrate_providers(settings, user_map, image_map, provider_type_map)

        migrate_articles(settings, user_map, image_map)
        tag_map = migrate_tags(settings, user_map)
        creator_map = migrate_creators(settings, user_map, image_map)
        project_map, product_map, option_value_map, batch_map = \
            migrate_projects(settings, user_map, creator_map,
                             tag_map, image_map)
        migrate_related_projects(settings, project_map)

        migrate_payment_gateways()
        migrate_payment_methods()
        migrate_orders(settings, user_map, product_map, option_value_map,
                       batch_map)

        scott_user = model.Session.query(model.User).\
            filter_by(email='scott.torborg@crowdsupply.com').\
            one()
        scott_user.url_path = 'storborg'
        scott_user.location = 'Portland, OR'
        scott_user.twitter_username = 'storborg'
