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

from .. import model


old_url = 'mysql+pymysql://crowdsupply:quux@localhost/crowdsupply?charset=utf8'


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def migrate_aliases(old_node, new_node):
    canonical_path = None
    for alias in old_node.aliases:
        print("  path: %s" % alias.path)
        if alias.canonical:
            canonical_path = alias.path
        new_node.update_path(alias.path)
    if canonical_path:
        new_node.update_path(canonical_path)


def migrate(user_map):
    q = scrappy_meta.Session.query(cs_model.Creator)
    for old_creator in q:
        print("creator %s" % old_creator.name)
        creator = model.Creator(
            name=old_creator.name,
            teaser=old_creator.teaser,
            body=old_creator.body.text,
            published=old_creator.published,
            listed=old_creator.listed,
        )
        model.Session.add(creator)
        migrate_aliases(old_creator, creator)

        for old_project in old_creator.projects:
            print("  project %s" % old_project.name)
            project = model.Project(
                creator=creator,
                name=old_project.name,
                teaser=old_project.teaser,
                body=old_project.body.text,
                published=old_project.published,
                listed=old_project.listed,
            )
            model.Session.add(project)
            migrate_aliases(old_project, project)


def migrate_users():
    user_map = {}
    return user_map


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
    scrappy_model.init_model(old_engine, site_map={})

    with transaction.manager:
        user_map = migrate_users()
        migrate(user_map)
