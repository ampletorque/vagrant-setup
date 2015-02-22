from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os.path
import sys

import transaction

from sqlalchemy import create_engine, engine_from_config
from pyramid.paster import get_appsettings, setup_logging

try:
    from scrappy import model as scrappy_model
except ImportError:
    scrappy_model = None

from .. import model

from .migration import images, users, content, orders


old_url = 'mysql+pymysql://crowdsupply:quux@localhost/crowdsupply?charset=utf8'


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


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

        image_map = images.migrate_images(settings)
        user_map = users.migrate_users(settings, image_map)

        provider_type_map = content.migrate_provider_types(settings, user_map,
                                                           image_map)
        content.migrate_providers(settings, user_map, image_map,
                                  provider_type_map)
        content.migrate_articles(settings, user_map, image_map)
        tag_map = content.migrate_tags(settings, user_map)
        creator_map = content.migrate_creators(settings, user_map, image_map)
        project_map, product_map, option_value_map, batch_map = \
            content.migrate_projects(settings, user_map, creator_map,
                                     tag_map, image_map)
        content.migrate_related_projects(settings, project_map)

        orders.migrate_payment_gateways()
        orders.migrate_payment_methods()
        orders.migrate_orders(settings, user_map, product_map,
                              option_value_map, batch_map)

        scott_user = model.Session.query(model.User).\
            filter_by(email='scott.torborg@crowdsupply.com').\
            one()
        scott_user.url_path = 'storborg'
        scott_user.location = 'Portland, OR'
        scott_user.twitter_username = 'storborg'
