from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os.path
import sys

import transaction

from sqlalchemy import MetaData, create_engine, engine_from_config
from pyramid.paster import get_appsettings, setup_logging

try:
    from scrappy import model as scrappy_model
except ImportError:
    scrappy_model = None

from ... import model

from . import images, users, content, orders, vendors, stock


old_url = 'mysql+pymysql://crowdsupply:quux@localhost/crowdsupply?charset=utf8'


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def drop_existing_tables(engine):
    "Drop all tables, including tables that aren't defined in metadata."
    temp_metadata = MetaData()
    temp_metadata.reflect(bind=engine)
    for table in reversed(temp_metadata.sorted_tables):
        table.drop(bind=engine)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    engine = engine_from_config(settings, 'sqlalchemy.')
    drop_existing_tables(engine)

    model.Session.configure(bind=engine)
    model.Base.metadata.create_all(engine)

    old_engine = create_engine(old_url)
    scrappy_model.init_model(old_engine, site_map={}, default_site_id=701)

    with transaction.manager:
        root_user = model.User(
            name=u'Root User',
            email='root@crowdsupply.com',
        )
        root_user.update_password(None)
        model.Session.add(root_user)
        model.Session.flush()

        user_map = users.migrate_users(settings)
        images.migrate_images(settings)
        users.migrate_user_data(settings, user_map)

        content.migrate_providers(settings, user_map)
        content.migrate_articles(settings, user_map)
        tag_map = content.migrate_tags(settings, user_map)
        creator_map = content.migrate_creators(settings, user_map)
        project_map, product_map, option_value_map, batch_map = \
            content.migrate_projects(settings, creator_map,
                                     tag_map, user_map)

        orders.migrate_payment_gateways()
        orders.migrate_payment_methods(user_map)
        cart_item_map = orders.migrate_orders(settings, product_map,
                                              option_value_map, batch_map,
                                              user_map)

        vendors.migrate_vendors(settings, user_map)
        vendors.migrate_vendor_orders(settings, product_map, option_value_map,
                                      user_map)

        stock.migrate_inventory_adjustments()
        stock.migrate_items(cart_item_map)
        stock.update_stock_flags()

        scott_user = model.Session.query(model.User).\
            filter_by(email='scott.torborg@crowdsupply.com').\
            one()
        scott_user.url_path = 'storborg'
        scott_user.location = 'Portland, OR'
        scott_user.twitter_username = 'storborg'
