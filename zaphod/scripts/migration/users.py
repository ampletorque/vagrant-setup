from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

try:
    from scrappy import model as scrappy_model
    from crowdsupply import model as cs_model
    from scrappy.model import meta as scrappy_meta
except ImportError:
    scrappy_meta = scrappy_model = cs_model = None

from ... import model, helpers as h

from . import utils


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
        utils.migrate_image_associations(settings, image_map, old_user, user)
        user_map[old_user] = user
        model.Session.flush()

    # Take a second pass through to set the updated by / created by.
    for old_user in scrappy_meta.Session.query(scrappy_model.Account).\
            order_by(scrappy_model.Account.id.desc()):
        new_user = user_map[old_user]
        new_user.updated_by = user_map[old_user.updated_by]
        new_user.created_by = user_map[old_user.created_by]
        utils.migrate_comments(old_user, new_user)

    # Set image updated by / created by.
    for old_image, new_image in image_map.items():
        new_image.updated_by = user_map[old_image.updated_by]
        new_image.created_by = user_map[old_image.created_by]

    return user_map
